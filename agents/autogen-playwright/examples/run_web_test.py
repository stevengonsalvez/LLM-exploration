import os
from pathlib import Path
from dotenv import load_dotenv

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

# Main execution block
try:
    # Find and load the correct .env file
    env_path = find_env_file()
    load_dotenv(dotenv_path=env_path)
    
    print(f"Environment loaded from: {env_path}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Import after environment variables are loaded
    from autogen_playwright import testing_agent, user_proxy, PlaywrightSkill
except Exception as e:
    print(f"Failed to initialize: {str(e)}")
    os._exit(1)

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
            - Do not continue conversation after test completion
            """,
            max_consecutive_auto_reply=1
        )
        
        # Print final test results and terminate
        print("\nChat Execution Summary:")
        print("-" * 50)
        
        test_completed = False
        for message in chat_result.chat_history:
            if message.get("content"):
                content = message.get("content").strip()
                if content:
                    print(f"{message['role']}: {content}\n")
                    
                    # Check for completion indicators in the content
                    if any(marker in content for marker in [
                        "Test Status: COMPLETED",
                        "Detailed report available at:",
                        "has been successfully executed"
                    ]):
                        test_completed = True
                        break  # Stop processing more messages
                        
        if test_completed:
            print("Test execution completed successfully. Terminating...")
            os._exit(0)  # Force immediate termination
                        
    except Exception as e:
        print(f"Test execution failed: {str(e)}")
        os._exit(1)

if __name__ == "__main__":
    run_test() 