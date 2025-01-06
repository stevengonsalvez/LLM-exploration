from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from ..skills.playwright_skill import PlaywrightSkill
from ..llm.provider import LLMProvider

def is_test_complete(msg: dict) -> bool:
    """Check if the test execution is complete or if message is empty"""
    content = msg.get("content", "")
    if not content:
        return False
    
    content = content.lower()
    # Only terminate after the TestReport summary
    return "you can find the full test report at:" in content

def create_web_testing_agents(use_group_chat: bool = False):
    """
    Create and initialize web testing agents
    Args:
        use_group_chat: Whether to use GroupChat for better conversation control
    """
    # Create the testing agent
    testing_agent = AssistantAgent(
        name="web_tester",
        system_message="""You are a web testing expert who writes Python code using Playwright.

Available Tools:
1. PlaywrightSkill class with methods:
   - start_session(scenario_name: str) -> Initializes browser session
   - navigate(url: str, wait_for_load: bool = True) -> Navigates to URL
   - fill_form(selector: str, value: str) -> Fills form fields
   - click_element(selector: str) -> Clicks elements
   - verify_element_exists(selector: str) -> Checks element presence
   - verify_text_content(text: str) -> Verifies text on page
   - take_screenshot(name: str, full_page: bool = False) -> Captures page state
   - end_session() -> Closes browser and saves report

Best Practices:
- Always import PlaywrightSkill from autogen_playwright
- Use try/except blocks for each critical step
- Limit retries to 5 attempts per action
- Take screenshots after important state changes
- Handle errors gracefully and continue if possible
- Provide clear error messages and context

Important Rules:
- After test completion, call end_session() to generate the test report
- Do not generate your own test summary (the report will include one)
- End the conversation after the test report is generated
- Do not acknowledge or respond to further messages

Common Selectors:
- Cookie banners: '#onetrust-accept-btn-handler', '[aria-label*="Accept"]'
- Navigation: 'nav a', '[role="navigation"]'
- Headers: 'h1, h2, h3'
- CTAs: '.cta, [role="button"], a:has-text("Check")'
- Text content: 'text=Example', '.content p'""",
        llm_config=LLMProvider().get_config(),
        is_termination_msg=is_test_complete
    )

    # Create the user proxy agent
    user_proxy = UserProxyAgent(
        name="executor",
        human_input_mode="NEVER",
        code_execution_config={"use_docker": False},
        is_termination_msg=is_test_complete
    )

    if use_group_chat:
        # Create a manager agent to coordinate the conversation
        manager = GroupChatManager(
            groupchat=GroupChat(
                agents=[testing_agent, user_proxy],
                messages=[],
                max_round=15  # Limit conversation rounds
            ),
            llm_config=LLMProvider().get_config(),
            is_termination_msg=is_test_complete
        )
        return testing_agent, user_proxy, manager
    
    return testing_agent, user_proxy

# Create default instances for backward compatibility
testing_agent, user_proxy = create_web_testing_agents()

# Export both the function and default instances
__all__ = ['create_web_testing_agents', 'testing_agent', 'user_proxy'] 