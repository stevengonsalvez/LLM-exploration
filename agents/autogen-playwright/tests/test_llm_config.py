import os
import pytest
from autogen_playwright.llm.config import LLMConfig
from autogen_playwright.llm.provider import LLMProvider

def test_llm_config_from_env():
    os.environ['LLM_PROVIDER'] = 'anthropic'
    os.environ['LLM_API_KEY'] = 'test-key'
    os.environ['LLM_MODEL'] = 'claude-2'
    os.environ['LLM_TEMPERATURE'] = '0.8'
    
    config = LLMConfig.from_env()
    assert config.provider == 'anthropic'
    assert config.api_key == 'test-key'
    assert config.model == 'claude-2'
    assert config.temperature == 0.8

def test_llm_provider_config_generation():
    config = LLMConfig(
        provider='openai',
        api_key='test-key',
        model='gpt-4',
        temperature=0.7
    )
    
    provider = LLMProvider(config)
    llm_config = provider.get_config()
    
    assert llm_config['temperature'] == 0.7
    assert llm_config['api_key'] == 'test-key'
    assert llm_config['model'] == 'gpt-4' 