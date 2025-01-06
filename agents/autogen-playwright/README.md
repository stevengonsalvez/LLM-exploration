# AutoGen Playwright

A framework for automated web testing using AutoGen agents and Playwright.

## Features
- Automated web testing using LLM-powered agents
- Playwright for browser automation
- Detailed test reporting with screenshots
- AgentOps integration for monitoring
- Markdown report generation

## Installation
```bash
pip install -e .
```

## Usage
```python
from autogen_playwright import testing_agent, user_proxy, PlaywrightSkill

def run_test():
    chat_result = user_proxy.initiate_chat(
        testing_agent,
        message="""
        Execute web test scenario...
        """
    )
```

## Configuration
Set up your environment variables in `.env`:
- LLM configuration (OpenAI, etc.)
- Playwright settings
- AgentOps API key 