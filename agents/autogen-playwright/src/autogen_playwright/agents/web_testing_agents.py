from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import logging
import json
from typing import Optional
from ..skills.playwright_skill import PlaywrightSkill
from ..llm.provider import LLMProvider

logger = logging.getLogger(__name__)

def is_test_complete(msg: dict) -> bool:
    """Check if the test execution is complete or if message is empty"""
    content = msg.get("content", "")
    if not content:
        logger.warning("Received empty message content")
        return False
    
    content = content.lower()
    logger.info(f"Checking message content: {content[:100]}...")
    # Only terminate after the TestReport summary
    return "you can find the full test report at:" in content

class ConversationMonitor:
    """Monitor conversation for empty messages and token usage"""
    def __init__(self, max_consecutive_empty: int = 3, max_total_tokens: Optional[int] = None):
        self.max_consecutive_empty = max_consecutive_empty
        self.max_total_tokens = max_total_tokens
        self.consecutive_empty = 0
        self.total_tokens = 0
        
    def check_message(self, msg: dict) -> bool:
        """
        Check message against termination conditions
        Returns True if should terminate
        """
        content = msg.get("content", "").strip()
        
        # Check for empty messages
        if not content:
            self.consecutive_empty += 1
            logger.warning(f"Empty message detected ({self.consecutive_empty}/{self.max_consecutive_empty})")
            if self.consecutive_empty >= self.max_consecutive_empty:
                logger.error(f"Terminating due to {self.consecutive_empty} consecutive empty messages")
                return True
        else:
            self.consecutive_empty = 0
            
        # Track token usage if response contains it
        try:
            if "response" in msg:
                response = json.loads(msg["response"])
                if "usage" in response:
                    usage = response["usage"]
                    tokens = usage.get("total_tokens", 0)
                    self.total_tokens += tokens
                    logger.info(f"Total tokens used: {self.total_tokens}")
                    
                    if self.max_total_tokens and self.total_tokens >= self.max_total_tokens:
                        logger.error(f"Terminating due to token limit: {self.total_tokens} >= {self.max_total_tokens}")
                        return True
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
            
        return False

def create_web_testing_agents(use_group_chat: bool = False):
    """
    Create and initialize web testing agents
    Args:
        use_group_chat: Whether to use GroupChat for better conversation control
    """
    llm_config = LLMProvider().get_config()
    logger.info(f"Creating agents with config: {llm_config}")
    
    # Create conversation monitor
    monitor = ConversationMonitor(
        max_consecutive_empty=llm_config.get("max_consecutive_empty", 3),
        max_total_tokens=llm_config.get("max_total_tokens")
    )
    
    def is_termination_msg(msg: dict) -> bool:
        """Combined check for test completion and conversation limits"""
        if monitor.check_message(msg):
            return True
        return is_test_complete(msg)
    
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
        llm_config=llm_config,
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1
        )

    # Create the user proxy agent
    user_proxy = UserProxyAgent(
        name="executor",
        human_input_mode="NEVER",
        code_execution_config={
            "use_docker": False,
            "last_n_messages": 3,  # Consider last 3 messages for context
            "work_dir": None       # Use default working directory
        },
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1
    )

    if use_group_chat:
        # Create a manager agent to coordinate the conversation
        manager = GroupChatManager(
            groupchat=GroupChat(
                agents=[testing_agent, user_proxy],
                messages=[],
                max_round=15  # Limit conversation rounds
            ),
            llm_config=llm_config,
            is_termination_msg=is_termination_msg
        )
        return testing_agent, user_proxy, manager
    
    return testing_agent, user_proxy

# Export only the function
__all__ = ['create_web_testing_agents'] 