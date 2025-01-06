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
    try:
        chat_result = user_proxy.initiate_chat(
            testing_agent,
            message="""
            Execute the following test scenario:
            
            Test Scenario: EE Broadband Page Navigation and Validation
            
            Steps:
            1. Navigate to ee.co.uk
            2. Accept cookies in the OneTrust banner
            3. Navigate to Broadband section
            4. Click on 'Explore Broadband'
            5. Analyze and summarize the page content
            6. Verify presence of broadband availability checker
            
            Important:
            - Maximum 5 retries for any action
            - Take screenshots at key steps
            - Provide detailed error information if steps fail
            - Generate a test summary at the end
            """,
            max_consecutive_auto_reply=2
        )
        
        # Print final test results and terminate
        print("\nChat Execution Summary:")
        print("-" * 50)
        last_meaningful_message = None
        
        for message in chat_result.chat_history:
            if message.get("content"):
                content = message.get("content").strip()
                if content:  # Only process non-empty messages
                    last_meaningful_message = content
                    print(f"{message['role']}: {content}\n")
                    
                    # Check for test completion markers
                    if any(marker in content for marker in [
                        "Test Status: COMPLETED",
                        "Test Execution Summary",
                        "Detailed report:"
                    ]):
                        print("Test execution completed, terminating...")
                        return  # Exit function instead of using exit(0)
        
        # If we got here and have a last message, print it
        if last_meaningful_message:
            print(f"Last message received: {last_meaningful_message}")
            
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
        return
    finally:
        print("Test execution completed")

if __name__ == "__main__":
    run_test() 