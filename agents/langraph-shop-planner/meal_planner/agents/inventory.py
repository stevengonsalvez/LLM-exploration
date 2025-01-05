from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph
from langgraph.checkpoint.memory import MemorySaver

from ..core.schemas.base import (
    Inventory, FoodItem, InventoryState
)
from ..core.llm.base import BaseLLM

class InventoryAgent:
    def __init__(
        self,
        llm: BaseLLM,
        expiry_warning_days: int = 7
    ):
        self.llm = llm
        self.expiry_warning_days = expiry_warning_days
        self.memory = MemorySaver()
        self.graph = self._create_graph()
    
    def _create_graph(self) -> Graph:
        """Create the inventory management graph following ReACT framework."""
        workflow = StateGraph(InventoryState)
        
        # Define nodes based on ReACT framework
        # 1. Observe: Update inventory with new items
        workflow.add_node("observe", self._update_inventory_node)
        # 2. Think: Check expiry dates and analyze inventory
        workflow.add_node("think", self._check_expiry_node)
        # 3. Act: Optimize and suggest actions
        workflow.add_node("act", self._optimize_inventory_node)
        
        # Define edges
        workflow.add_edge("observe", "think")
        workflow.add_edge("think", "act")
        
        workflow.set_entry_point("observe")
        return workflow.compile(checkpointer=self.memory)
    
    async def _update_inventory_node(self, state: InventoryState) -> InventoryState:
        """Node for updating inventory with new items (Observe step)."""
        try:
            current_items = state.current_inventory.items
            
            for new_item in state.pending_updates:
                if new_item.name in current_items:
                    # Update existing item
                    existing_item = current_items[new_item.name]
                    existing_item.quantity += new_item.quantity
                    existing_item.expiry_date = new_item.expiry_date or existing_item.expiry_date
                    existing_item.price = new_item.price or existing_item.price
                else:
                    # Add new item
                    current_items[new_item.name] = new_item
            
            state.current_inventory.last_updated = datetime.now()
            state.step += 1
            state.status = "inventory_updated"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _check_expiry_node(self, state: InventoryState) -> InventoryState:
        """Node for checking expiry dates and analyzing inventory (Think step)."""
        try:
            current_items = state.current_inventory.items
            now = datetime.now()
            warning_date = now + timedelta(days=self.expiry_warning_days)
            
            # Check expiry dates
            expired_items = []
            for name, item in list(current_items.items()):
                if item.expiry_date:
                    if item.expiry_date <= now:
                        expired_items.append(item)
                        del current_items[name]
                    elif item.expiry_date <= warning_date:
                        state.metadata.setdefault("expiring_soon", []).append(item)
            
            state.expired_items = expired_items
            state.step += 1
            state.status = "expiry_checked"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _optimize_inventory_node(self, state: InventoryState) -> InventoryState:
        """Node for optimizing inventory using LLM (Act step)."""
        try:
            if not state.current_inventory.items:
                state.status = "completed"
                return state
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an inventory optimization expert following the ReACT framework.
                For the current inventory:
                1. Thought: Analyze the current inventory state and expiry dates
                2. Action: Generate optimization suggestions considering:
                   - Items that need to be used soon
                   - Common recipe combinations
                   - Storage optimization
                3. Observation: Review suggestions for practicality
                4. Final Answer: Provide structured recommendations
                
                Format suggestions in a clear, actionable format."""),
                ("user", "{inventory}")
            ])
            
            inventory_str = "\n".join([
                f"{name}: {item.quantity} {item.unit} (expires: {item.expiry_date})"
                for name, item in state.current_inventory.items.items()
            ])
            
            response = await self.llm.generate(
                prompt=prompt.format_messages(inventory=inventory_str)[0].content,
                temperature=0.3
            )
            
            state.metadata["optimization_suggestions"] = response
            state.step += 1
            state.status = "completed"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def update_inventory(self, current_inventory: Inventory, new_items: List[FoodItem]) -> InventoryState:
        """Update inventory with new items and perform optimization."""
        initial_state = InventoryState(
            agent_id="inventory_manager",
            current_inventory=current_inventory,
            pending_updates=new_items
        )
        
        return await self.graph.arun(initial_state)
    
    async def get_available_ingredients(self, min_quantity: float = 0.0) -> List[FoodItem]:
        """Get list of available ingredients above minimum quantity."""
        available = []
        for item in self.current_inventory.items.values():
            if item.quantity > min_quantity:
                available.append(item)
        return available 