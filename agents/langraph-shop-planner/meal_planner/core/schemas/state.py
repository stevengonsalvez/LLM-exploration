from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

class BaseMessagesState(BaseModel):
    """Base class for message-based agent states."""
    agent_id: str
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "initialized"
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ReceiptParserMessagesState(BaseMessagesState):
    """State for receipt parser agent."""
    current_text: Optional[str] = None
    extracted_items: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    requires_validation: bool = False

class InventoryMessagesState(BaseMessagesState):
    """State for inventory manager agent."""
    current_items: List[Dict[str, Any]] = Field(default_factory=list)
    inventory_actions: List[Dict[str, Any]] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    requires_validation: bool = False
    update_result: Optional[Dict[str, Any]] = None

class MealPlannerMessagesState(BaseMessagesState):
    """State for meal planner agent."""
    available_ingredients: List[Dict[str, Any]] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    meal_suggestions: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    requires_validation: bool = False
    meal_plan: Optional[Dict[str, List[Dict[str, Any]]]] = None 