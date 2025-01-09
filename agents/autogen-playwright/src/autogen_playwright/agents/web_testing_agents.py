from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager, Agent
import logging
import json
import re
from typing import Optional, List, Dict, Any, Tuple, Union
from ..skills.playwright_skill import PlaywrightSkill
from ..llm.provider import LLMProvider
from ..prompts import WEB_TESTER_PROMPT, DEBUG_AGENT_PROMPT, SECURITY_ADMIN_PROMPT

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
        system_message=WEB_TESTER_PROMPT,
        llm_config=llm_config,
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1
    )

    # Create the debugging agent
    debug_agent = AssistantAgent(
        name="debug_agent",
        system_message=DEBUG_AGENT_PROMPT,
        llm_config=llm_config,
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=1,
    )

    # Create the security admin agent
    admin_agent = UserProxyAgent(
        name="security_admin",
        system_message=SECURITY_ADMIN_PROMPT,
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