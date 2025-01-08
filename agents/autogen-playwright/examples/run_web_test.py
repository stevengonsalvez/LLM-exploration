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

def run_test():
    try:
        logger.info("Starting test execution...")
        
        # Import after environment variables are loaded
        from autogen_playwright import create_web_testing_agents, PlaywrightSkill
        
        # Create agents with loaded environment
        testing_agent, user_proxy = create_web_testing_agents()
        
        # Start runtime logging with SQLite
        db_path = Path("runtime_logs/autogen_logs.db")
        db_path.parent.mkdir(exist_ok=True)
        logging_config = {
            "dbname": str(db_path),
            "table_name": "agent_logs",  # Optional: specify table name
            "create_table": True         # Optional: create table if not exists
        }
        logging_session_id = autogen.runtime_logging.start(config=logging_config)
        logger.info(f"Started autogen runtime logging with session ID: {logging_session_id}")
        
        test_message = """
        Execute the following test scenario:
        
        Test Scenario: EE Broadband Page Navigation and Validation
        
        Steps:
        1. Navigate to ee.co.uk
        2. Accept cookies in the OneTrust banner
        3. Navigate to Broadband section
        4. Navigate to explore broadband page
        5. Analyze and summarize the page content
        6. Verify presence of broadband availability checker
        
        Important:
        - Maximum 5 retries for any action
        - Take screenshots at key steps
        - Provide detailed error information if steps fail
        - Generate a test summary at the end
        - Do not continue conversation after test completion
        """
        
        try:
            logger.info("Initiating chat with test message...")
            chat_result = user_proxy.initiate_chat(
                testing_agent,
                message=test_message,
                max_consecutive_auto_reply=1,  # Maximum consecutive replies without human input
                max_turns=3,                   # Maximum total turns in the conversation
            )
            
            # Print final test results and terminate
            logger.info("Chat completed, processing results...")
            print("\nChat Execution Summary:")
            print("-" * 50)
            
            test_completed = False
            for message in chat_result.chat_history:
                role = message.get('role', 'unknown')
                content = message.get('content', '').strip()
                
                if content:
                    logger.info(f"Message from {role}: {content[:100]}...")
                    print(f"{role}: {content}\n")
                    
                    # Check for completion indicators
                    if any(marker in content.lower() for marker in [
                        "test status: completed",
                        "detailed report available at:",
                        "has been successfully executed",
                        "you can find the full test report at:"
                    ]):
                        test_completed = True
                        logger.info("Found test completion marker")
                        break
            
            if test_completed:
                logger.info("Test execution completed successfully")
                print("Test execution completed successfully. Terminating...")
                return True
            else:
                logger.warning("Test execution did not complete properly")
                print("Test execution did not complete properly")
                return False
                
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
        load_dotenv(dotenv_path=env_path, override=True)  # Force override any existing env vars
        
        logger.info(f"Environment loaded from: {env_path}")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Environment variables after loading:")
        logger.info(f"LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
        logger.info(f"LLM_MODEL: {os.getenv('LLM_MODEL')}")
        
        success = run_test()
        exit_code = 0 if success else 1
        os._exit(exit_code)
        
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}", exc_info=True)
        print(f"Failed to initialize: {str(e)}")
        os._exit(1)