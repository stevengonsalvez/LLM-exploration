from typing import Dict, List, Optional, Tuple, Any
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import re
from datetime import datetime
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver

from ..core.schemas.base import (
    Receipt, FoodItem, FoodCategory, ReceiptParserState
)
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
            },
            {
                "name": "parse_items",
                "description": "Parse items from receipt text",
                "func": self._parse_items,
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
    
    async def _parse_items(self, text: str) -> Tuple[List[FoodItem], Dict[str, float]]:
        """Parse items from receipt text using LLM."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert receipt parser following the ReACT framework.
            For each item in the receipt:
            1. Thought: Analyze the item text and identify key components
            2. Action: Extract the following information:
               - Name
               - Category (from FoodCategory enum)
               - Quantity
               - Unit
               - Price
            3. Observation: Validate extracted information
            4. Final Answer: Format as a JSON object
            
            Format the final output as a JSON list of items."""),
            ("user", "{text}")
        ])
        
        response = await self.llm.generate(
            prompt=prompt.format_messages(text=text)[0].content,
            temperature=0.3
        )
        
        # Process LLM response and calculate confidence scores
        items = []
        confidence_scores = {}
        
        try:
            parsed = eval(response)  # Safe since we control the LLM output format
            for item_data in parsed:
                item = FoodItem(
                    name=item_data["name"],
                    category=FoodCategory(item_data["category"]),
                    quantity=float(item_data["quantity"]),
                    unit=item_data["unit"],
                    price=float(item_data["price"])
                )
                items.append(item)
                confidence_scores[item.name] = self._calculate_confidence(item_data)
        except Exception as e:
            raise Exception(f"Failed to parse items: {str(e)}")
        
        return items, confidence_scores
    
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
        workflow = StateGraph(ReceiptParserState)
        
        # Define nodes based on ReACT framework
        # 1. Observe: Extract text from receipt
        workflow.add_node("observe", self._extract_text_node)
        # 2. Think: Parse and analyze items
        workflow.add_node("think", self._parse_items_node)
        # 3. Act: Validate and decide on next action
        workflow.add_node("act", self._validate_results_node)
        
        # Define edges
        workflow.add_edge("observe", "think")
        workflow.add_edge("think", "act")
        
        # Add conditional edges for human validation
        workflow.add_conditional_edges(
            "act",
            self._needs_human_validation,
            {
                True: "end",  # Requires human validation
                False: "end"  # Automatically proceed
            }
        )
        
        workflow.set_entry_point("observe")
        return workflow.compile(checkpointer=self.memory)
    
    async def _extract_text_node(self, state: ReceiptParserState) -> ReceiptParserState:
        """Node for text extraction from image/PDF (Observe step)."""
        try:
            if state.current_receipt and state.current_receipt.image_path:
                if state.current_receipt.image_path.endswith('.pdf'):
                    text = await self.tool_executor.execute(
                        "extract_text_from_pdf",
                        {"pdf_path": state.current_receipt.image_path}
                    )
                else:
                    text = await self.tool_executor.execute(
                        "extract_text_from_image",
                        {"image_path": state.current_receipt.image_path}
                    )
                
                state.current_receipt.raw_text = text
                state.step += 1
                state.status = "text_extracted"
            else:
                state.error = "No image path provided"
                state.status = "failed"
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _parse_items_node(self, state: ReceiptParserState) -> ReceiptParserState:
        """Node for parsing items from text (Think step)."""
        try:
            if state.current_receipt and state.current_receipt.raw_text:
                items, confidence_scores = await self.tool_executor.execute(
                    "parse_items",
                    {"text": state.current_receipt.raw_text}
                )
                
                state.extracted_items = items
                state.confidence_scores = confidence_scores
                state.step += 1
                state.status = "items_parsed"
            else:
                state.error = "No raw text available"
                state.status = "failed"
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _validate_results_node(self, state: ReceiptParserState) -> ReceiptParserState:
        """Node for validating parsed results (Act step)."""
        if not state.extracted_items:
            state.requires_human_validation = True
            state.status = "needs_validation"
            return state
        
        # Check confidence scores
        low_confidence_items = [
            item.name for item in state.extracted_items
            if state.confidence_scores.get(item.name, 0) < self.confidence_threshold
        ]
        
        if low_confidence_items:
            state.requires_human_validation = True
            state.metadata["low_confidence_items"] = low_confidence_items
            state.status = "needs_validation"
        else:
            state.requires_human_validation = False
            state.status = "completed"
        
        state.step += 1
        return state
    
    def _needs_human_validation(self, state: ReceiptParserState) -> bool:
        """Determine if human validation is needed."""
        return state.requires_human_validation
    
    async def process_receipt(self, image_path: str) -> ReceiptParserState:
        """Process a receipt image/PDF and extract items."""
        initial_state = ReceiptParserState(
            agent_id="receipt_parser",
            current_receipt=Receipt(
                date=datetime.now(),
                items=[],
                total_amount=0.0,
                image_path=image_path
            )
        )
        
        return await self.graph.arun(initial_state) 