from typing import Dict, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class FoodCategory(str, Enum):
    PROTEIN = "protein"
    VEGETABLE = "vegetable"
    FRUIT = "fruit"
    GRAIN = "grain"
    DAIRY = "dairy"
    CONDIMENT = "condiment"
    SNACK = "snack"
    BEVERAGE = "beverage"
    OTHER = "other"

class FoodItem(BaseModel):
    """Represents a food item from receipt or inventory."""
    name: str
    category: FoodCategory
    quantity: float
    unit: str
    expiry_date: Optional[datetime] = None
    price: Optional[float] = None
    calories_per_unit: Optional[float] = None
    nutritional_info: Optional[Dict[str, float]] = None

class Receipt(BaseModel):
    """Represents a processed receipt."""
    id: str = Field(default_factory=lambda: datetime.now().isoformat())
    date: datetime
    store_name: Optional[str] = None
    items: List[FoodItem]
    total_amount: float
    raw_text: Optional[str] = None
    image_path: Optional[str] = None

class Inventory(BaseModel):
    """Represents the current food inventory."""
    items: Dict[str, FoodItem]  # name -> FoodItem
    last_updated: datetime = Field(default_factory=datetime.now)

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class Recipe(BaseModel):
    """Represents a recipe."""
    name: str
    meal_type: MealType
    ingredients: List[FoodItem]
    instructions: List[str]
    prep_time: int  # minutes
    cook_time: int  # minutes
    servings: int
    calories_per_serving: Optional[float] = None
    nutritional_info: Optional[Dict[str, float]] = None

class MealPlan(BaseModel):
    """Represents a meal plan."""
    id: str = Field(default_factory=lambda: datetime.now().isoformat())
    start_date: datetime
    end_date: datetime
    meals: Dict[str, List[Recipe]]  # date -> list of recipes
    shopping_list: List[FoodItem]
    total_calories: Optional[float] = None
    notes: Optional[str] = None

class AgentState(BaseModel):
    """Base state for all agents."""
    agent_id: str
    step: int = 0
    status: str = "initialized"
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    checkpoint: Optional[Dict[str, Any]] = None

class ReceiptParserState(AgentState):
    """State for receipt parsing agent."""
    current_receipt: Optional[Receipt] = None
    extracted_items: List[FoodItem] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    requires_human_validation: bool = False

class InventoryState(AgentState):
    """State for inventory management agent."""
    current_inventory: Inventory
    pending_updates: List[FoodItem] = Field(default_factory=list)
    expired_items: List[FoodItem] = Field(default_factory=list)

class MealPlannerState(AgentState):
    """State for meal planning agent."""
    current_plan: Optional[MealPlan] = None
    available_ingredients: List[FoodItem] = Field(default_factory=list)
    dietary_restrictions: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict) 