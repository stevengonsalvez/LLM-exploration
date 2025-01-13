from typing import Dict, Optional
from pathlib import Path
import logging
from .log_analyzer import LogAnalyzer

logger = logging.getLogger(__name__)

def print_session_summary(session_id: Optional[str] = None, db_path: Optional[str] = None) -> Dict:
    """
    Print a summary of token usage and costs for a session or all sessions
    Args:
        session_id: Optional session ID to analyze
        db_path: Optional path to SQLite database
    Returns:
        Dictionary containing the statistics
    """
    analyzer = LogAnalyzer(db_path) if db_path else LogAnalyzer()
    stats = analyzer.get_session_stats(session_id)
    
    if session_id:
        print(f"\nSession Summary (ID: {session_id})")
    else:
        print("\nOverall Summary (All Sessions)")
    print("-" * 50)
    print(f"Prompt Tokens: {stats['prompt_tokens']:,} (${stats['prompt_cost']:.4f})")
    print(f"Completion Tokens: {stats['completion_tokens']:,} (${stats['completion_cost']:.4f})")
    print(f"Total Tokens: {stats['total_tokens']:,} (${stats['total_cost']:.4f})")
    print(f"Number of Requests: {stats['request_count']}")
    print(f"Average Tokens per Request: {stats['average_tokens_per_request']:.1f}")
    
    return stats

def analyze_conversation(session_id: str, db_path: Optional[str] = None) -> None:
    """
    Analyze and print the conversation flow for a specific session
    Args:
        session_id: Session ID to analyze
        db_path: Optional path to SQLite database
    """
    analyzer = LogAnalyzer(db_path) if db_path else LogAnalyzer()
    flow = analyzer.get_conversation_flow(session_id)
    
    if flow.empty:
        logger.warning("No conversation data found for analysis")
        print("\nNo conversation data available for analysis")
        return
    
    print(f"\nConversation Flow Analysis (Session: {session_id})")
    print("-" * 50)
    
    message_count = 0
    for _, row in flow.iterrows():
        # Get available fields with defaults
        time_value = row.get("time", "N/A")
        request = row.get("request_content", "No request content")
        response = row.get("response_content", "No response content")
        prompt_tokens = row.get("prompt_tokens", 0)
        completion_tokens = row.get("completion_tokens", 0)
        
        # Skip empty responses
        if response == "Empty response" and completion_tokens <= 1:
            continue
            
        # Log full content at debug level
        logger.debug(f"Request content: {request}")
        logger.debug(f"Response content: {response}")
        
        message_count += 1
        print(f"\nMessage {message_count} at {time_value}")
        print(f"Token Usage - Input: {prompt_tokens}, Output: {completion_tokens}")
        print("-" * 30)

def get_db_path(workspace_root: Optional[str] = None) -> str:
    """
    Get the path to the SQLite database
    Args:
        workspace_root: Optional workspace root directory
    Returns:
        Path to the SQLite database
    """
    if workspace_root:
        return str(Path(workspace_root) / "runtime_logs" / "autogen_logs.db")
    return "runtime_logs/autogen_logs.db" 