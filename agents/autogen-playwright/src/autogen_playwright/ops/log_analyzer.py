import sqlite3
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class LogAnalyzer:
    """Analyzer for autogen runtime logs stored in SQLite database"""
    
    def __init__(self, db_path: str = "runtime_logs/autogen_logs.db"):
        """
        Initialize log analyzer
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
    def get_log_data(self, table: str = "chat_completions") -> List[Dict]:
        """
        Retrieve raw log data from database
        Args:
            table: Table name to query (default: chat_completions)
        Returns:
            List of dictionaries containing log data
        """
        try:
            con = sqlite3.connect(self.db_path)
            query = f"SELECT * from {table}"
            cursor = con.execute(query)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            data = [dict(zip(column_names, row)) for row in rows]
            logger.info(f"Retrieved {len(data)} records from {table}")
            con.close()
            return data
        except sqlite3.OperationalError as e:
            logger.warning(f"Error reading from database: {str(e)}")
            return []
    
    def get_log_dataframe(self, table: str = "chat_completions") -> pd.DataFrame:
        """
        Get log data as a pandas DataFrame with parsed columns
        Args:
            table: Table name to query
        Returns:
            DataFrame with parsed request/response data and token counts
        """
        log_data = self.get_log_data(table)
        df = pd.DataFrame(log_data)
        
        if not df.empty:
            # Add required columns with defaults if missing
            if "response" not in df.columns:
                logger.warning("Response column missing from logs")
                df["response"] = "{}"
            if "request" not in df.columns:
                logger.warning("Request column missing from logs")
                df["request"] = "{}"
            if "time" not in df.columns:
                logger.warning("Time column missing from logs")
                df["time"] = pd.Timestamp.now()
                
            # Parse JSON columns and extract token counts
            token_counts = df.apply(
                lambda row: self._extract_token_counts(row["response"]), axis=1
            )
            df["prompt_tokens"] = token_counts.apply(lambda x: x[0])
            df["completion_tokens"] = token_counts.apply(lambda x: x[1])
            df["total_tokens"] = token_counts.apply(lambda x: x[2])
            
            # Extract content
            df["request_content"] = df.apply(
                lambda row: self._extract_request_content(row["request"]), axis=1
            )
            df["response_content"] = df.apply(
                lambda row: self._extract_response_content(row["response"]), axis=1
            )
            
            # Convert time column
            if "time" in df.columns:
                df["timestamp"] = pd.to_datetime(df["time"])
            
            logger.info(f"Processed {len(df)} rows with token and content extraction")
            
        return df
    
    def get_session_stats(self, session_id: Optional[str] = None) -> Dict:
        """
        Get token and cost statistics for a session or all sessions
        Args:
            session_id: Optional session ID to filter by
        Returns:
            Dictionary containing token and cost statistics
        """
        df = self.get_log_dataframe()
        
        if session_id and not df.empty and "session_id" in df.columns:
            df = df[df["session_id"] == session_id]
            logger.info(f"Analyzing session {session_id} with {len(df)} messages")
            
        # Calculate costs (using OpenAI's pricing for GPT-4)
        prompt_cost = (df["prompt_tokens"].sum() if not df.empty else 0) * 0.03 / 1000  # $0.03 per 1k tokens
        completion_cost = (df["completion_tokens"].sum() if not df.empty else 0) * 0.06 / 1000  # $0.06 per 1k tokens
            
        stats = {
            "prompt_tokens": df["prompt_tokens"].sum() if not df.empty else 0,
            "completion_tokens": df["completion_tokens"].sum() if not df.empty else 0,
            "total_tokens": df["total_tokens"].sum() if not df.empty else 0,
            "prompt_cost": round(prompt_cost, 4),
            "completion_cost": round(completion_cost, 4),
            "total_cost": round(prompt_cost + completion_cost, 4),
            "request_count": len(df),
            "average_tokens_per_request": round(df["total_tokens"].mean(), 2) if not df.empty else 0
        }
        
        if session_id:
            stats["session_id"] = session_id
            
        return stats
    
    def get_conversation_flow(self, session_id: str) -> pd.DataFrame:
        """
        Get the conversation flow for a specific session
        Args:
            session_id: Session ID to analyze
        Returns:
            DataFrame with conversation flow details
        """
        df = self.get_log_dataframe()
        
        # Return empty DataFrame with correct columns if no data
        if df.empty:
            logger.warning("No log data found")
            return pd.DataFrame(columns=["time", "request_content", "response_content", "prompt_tokens", "completion_tokens"])
            
        # Filter by session if column exists
        if "session_id" in df.columns:
            df = df[df["session_id"] == session_id]
            logger.info(f"Found {len(df)} messages for session {session_id}")
        else:
            logger.warning("Session ID column missing from logs")
            
        # Sort by time if available
        if "time" in df.columns:
            df = df.sort_values("time")
            
        # Select available columns
        columns = []
        for col in ["time", "request_content", "response_content", "prompt_tokens", "completion_tokens"]:
            if col in df.columns:
                columns.append(col)
            else:
                logger.warning(f"Column {col} missing from logs")
                
        return df[columns] if columns else df
    
    @staticmethod
    def _extract_token_counts(response_str: str) -> Tuple[int, int, int]:
        """Extract token counts from response JSON"""
        try:
            response = json.loads(response_str)
            usage = response["usage"]
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
            return prompt_tokens, completion_tokens, total_tokens
        except (json.JSONDecodeError, KeyError):
            return 0, 0, 0
            
    @staticmethod
    def _extract_request_content(request_str: str) -> str:
        """Extract request content from request JSON"""
        try:
            request = json.loads(request_str)
            messages = request.get("messages", [])
            
            # Skip system messages and get the actual user message
            user_messages = [msg for msg in messages if msg.get("role") != "system"]
            if user_messages:
                content = user_messages[-1]["content"]  # Get the last user message
                logger.debug(f"Request content (first 100 chars): {content[:100]}")
                return content
                
            # Fallback to first message if no user messages found
            if messages:
                content = f"[{messages[0]['role']}] {messages[0]['content']}"
                logger.debug(f"Fallback content (first 100 chars): {content[:100]}")
                return content
                
            return "No message content"
        except (json.JSONDecodeError, KeyError, IndexError):
            return ""
            
    @staticmethod
    def _extract_response_content(response_str: str) -> str:
        """Extract response content from response JSON"""
        try:
            response = json.loads(response_str)
            content = response["choices"][0]["message"]["content"]
            if content.strip():
                logger.debug(f"Response content (first 100 chars): {content[:100]}")
                return content
            return "Empty response"
        except (json.JSONDecodeError, KeyError, IndexError):
            return "" 