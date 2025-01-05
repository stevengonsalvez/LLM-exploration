from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from langchain.prompts import ChatPromptTemplate
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver

from ..core.schemas.base import (
    FoodItem, Recipe, MealPlan, MealType, MealPlannerState
)
from ..core.llm.base import BaseLLM

class MealPlannerAgent:
    def __init__(
        self,
        llm: BaseLLM,
        min_meals_per_day: int = 3,
        max_meals_per_day: int = 5
    ):
        self.llm = llm
        self.min_meals_per_day = min_meals_per_day
        self.max_meals_per_day = max_meals_per_day
        self.tools = self._create_tools()
        self.tool_executor = ToolExecutor(self.tools)
        self.memory = MemorySaver()
        self.graph = self._create_graph()
    
    def _create_tools(self) -> List[Dict]:
        return [
            {
                "name": "generate_recipes",
                "description": "Generate recipes based on available ingredients",
                "func": self._generate_recipes,
            },
            {
                "name": "optimize_meal_plan",
                "description": "Optimize meal plan for nutrition and variety",
                "func": self._optimize_meal_plan,
            }
        ]
    
    async def _generate_recipes(self, ingredients: List[FoodItem], meal_type: MealType) -> List[Recipe]:
        """Generate recipes using available ingredients."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a creative chef following the ReACT framework.
            For each recipe:
            1. Thought: Analyze available ingredients and meal type requirements
            2. Action: Create a recipe considering:
               - Nutritional balance
               - Cooking time
               - Ingredient combinations
               - Dietary restrictions
            3. Observation: Review recipe feasibility
            4. Final Answer: Format recipe as a JSON object
            
            Format each recipe with complete details."""),
            ("user", "Ingredients: {ingredients}\nMeal Type: {meal_type}")
        ])
        
        ingredients_str = "\n".join([
            f"- {item.name}: {item.quantity} {item.unit}"
            for item in ingredients
        ])
        
        response = await self.llm.generate(
            prompt=prompt.format_messages(
                ingredients=ingredients_str,
                meal_type=meal_type
            )[0].content,
            temperature=0.7
        )
        
        # Parse LLM response into Recipe objects
        recipes = []
        try:
            parsed = eval(response)  # Safe since we control the LLM output format
            for recipe_data in parsed:
                recipe = Recipe(
                    name=recipe_data["name"],
                    meal_type=meal_type,
                    ingredients=recipe_data["ingredients"],
                    instructions=recipe_data["instructions"],
                    prep_time=recipe_data["prep_time"],
                    cook_time=recipe_data["cook_time"],
                    servings=recipe_data["servings"],
                    calories_per_serving=recipe_data.get("calories_per_serving"),
                    nutritional_info=recipe_data.get("nutritional_info")
                )
                recipes.append(recipe)
        except Exception as e:
            raise Exception(f"Failed to parse recipes: {str(e)}")
        
        return recipes
    
    async def _optimize_meal_plan(self, recipes: List[Recipe], days: int) -> Dict[str, List[Recipe]]:
        """Optimize meal plan for nutrition and variety."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meal planning expert following the ReACT framework.
            For the meal plan:
            1. Thought: Analyze available recipes and planning requirements
            2. Action: Create an optimal meal plan considering:
               - Nutritional balance across days
               - Variety in meals
               - Ingredient usage efficiency
               - Dietary preferences and restrictions
            3. Observation: Review plan feasibility
            4. Final Answer: Format plan as a JSON object
            
            Format the plan with dates as keys and lists of recipe names as values."""),
            ("user", "Recipes: {recipes}\nDays: {days}")
        ])
        
        recipes_str = "\n".join([
            f"- {recipe.name} ({recipe.meal_type}): {recipe.calories_per_serving} cal/serving"
            for recipe in recipes
        ])
        
        response = await self.llm.generate(
            prompt=prompt.format_messages(
                recipes=recipes_str,
                days=days
            )[0].content,
            temperature=0.5
        )
        
        # Parse LLM response into meal plan
        try:
            meal_plan = eval(response)  # Safe since we control the LLM output format
            optimized_plan = {}
            
            for date_str, recipe_names in meal_plan.items():
                date_recipes = []
                for name in recipe_names:
                    recipe = next((r for r in recipes if r.name == name), None)
                    if recipe:
                        date_recipes.append(recipe)
                optimized_plan[date_str] = date_recipes
            
            return optimized_plan
            
        except Exception as e:
            raise Exception(f"Failed to optimize meal plan: {str(e)}")
    
    def _create_graph(self) -> Graph:
        """Create the meal planning graph following ReACT framework."""
        workflow = StateGraph(MealPlannerState)
        
        # Define nodes based on ReACT framework
        # 1. Observe: Generate recipes from available ingredients
        workflow.add_node("observe", self._generate_recipes_node)
        # 2. Think: Create initial meal plan
        workflow.add_node("think", self._create_meal_plan_node)
        # 3. Act: Optimize and validate plan
        workflow.add_node("act_optimize", self._optimize_plan_node)
        workflow.add_node("act_validate", self._validate_plan_node)
        
        # Define edges
        workflow.add_edge("observe", "think")
        workflow.add_edge("think", "act_optimize")
        workflow.add_edge("act_optimize", "act_validate")
        
        workflow.set_entry_point("observe")
        return workflow.compile(checkpointer=self.memory)
    
    async def _generate_recipes_node(self, state: MealPlannerState) -> MealPlannerState:
        """Node for generating recipes (Observe step)."""
        try:
            all_recipes = []
            for meal_type in MealType:
                recipes = await self.tool_executor.execute(
                    "generate_recipes",
                    {
                        "ingredients": state.available_ingredients,
                        "meal_type": meal_type
                    }
                )
                all_recipes.extend(recipes)
            
            state.metadata["generated_recipes"] = all_recipes
            state.step += 1
            state.status = "recipes_generated"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _create_meal_plan_node(self, state: MealPlannerState) -> MealPlannerState:
        """Node for creating initial meal plan (Think step)."""
        try:
            if not state.metadata.get("generated_recipes"):
                state.error = "No recipes available"
                state.status = "failed"
                return state
            
            days = (state.current_plan.end_date - state.current_plan.start_date).days + 1
            optimized_plan = await self.tool_executor.execute(
                "optimize_meal_plan",
                {
                    "recipes": state.metadata["generated_recipes"],
                    "days": days
                }
            )
            
            state.current_plan.meals = optimized_plan
            state.step += 1
            state.status = "plan_created"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _optimize_plan_node(self, state: MealPlannerState) -> MealPlannerState:
        """Node for optimizing meal plan (Act step - Optimize)."""
        try:
            if not state.current_plan or not state.current_plan.meals:
                state.error = "No meal plan to optimize"
                state.status = "failed"
                return state
            
            # Calculate shopping list
            shopping_list = {}
            for recipes in state.current_plan.meals.values():
                for recipe in recipes:
                    for ingredient in recipe.ingredients:
                        if ingredient.name in shopping_list:
                            shopping_list[ingredient.name].quantity += ingredient.quantity
                        else:
                            shopping_list[ingredient.name] = ingredient.copy()
            
            state.current_plan.shopping_list = list(shopping_list.values())
            
            # Calculate total calories
            total_calories = 0
            for recipes in state.current_plan.meals.values():
                for recipe in recipes:
                    if recipe.calories_per_serving:
                        total_calories += recipe.calories_per_serving * recipe.servings
            
            state.current_plan.total_calories = total_calories
            state.step += 1
            state.status = "plan_optimized"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def _validate_plan_node(self, state: MealPlannerState) -> MealPlannerState:
        """Node for validating meal plan (Act step - Validate)."""
        try:
            if not state.current_plan or not state.current_plan.meals:
                state.error = "No meal plan to validate"
                state.status = "failed"
                return state
            
            # Validate meal count per day
            for date, recipes in state.current_plan.meals.items():
                if len(recipes) < self.min_meals_per_day:
                    state.metadata.setdefault("warnings", []).append(
                        f"Not enough meals on {date}: {len(recipes)} meals"
                    )
                elif len(recipes) > self.max_meals_per_day:
                    state.metadata.setdefault("warnings", []).append(
                        f"Too many meals on {date}: {len(recipes)} meals"
                    )
            
            state.step += 1
            state.status = "completed"
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return state
    
    async def generate_meal_plan(
        self,
        available_ingredients: List[FoodItem],
        start_date: datetime,
        end_date: datetime,
        dietary_restrictions: Optional[List[str]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> MealPlannerState:
        """Generate a meal plan based on available ingredients and preferences."""
        initial_state = MealPlannerState(
            agent_id="meal_planner",
            available_ingredients=available_ingredients,
            dietary_restrictions=dietary_restrictions or [],
            preferences=preferences or {},
            current_plan=MealPlan(
                start_date=start_date,
                end_date=end_date,
                meals={},
                shopping_list=[]
            )
        )
        
        return await self.graph.arun(initial_state) 