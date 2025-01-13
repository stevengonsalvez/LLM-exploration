# AutoGen Playwright

An experimental framework exploring automated web testing using Microsoft's AutoGen multi-agent framework combined with Playwright. This project aims to investigate the potential of LLM-powered agents in automated testing scenarios.

## Overview
This project explores the intersection of Large Language Models (LLMs) and automated testing by leveraging AutoGen's multi-agent architecture. The goal is to create more intelligent and adaptable automated tests that can understand test requirements in natural language and translate them into executable test scenarios.

## Features
- **LLM-Powered Test Generation**: Converts natural language test requirements into executable Playwright test scripts
- **Multi-Agent Testing Architecture**:
  - Test Planning Agent: Analyzes requirements and creates test strategies
  - Test Execution Agent: Implements and runs Playwright tests
  - User Proxy Agent: Handles human-in-the-loop interactions when needed
- **Playwright Integration**: 
  - Full browser automation support
  - Cross-browser testing capabilities
  - Network interception and mocking
- **Advanced Reporting**:
  - Detailed test execution logs
  - Automatic screenshot capture on failures
  - Markdown report generation with visual evidence
  - AgentOps integration for monitoring agent interactions
- **Flexible Configuration**:
  - Customizable LLM providers
  - Configurable browser settings
  - Environment-based configuration

## Installation
```bash
pip install -e .
```

## Prerequisites
- Python 3.9 or higher
- OpenAI API key or other supported LLM provider
- AgentOps API key (optional, for monitoring)

## Quick Start
```python
from autogen_playwright import testing_agent, user_proxy, PlaywrightSkill

def run_test():
    # Initialize the test scenario
    chat_result = user_proxy.initiate_chat(
        testing_agent,
        message="""
        Test Scenario: Verify user login flow
        1. Navigate to login page
        2. Enter valid credentials
        3. Verify successful login
        """
    )
```

## Configuration
Create a `.env` file in your project root:
```
# LLM Configuration
OPENAI_API_KEY=your_api_key
MODEL_NAME=gpt-4

# Playwright Settings
BROWSER_TYPE=chromium
HEADLESS=true

# Monitoring
AGENTOPS_API_KEY=your_api_key
```

## LLM Caching
The framework implements disk-based caching for LLM responses to optimize costs and improve response times:

### Cache Configuration
- **Enable/Disable**: Set via `LLM_CACHE_ENABLE` (defaults to true)
- **Cache Location**: Configured through `LLM_CACHE_PATH` (defaults to '/tmp/autogen-playwright-cache')
- **Cache Seeding**: Optional cache seed via `LLM_CACHE_SEED` for reproducible results

### What Gets Cached
- All LLM interactions including:
  - Test planning conversations
  - Test step generation
  - Response analysis
  - Error handling decisions

### Cache Behavior
- **Cache Keys**: Generated based on the conversation context and prompt
- **Hit/Miss Logging**: All cache interactions are logged for monitoring
- **Persistence**: Cache files are stored on disk and persist between runs
- **Cost Savings**: Repeated test scenarios reuse cached responses

### Monitoring Cache Performance
The framework includes built-in cache analytics:
```python
from autogen_playwright.ops import print_session_summary

# Get cache hit rates and token usage
stats = print_session_summary(session_id="your_session_id")
```

## Project Goals
1. **Explore AutoGen Capabilities**: Investigate how AutoGen's multi-agent system can be applied to web testing
2. **Natural Language Testing**: Enable test creation and maintenance using natural language
3. **Intelligent Test Maintenance**: Leverage LLMs for test adaptation and self-healing
4. **Best Practices Integration**: Combine AI capabilities with established testing practices

## Current Limitations & Areas of Exploration
- LLM context handling for complex test scenarios
- Test stability and reproducibility
- Cost-effectiveness of LLM-based testing
- Integration with existing test frameworks
- Performance optimization

## Contributing
This is an experimental project and contributions are welcome. Please feel free to submit issues and pull requests.

## License
MIT License 