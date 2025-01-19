from typing import Dict, List, Optional, Tuple, Any
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver

from ..core.schemas.state import ReceiptParserMessagesState
from ..core.llm.base import BaseLLM

class ReceiptParserAgent:
    def __init__(
        self,
        llm: BaseLLM,
        confidence_threshold: float = 0.8
    ):
        self.llm = llm
        self.confidence_threshold = confidence_threshold
        self.tools = self._create_tools()
        self.tool_executor = ToolExecutor(self.tools)
        self.memory = MemorySaver()
        self.graph = self._create_graph()
    
    def _create_tools(self) -> List[Dict]:
        return [
            {
                "name": "extract_text_from_image",
                "description": "Extract text from an image using OCR",
                "func": self._extract_text_from_image,
            },
            {
                "name": "extract_text_from_pdf",
                "description": "Extract text from a PDF file",
                "func": self._extract_text_from_pdf,
            }
        ]
    
    async def _extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image using OCR."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    async def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        try:
            pages = convert_from_path(pdf_path)
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page)
            return text
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def _process_text(self, state: ReceiptParserMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process text through LLM following ReACT framework."""
        messages = [
            SystemMessage(content="""You are an expert receipt parser following the ReACT framework.
            For each item in the receipt:
            1. Thought: Analyze the item text and identify key components
            2. Action: Extract the following information:
               - Name
               - Category
               - Quantity
               - Unit
               - Price
            3. Observation: Validate extracted information
            4. Final Answer: Format as a JSON object
            
            Format the final output as a JSON list of items."""),
            HumanMessage(content=state.current_text)
        ]
        
        response = await self.llm.generate(
            prompt="".join([m.content for m in messages]),
            temperature=0.3
        )
        
        try:
            parsed = eval(response)
            state.extracted_items = parsed
            state.confidence_scores = {
                item["name"]: self._calculate_confidence(item)
                for item in parsed
            }
            state.status = "items_parsed"
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return {"messages": messages}
    
    def _calculate_confidence(self, item_data: Dict) -> float:
        """Calculate confidence score for parsed item."""
        score = 1.0
        required_fields = ["name", "category", "quantity", "unit", "price"]
        
        for field in required_fields:
            if field not in item_data or not item_data[field]:
                score *= 0.8
            elif isinstance(item_data[field], str) and len(item_data[field].strip()) < 2:
                score *= 0.9
        
        return score
    
    def _create_graph(self) -> Graph:
        """Create the receipt parser graph following ReACT framework."""
        workflow = StateGraph(ReceiptParserMessagesState)
        
        # Define nodes
        workflow.add_node("extract", self._extract_node)
        workflow.add_node("process", self._process_text)
        workflow.add_node("validate", self._validate_node)
        
        # Define edges
        workflow.add_edge("extract", "process")
        workflow.add_edge("process", "validate")
        
        # Add conditional edges for validation
        workflow.add_conditional_edges(
            "validate",
            self._needs_validation,
            {
                True: END,  # Requires human validation
                False: END  # Automatically proceed
            }
        )
        
        workflow.set_entry_point("extract")
        return workflow.compile(checkpointer=self.memory)
    
    async def _extract_node(self, state: ReceiptParserMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text from image/PDF."""
        try:
            image_path = config.get("image_path")
            if not image_path:
                raise ValueError("No image path provided")
            
            if image_path.endswith('.pdf'):
                text = await self.tool_executor.execute(
                    "extract_text_from_pdf",
                    {"pdf_path": image_path}
                )
            else:
                text = await self.tool_executor.execute(
                    "extract_text_from_image",
                    {"image_path": image_path}
                )
            
            state.current_text = text
            state.status = "text_extracted"
            
            return {
                "messages": [
                    SystemMessage(content="Text extracted successfully"),
                    HumanMessage(content=text)
                ]
            }
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
            return {
                "messages": [
                    SystemMessage(content=f"Error extracting text: {str(e)}")
                ]
            }
    
    async def _validate_node(self, state: ReceiptParserMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate parsed results."""
        if not state.extracted_items:
            state.requires_validation = True
            state.status = "needs_validation"
            return {
                "messages": [
                    SystemMessage(content="No items extracted, requires validation")
                ]
            }
        
        # Check confidence scores
        low_confidence_items = [
            item["name"] for item in state.extracted_items
            if state.confidence_scores.get(item["name"], 0) < self.confidence_threshold
        ]
        
        if low_confidence_items:
            state.requires_validation = True
            state.metadata["low_confidence_items"] = low_confidence_items
            state.status = "needs_validation"
            return {
                "messages": [
                    SystemMessage(content=f"Low confidence items found: {', '.join(low_confidence_items)}")
                ]
            }
        
        state.requires_validation = False
        state.status = "completed"
        return {
            "messages": [
                SystemMessage(content="All items validated successfully")
            ]
        }
    
    def _needs_validation(self, state: ReceiptParserMessagesState) -> bool:
        """Determine if human validation is needed."""
        return state.requires_validation
    
    async def process_receipt(self, image_path: str) -> Dict[str, Any]:
        """Process a receipt image/PDF and extract items."""
        config = {
            "image_path": image_path,
            "configurable": {
                "thread_id": datetime.now().isoformat()
            }
        }
        
        initial_state = ReceiptParserMessagesState(
            agent_id="receipt_parser",
            messages=[]
        )
        
        return await self.graph.astream_events(
            {"messages": initial_state.messages},
            config,
            version="v2"
        ) 