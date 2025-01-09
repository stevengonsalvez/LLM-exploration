from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, Agent
import logging
import json
import re
from typing import Optional, List, Dict, Any, Tuple, Union
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

def custom_speaker_selection(
    last_speaker: Agent,
    groupchat: GroupChat
) -> Union[Agent, str]:
    """
    Custom speaker selection function for web testing group chat.
    Args:
        last_speaker: The last speaker agent
        groupchat: The GroupChat instance
    Returns:
        Either an Agent instance or a string from ['auto', 'manual', 'random', 'round_robin']
    """
    messages = groupchat.messages
    
    if not messages:
        # Start with web_tester if no messages
        return next(agent for agent in groupchat.agents if agent.name == "web_tester")
        
    last_message = messages[-1]
    content = last_message.get('content', '').lower()
    
    # Check for execution errors or failures
    error_patterns = [
        r"failed to .+: timeout \d+ms exceeded",
        r"error: .+",
        r"failed to .+: both normal and force click failed",
        r"element is not visible",
        r"element .+ not found",
        r"navigation timeout",
        r"execution failed"
    ]
    
    has_error = any(re.search(pattern, content) for pattern in error_patterns)
    
    if has_error and last_speaker.name == "executor":
        # If executor reports an error, route to debug_agent
        logger.info("Routing to debug_agent due to execution error")
        return next(agent for agent in groupchat.agents if agent.name == "debug_agent")
        
    if last_speaker.name == "debug_agent":
        # After debug_agent provides suggestions, route back to web_tester
        logger.info("Routing back to web_tester to implement fixes")
        return next(agent for agent in groupchat.agents if agent.name == "web_tester")
        
    if last_speaker.name == "web_tester":
        # Route web_tester's actions to security_admin for approval
        logger.info("Routing to security_admin for code review")
        return next(agent for agent in groupchat.agents if agent.name == "security_admin")
        
    if last_speaker.name == "security_admin":
        if "approved" in content:
            # If admin approves, route to executor
            logger.info("Code approved by admin, routing to executor")
            return next(agent for agent in groupchat.agents if agent.name == "executor")
        else:
            # If admin rejects, route back to web_tester for modifications
            logger.info("Code rejected by admin, routing back to web_tester")
            return next(agent for agent in groupchat.agents if agent.name == "web_tester")
    
    # Default to web_tester for other cases
    return next(agent for agent in groupchat.agents if agent.name == "web_tester")

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

def create_web_testing_agents(use_group_chat: bool = True) -> Union[Tuple[AssistantAgent, AssistantAgent, AssistantAgent, UserProxyAgent, GroupChatManager], 
                                                                  Tuple[AssistantAgent, UserProxyAgent]]:
    """
    Create and initialize web testing agents
    Args:
        use_group_chat: Whether to use GroupChat for better conversation control (default: True)
    Returns:
        If use_group_chat=True:
            Tuple[AssistantAgent, AssistantAgent, AssistantAgent, UserProxyAgent, GroupChatManager]: 
            (testing_agent, debug_agent, admin_agent, user_proxy, manager)
        If use_group_chat=False:
            Tuple[AssistantAgent, UserProxyAgent]: (testing_agent, user_proxy)
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
You focus on writing and executing web tests. When you encounter errors, implement the debug_agent's suggestions before proceeding.

Available Tools:
1. PlaywrightSkill class with methods:
   - start_session(scenario_name: str) -> Initializes browser session
   - navigate(url: str, wait_for_load: bool = True) -> Navigates to URL
   - fill_form(selector: str, value: str) -> Fills form fields
   - click_element(selector: str) -> Clicks elements
   - hover_element(selector: str) -> Hovers over elements
   - verify_element_exists(selector: str) -> Checks element presence
   - verify_text_content(text: str) -> Verifies text on page
   - take_screenshot(name: str, full_page: bool = False) -> Captures page state
   - end_session() -> Closes browser and saves report

Best Practices:
- Always import PlaywrightSkill from autogen_playwright
- Use try/except blocks for each critical step
- Take screenshots after important state changes
- Handle errors gracefully and continue if possible

When receiving debug suggestions:
1. Carefully review the suggested fix
2. Implement ALL suggested changes in your next response
3. Re-run the corrected code
4. If the fix doesn't work, wait for further debug suggestions
5. Only proceed with remaining test steps after successful fix

Important Rules:
- Maximum 5 retries for any action
- After test completion, call end_session() to generate the test report
- Do not generate your own test summary (the report will include one)
- End the conversation after the test report is generated
- Do not acknowledge or respond to further messages""",
        llm_config=llm_config,
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1
    )

    # Create the debugging agent
    debug_agent = AssistantAgent(
        name="debug_agent",
        system_message="""You are a Playwright debugging expert who analyzes and fixes test execution errors.
Your role is to:
1. Analyze error messages and call logs
2. Identify root causes of failures
3. Suggest fixes for common issues:
   - Selector problems
   - Timing/visibility issues
   - Navigation errors
   - Element state issues

When you receive an error:
1. Parse the error message and call log
2. Identify the specific failure point
3. Analyze timing, visibility, and selector issues
4. Suggest specific fixes to the web_tester
5. If needed, recommend timeout or retry adjustments

Common Fixes:
- Adjust selectors for better specificity
- Add waiting conditions for element state
- Modify timeouts for slow operations
- Implement retry logic for flaky actions
- Add visibility checks before interactions

Response Format:
Always structure your response as:
1. ERROR ANALYSIS: Brief analysis of the error
2. ROOT CAUSE: Identified root cause
3. SUGGESTED FIX: Specific code or configuration changes
4. PREVENTION: How to prevent similar issues""",
        llm_config=llm_config,
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1,
    )

    # Create the security admin agent
    admin_agent = UserProxyAgent(
        name="security_admin",
        system_message="""You are a security-focused code reviewer who approves or rejects code execution.
Your primary responsibilities are:
1. Review all code before execution for security risks
2. Check for potentially harmful operations:
   - File system modifications outside test directories
   - Network requests to unauthorized domains
   - System command execution
   - Resource-intensive operations
   - Data exfiltration attempts
3. Verify code adheres to testing scope and purpose

When reviewing code:
1. Analyze all imports and dependencies
2. Check file paths and URLs
3. Verify resource usage (memory, CPU)
4. Look for potential injection vulnerabilities
5. Ensure proper error handling

Response Format:
1. SECURITY ANALYSIS: List potential security concerns
2. SCOPE CHECK: Verify code matches intended purpose
3. DECISION: Either:
   - "APPROVED: {reason}" if code is safe
   - "REJECTED: {specific_issues}" if code needs changes

Important:
- Be strict about security but practical about testing needs
- Provide specific feedback for rejected code
- Consider the context of web testing automation""",
        code_execution_config=False,
        llm_config=llm_config,
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1,
        human_input_mode="NEVER"
    )

    # Create the user proxy agent
    user_proxy = UserProxyAgent(
        name="executor",
        human_input_mode="NEVER",
        code_execution_config={
            "use_docker": False,
            "last_n_messages": 3,
            "work_dir": None
        },
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1
    )

    if use_group_chat:
        # Create a group chat with all agents and custom speaker selection
        groupchat = GroupChat(
            agents=[testing_agent, debug_agent, admin_agent, user_proxy],
            messages=[],
            max_round=15,
            speaker_selection_method=custom_speaker_selection,
            allow_repeat_speaker=False
        )
        
        # Create a manager agent to coordinate the conversation
        manager = GroupChatManager(
            groupchat=groupchat,
            llm_config=llm_config,
            is_termination_msg=is_termination_msg
        )
        return testing_agent, debug_agent, admin_agent, user_proxy, manager
    
    return testing_agent, user_proxy

# Export only the function
__all__ = ['create_web_testing_agents'] 