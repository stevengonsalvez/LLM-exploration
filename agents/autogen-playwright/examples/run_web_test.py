import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (where .env should be)
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'

# Load environment variables from .env file BEFORE other imports
load_dotenv(dotenv_path=env_path)

# Debug print
print(f"Project root: {project_root}")
print(f"Env file path: {env_path}")
print(f"Env file exists: {env_path.exists()}")
print(f"LLM_API_KEY loaded: {'LLM_API_KEY' in os.environ}")
print(f"Current working directory: {os.getcwd()}")

# Import after environment variables are loaded
from autogen_playwright import testing_agent, user_proxy, PlaywrightSkill

def run_test():
    # Initialize chat between agents
    user_proxy.initiate_chat(
        testing_agent,
        message="""
        Please test the login page at https://demo.playwright.dev/todomvc/
        1. Add a new todo item "Buy groceries"
        2. Mark it as completed
        3. Verify the item is marked as completed
        """
    )

if __name__ == "__main__":
    run_test() 