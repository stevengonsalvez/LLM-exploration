from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver

from ..core.schemas.state import InventoryMessagesState
from ..core.llm.base import BaseLLM

class InventoryAgent:
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
                "name": "update_inventory",
                "description": "Update inventory with new items",
                "func": self._update_inventory,
            }
        ]
    
    async def _update_inventory(self, items: List[Dict]) -> Dict[str, Any]:
        """Update inventory with new items."""
        # Simulate database update
        return {
            "updated_items": items,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _process_items(self, state: InventoryMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process items through LLM following ReACT framework."""
        messages = [
            SystemMessage(content="""You are an expert inventory manager following the ReACT framework.
            For each item:
            1. Thought: Analyze the item and its current inventory status
            2. Action: Determine appropriate inventory action
               - Add new item
               - Update existing item
               - Remove item
            3. Observation: Validate inventory changes
            4. Final Answer: Format as a JSON object with action and details
            
            Format the final output as a JSON list of inventory actions."""),
            HumanMessage(content=str(state.current_items))
        ]
        
        response = await self.llm.generate(
            prompt="".join([m.content for m in messages]),
            temperature=0.3
        )
        
        try:
            parsed = eval(response)
            state.inventory_actions = parsed
            state.confidence_scores = {
                action["item"]: self._calculate_confidence(action)
                for action in parsed
            }
            state.status = "actions_determined"
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return {"messages": messages}
    
    def _calculate_confidence(self, action_data: Dict) -> float:
        """Calculate confidence score for inventory action."""
        score = 1.0
        required_fields = ["item", "action", "quantity", "unit"]
        
        for field in required_fields:
            if field not in action_data or not action_data[field]:
                score *= 0.8
            elif isinstance(action_data[field], str) and len(action_data[field].strip()) < 2:
                score *= 0.9
        
        return score
    
    def _create_graph(self) -> Graph:
        """Create the inventory management graph following ReACT framework."""
        workflow = StateGraph(InventoryMessagesState)
        
        # Define nodes
        workflow.add_node("process", self._process_items)
        workflow.add_node("update", self._update_node)
        workflow.add_node("validate", self._validate_node)
        
        # Define edges
        workflow.add_edge("process", "update")
        workflow.add_edge("update", "validate")
        
        # Add conditional edges for validation
        workflow.add_conditional_edges(
            "validate",
            self._needs_validation,
            {
                True: END,  # Requires human validation
                False: END  # Automatically proceed
            }
        )
        
        workflow.set_entry_point("process")
        return workflow.compile(checkpointer=self.memory)
    
    async def _update_node(self, state: InventoryMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update inventory with determined actions."""
        try:
            if not state.inventory_actions:
                raise ValueError("No inventory actions to process")
            
            result = await self.tool_executor.execute(
                "update_inventory",
                {"items": state.inventory_actions}
            )
            
            state.update_result = result
            state.status = "inventory_updated"
            
            return {
                "messages": [
                    SystemMessage(content="Inventory updated successfully"),
                    HumanMessage(content=str(result))
                ]
            }
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
            return {
                "messages": [
                    SystemMessage(content=f"Error updating inventory: {str(e)}")
                ]
            }
    
    async def _validate_node(self, state: InventoryMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate inventory updates."""
        if not state.inventory_actions:
            state.requires_validation = True
            state.status = "needs_validation"
            return {
                "messages": [
                    SystemMessage(content="No inventory actions processed, requires validation")
                ]
            }
        
        # Check confidence scores
        low_confidence_actions = [
            action["item"] for action in state.inventory_actions
            if state.confidence_scores.get(action["item"], 0) < self.confidence_threshold
        ]
        
        if low_confidence_actions:
            state.requires_validation = True
            state.metadata["low_confidence_actions"] = low_confidence_actions
            state.status = "needs_validation"
            return {
                "messages": [
                    SystemMessage(content=f"Low confidence actions found: {', '.join(low_confidence_actions)}")
                ]
            }
        
        state.requires_validation = False
        state.status = "completed"
        return {
            "messages": [
                SystemMessage(content="All inventory actions validated successfully")
            ]
        }
    
    def _needs_validation(self, state: InventoryMessagesState) -> bool:
        """Determine if human validation is needed."""
        return state.requires_validation
    
    async def update_inventory(self, items: List[Dict]) -> Dict[str, Any]:
        """Update inventory with new items."""
        config = {
            "configurable": {
                "thread_id": datetime.now().isoformat()
            }
        }
        
        initial_state = InventoryMessagesState(
            agent_id="inventory_manager",
            messages=[],
            current_items=items
        )
        
        return await self.graph.astream_events(
            {"messages": initial_state.messages},
            config,
            version="v2"
        ) 