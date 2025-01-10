import os
import logging
from pathlib import Path
from dotenv import load_dotenv
import autogen
from autogen_playwright.ops import print_session_summary, analyze_conversation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_env_file():
    """Find the .env file in the project root"""
    current_dir = Path.cwd()
    
    # First check in current directory
    env_path = current_dir / '.env'
    if env_path.exists():
        return env_path
        
    # Then check in project root (up one level from examples)
    project_root = current_dir.parent if current_dir.name == 'examples' else current_dir
    env_path = project_root / '.env'
    if env_path.exists():
        return env_path
        
    # Finally check in parent directory
    env_path = project_root.parent / '.env'
    if env_path.exists():
        return env_path
        
    raise FileNotFoundError("Could not find .env file in project directories")

def run_test(test_steps=None):
    try:
        logger.info("Starting test execution...")
        
        # Import after environment variables are loaded
        from autogen_playwright import create_web_testing_agents, PlaywrightSkill
        
        # Create agents with loaded environment
        use_group_chat = os.getenv('USE_GROUP_CHAT', 'true').lower() == 'true'
        logger.info(f"Using group chat mode: {use_group_chat}")
        
        agents = create_web_testing_agents(use_group_chat=use_group_chat)
        
        if use_group_chat:
            testing_agent, debug_agent, admin_agent, executor, manager = agents
        else:
            testing_agent, executor = agents
        
        # Start runtime logging with SQLite
        db_path = Path("runtime_logs/autogen_logs.db")
        db_path.parent.mkdir(exist_ok=True)
        logging_config = {
            "dbname": str(db_path),
            "table_name": "agent_logs",
            "create_table": True
        }
        logging_session_id = autogen.runtime_logging.start(config=logging_config)
        logger.info(f"Started autogen runtime logging with session ID: {logging_session_id}")
        
        # Default test steps if none provided
        default_steps = [
            "Navigate to ee.co.uk",
            "Accept cookies in the OneTrust banner",
            "Hover over 'Broadband' in the global navigation menu",
            "click to 'explore broadband' within the submenu pop up on the hover",
            "Analyze and summarize the page content",
            "Then go and enter postcode as UB87PE in the postcode field and click continue",
            "Analyze and summarize the page"
        ]
        
        steps_to_use = test_steps if test_steps else default_steps
        steps_formatted = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps_to_use))
        
        test_message = f"""
        Execute the following test scenario:
        
        Test Scenario: EE Broadband Page Navigation and Validation
        
        Steps:
        {steps_formatted}
        
        Important:
        - Maximum 5 retries for any action
        - Take screenshots at key steps
        - Provide detailed error information if steps fail
        - Generate a test summary at the end
        """
        
        try:
            logger.info("Initiating chat with test message...")
            max_iterations = int(os.getenv('MAX_ITERATIONS', '10'))
            
            # Initiate chat based on mode
            if use_group_chat:
                chat_result = executor.initiate_chat(
                    manager,
                    message=test_message,
                    max_turns=max_iterations
                )
            else:
                chat_result = executor.initiate_chat(
                    testing_agent,
                    message=test_message,
                    max_turns=max_iterations,
                    summary_method="reflection_with_llm"
                )
            
            return True
                
        finally:
            # Stop runtime logging and print session info
            autogen.runtime_logging.stop()
            logger.info(f"Stopped autogen runtime logging for session {logging_session_id}")
            
            # Print analytics
            print("\n=== Test Analytics ===")
            print_session_summary(logging_session_id, str(db_path))
            analyze_conversation(logging_session_id, str(db_path))
            
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
        print(f"Test execution failed: {str(e)}")
        return False

if __name__ == "__main__":
    try:
        # Find and load the correct .env file
        env_path = find_env_file()
        load_dotenv(dotenv_path=env_path, override=True)
        
        logger.info(f"Environment loaded from: {env_path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Environment variables after loading:")
        logger.info(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
        logger.info(f"LLM_MODEL: {os.getenv('LLM_MODEL')}")
        
        # Example of how to pass custom steps
        custom_steps = os.getenv('TEST_STEPS')
        if custom_steps:
            try:
                import json
                steps = json.loads(custom_steps)
            except json.JSONDecodeError:
                logger.warning("Invalid TEST_STEPS format, using default steps")
                steps = None
        else:
            steps = None
            
        success = run_test(test_steps=steps)
        exit_code = 0 if success else 1
        os._exit(exit_code)
        
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}", exc_info=True)
        print(f"Failed to initialize: {str(e)}")
        os._exit(1)