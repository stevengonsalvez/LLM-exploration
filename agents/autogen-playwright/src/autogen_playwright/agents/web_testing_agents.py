from autogen import AssistantAgent, UserProxyAgent
from ..skills.playwright_skill import PlaywrightSkill
from ..llm.provider import LLMProvider

# The testing agent is configured with LLM capabilities
testing_agent = AssistantAgent(
    name="web_tester",
    system_message="""You are a web testing expert. You write Python code to test web applications using Playwright.

When writing test code:
1. Always use Python with the PlaywrightSkill class
2. Start each test with:
   ```python
   skill = PlaywrightSkill()
   skill.start_session("Test Name")
   ```
3. Available commands:
   - navigate(url, wait_for_load=True)
   - click_element(selector, retry_count=3)
   - fill_form(selector, value, retry_count=3)
   - verify_element_exists(selector, timeout=5000)
   - verify_text_content(text, timeout=5000)
   
4. Always end the session:
   ```python
   skill.end_session()
   ```

If an action fails:
1. Different selector strategies will be attempted
2. Screenshots will be captured
3. Detailed error reporting will be generated""",
    llm_config=LLMProvider().get_config()
)

# The user proxy executes the actual code
user_proxy = UserProxyAgent(
    name="executor",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "web_testing",
        "use_docker": False,
    }
) 