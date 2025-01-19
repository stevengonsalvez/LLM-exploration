from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt.tool_executor import ToolExecutor
from langgraph.checkpoint.memory import MemorySaver

from ..core.schemas.state import MealPlannerMessagesState
from ..core.llm.base import BaseLLM

class MealPlannerAgent:
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
                "name": "generate_meal_plan",
                "description": "Generate a meal plan based on available ingredients",
                "func": self._generate_meal_plan,
            }
        ]
    
    async def _generate_meal_plan(self, ingredients: List[Dict], preferences: Dict) -> Dict[str, Any]:
        """Generate a meal plan based on available ingredients and preferences."""
        # Simulate meal plan generation
        return {
            "meal_plan": {
                "breakfast": [],
                "lunch": [],
                "dinner": []
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def _process_ingredients(self, state: MealPlannerMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Process ingredients through LLM following ReACT framework."""
        messages = [
            SystemMessage(content="""You are an expert meal planner following the ReACT framework.
            For the available ingredients:
            1. Thought: Analyze ingredients and dietary preferences
            2. Action: Generate meal suggestions considering:
               - Nutritional balance
               - Dietary restrictions
               - Cooking time
               - Ingredient combinations
            3. Observation: Validate meal suggestions
            4. Final Answer: Format as a JSON object with meal plans
            
            Format the final output as a JSON object with breakfast, lunch, and dinner arrays."""),
            HumanMessage(content=f"Ingredients: {state.available_ingredients}\nPreferences: {state.preferences}")
        ]
        
        response = await self.llm.generate(
            prompt="".join([m.content for m in messages]),
            temperature=0.3
        )
        
        try:
            parsed = eval(response)
            state.meal_suggestions = parsed
            state.confidence_scores = {
                meal["name"]: self._calculate_confidence(meal)
                for meals in parsed.values()
                for meal in meals
            }
            state.status = "meals_suggested"
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
        
        return {"messages": messages}
    
    def _calculate_confidence(self, meal_data: Dict) -> float:
        """Calculate confidence score for meal suggestion."""
        score = 1.0
        required_fields = ["name", "ingredients", "cooking_time", "difficulty"]
        
        for field in required_fields:
            if field not in meal_data or not meal_data[field]:
                score *= 0.8
            elif isinstance(meal_data[field], str) and len(meal_data[field].strip()) < 2:
                score *= 0.9
        
        return score
    
    def _create_graph(self) -> Graph:
        """Create the meal planning graph following ReACT framework."""
        workflow = StateGraph(MealPlannerMessagesState)
        
        # Define nodes
        workflow.add_node("process", self._process_ingredients)
        workflow.add_node("generate", self._generate_node)
        workflow.add_node("validate", self._validate_node)
        
        # Define edges
        workflow.add_edge("process", "generate")
        workflow.add_edge("generate", "validate")
        
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
    
    async def _generate_node(self, state: MealPlannerMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meal plan from suggestions."""
        try:
            if not state.meal_suggestions:
                raise ValueError("No meal suggestions to process")
            
            result = await self.tool_executor.execute(
                "generate_meal_plan",
                {
                    "ingredients": state.available_ingredients,
                    "preferences": state.preferences
                }
            )
            
            state.meal_plan = result["meal_plan"]
            state.status = "plan_generated"
            
            return {
                "messages": [
                    SystemMessage(content="Meal plan generated successfully"),
                    HumanMessage(content=str(result))
                ]
            }
            
        except Exception as e:
            state.error = str(e)
            state.status = "failed"
            return {
                "messages": [
                    SystemMessage(content=f"Error generating meal plan: {str(e)}")
                ]
            }
    
    async def _validate_node(self, state: MealPlannerMessagesState, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate meal plan."""
        if not state.meal_suggestions:
            state.requires_validation = True
            state.status = "needs_validation"
            return {
                "messages": [
                    SystemMessage(content="No meal suggestions processed, requires validation")
                ]
            }
        
        # Check confidence scores
        low_confidence_meals = [
            meal["name"]
            for meals in state.meal_suggestions.values()
            for meal in meals
            if state.confidence_scores.get(meal["name"], 0) < self.confidence_threshold
        ]
        
        if low_confidence_meals:
            state.requires_validation = True
            state.metadata["low_confidence_meals"] = low_confidence_meals
            state.status = "needs_validation"
            return {
                "messages": [
                    SystemMessage(content=f"Low confidence meals found: {', '.join(low_confidence_meals)}")
                ]
            }
        
        state.requires_validation = False
        state.status = "completed"
        return {
            "messages": [
                SystemMessage(content="All meal suggestions validated successfully")
            ]
        }
    
    def _needs_validation(self, state: MealPlannerMessagesState) -> bool:
        """Determine if human validation is needed."""
        return state.requires_validation
    
    async def generate_meal_plan(self, ingredients: List[Dict], preferences: Dict) -> Dict[str, Any]:
        """Generate a meal plan based on available ingredients and preferences."""
        config = {
            "configurable": {
                "thread_id": datetime.now().isoformat()
            }
        }
        
        initial_state = MealPlannerMessagesState(
            agent_id="meal_planner",
            messages=[],
            available_ingredients=ingredients,
            preferences=preferences
        )
        
        return await self.graph.astream_events(
            {"messages": initial_state.messages},
            config,
            version="v2"
        ) 