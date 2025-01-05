import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio
import streamlit as st
from dotenv import load_dotenv

from core.llm.openai_llm import OpenAILLM, OpenAIConfig
from core.schemas.base import (
    Inventory, FoodItem, Receipt, MealPlan, FoodCategory,
    ReceiptParserState, InventoryState, MealPlannerState
)
from agents.receipt_parser import ReceiptParserAgent
from agents.inventory import InventoryAgent
from agents.meal_planner import MealPlannerAgent
from config.settings import settings

# Load environment variables
load_dotenv()

class MealPlannerApp:
    def __init__(self):
        # Initialize LLM
        llm_config = OpenAIConfig(**settings.get_llm_config())
        self.llm = OpenAILLM(llm_config)
        
        # Initialize agents
        self.receipt_parser = ReceiptParserAgent(
            self.llm,
            confidence_threshold=settings.confidence_threshold
        )
        self.inventory_manager = InventoryAgent(
            self.llm,
            expiry_warning_days=settings.expiry_warning_days
        )
        self.meal_planner = MealPlannerAgent(
            self.llm,
            min_meals_per_day=settings.min_meals_per_day,
            max_meals_per_day=settings.max_meals_per_day
        )
        
        # Initialize state
        self.inventory = Inventory(items={})
        
        # Ensure directories exist
        settings.ensure_directories()
    
    async def process_receipt(self, file_path: str) -> ReceiptParserState:
        """Process a receipt image/PDF and extract items."""
        return await self.receipt_parser.process_receipt(file_path)
    
    async def update_inventory(self, items: List[FoodItem]) -> InventoryState:
        """Update inventory with new items."""
        return await self.inventory_manager.update_inventory(self.inventory, items)
    
    async def generate_meal_plan(
        self,
        start_date: datetime,
        end_date: datetime,
        dietary_restrictions: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> MealPlannerState:
        """Generate a meal plan."""
        available_ingredients = list(self.inventory.items.values())
        return await self.meal_planner.generate_meal_plan(
            available_ingredients,
            start_date,
            end_date,
            dietary_restrictions,
            preferences
        )

async def main():
    st.title("Smart Meal Planner")
    
    # Initialize app
    if "app" not in st.session_state:
        st.session_state.app = MealPlannerApp()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Receipt Upload", "Inventory", "Meal Planning"])
    
    if page == "Receipt Upload":
        st.header("Upload Receipt")
        uploaded_file = st.file_uploader("Choose a receipt image or PDF", type=["jpg", "jpeg", "png", "pdf"])
        
        if uploaded_file:
            # Save uploaded file
            file_path = f"uploads/{uploaded_file.name}"
            os.makedirs("uploads", exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("Process Receipt"):
                with st.spinner("Processing receipt..."):
                    receipt_state = await st.session_state.app.process_receipt(file_path)
                    
                    if receipt_state.status == "completed":
                        st.success("Receipt processed successfully!")
                        st.write("Extracted Items:")
                        for item in receipt_state.extracted_items:
                            st.write(f"- {item.name}: {item.quantity} {item.unit}")
                        
                        if st.button("Add to Inventory"):
                            inventory_state = await st.session_state.app.update_inventory(receipt_state.extracted_items)
                            if inventory_state.status == "completed":
                                st.success("Inventory updated successfully!")
                    
                    elif receipt_state.status == "needs_validation":
                        st.warning("Some items need validation:")
                        for item_name in receipt_state.metadata.get("low_confidence_items", []):
                            st.write(f"- {item_name}")
                    
                    else:
                        st.error(f"Error processing receipt: {receipt_state.error}")
    
    elif page == "Inventory":
        st.header("Current Inventory")
        
        # Display current inventory
        for name, item in st.session_state.app.inventory.items.items():
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{name}**")
            with col2:
                st.write(f"{item.quantity} {item.unit}")
            with col3:
                if item.expiry_date:
                    st.write(f"Expires: {item.expiry_date.strftime('%Y-%m-%d')}")
        
        # Manual item entry
        st.subheader("Add Item Manually")
        with st.form("add_item"):
            name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1)
            unit = st.text_input("Unit")
            category = st.selectbox("Category", [c.value for c in FoodCategory])
            expiry = st.date_input("Expiry Date")
            
            if st.form_submit_button("Add Item"):
                new_item = FoodItem(
                    name=name,
                    quantity=quantity,
                    unit=unit,
                    category=category,
                    expiry_date=datetime.combine(expiry, datetime.min.time())
                )
                inventory_state = await st.session_state.app.update_inventory([new_item])
                if inventory_state.status == "completed":
                    st.success("Item added successfully!")
    
    elif page == "Meal Planning":
        st.header("Generate Meal Plan")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            days = st.number_input("Number of Days", min_value=1, max_value=31, value=7)
        
        end_date = start_date + timedelta(days=days-1)
        
        # Dietary restrictions
        st.subheader("Dietary Restrictions")
        restrictions = []
        if st.checkbox("Vegetarian"):
            restrictions.append("vegetarian")
        if st.checkbox("Vegan"):
            restrictions.append("vegan")
        if st.checkbox("Gluten-free"):
            restrictions.append("gluten-free")
        
        # Preferences
        st.subheader("Preferences")
        preferences = {}
        preferences["max_prep_time"] = st.slider("Maximum Prep Time (minutes)", 0, 120, 30)
        preferences["calories_per_day"] = st.slider("Target Calories per Day", 1000, 3000, 2000)
        
        if st.button("Generate Plan"):
            with st.spinner("Generating meal plan..."):
                plan_state = await st.session_state.app.generate_meal_plan(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.min.time()),
                    restrictions,
                    preferences
                )
                
                if plan_state.status == "completed":
                    st.success("Meal plan generated successfully!")
                    
                    # Display meal plan
                    st.subheader("Meal Plan")
                    for date, recipes in plan_state.current_plan.meals.items():
                        st.write(f"**{date}**")
                        for recipe in recipes:
                            with st.expander(f"{recipe.name} ({recipe.meal_type})"):
                                st.write("**Ingredients:**")
                                for ingredient in recipe.ingredients:
                                    st.write(f"- {ingredient.quantity} {ingredient.unit} {ingredient.name}")
                                st.write("\n**Instructions:**")
                                for i, step in enumerate(recipe.instructions, 1):
                                    st.write(f"{i}. {step}")
                                st.write(f"\nPrep time: {recipe.prep_time} minutes")
                                st.write(f"Cook time: {recipe.cook_time} minutes")
                                if recipe.calories_per_serving:
                                    st.write(f"Calories per serving: {recipe.calories_per_serving}")
                    
                    # Display shopping list
                    st.subheader("Shopping List")
                    for item in plan_state.current_plan.shopping_list:
                        st.write(f"- {item.quantity} {item.unit} {item.name}")
                
                else:
                    st.error(f"Error generating meal plan: {plan_state.error}")

if __name__ == "__main__":
    asyncio.run(main()) 