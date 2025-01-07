from typing import Dict, Optional, Any
import os
from dataclasses import dataclass

@dataclass
class LLMConfig:
    provider: str
    api_key: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    request_timeout: int = 600
    cache_seed: Optional[int] = None
    cache_enable: bool = True
    cache_path: Optional[str] = None
    max_consecutive_empty: int = 3  # Maximum number of consecutive empty exchanges allowed
    max_total_tokens: Optional[int] = None  # Maximum total tokens for the entire conversation, None for no limit
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable must be set")
            
        # Get max_total_tokens from env, default to None if not set
        max_total_tokens_str = os.getenv('LLM_MAX_TOTAL_TOKENS')
        max_total_tokens = int(max_total_tokens_str) if max_total_tokens_str else None
            
        return cls(
            provider=os.getenv('LLM_PROVIDER', 'openai'),
            api_key=api_key,
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS')) if os.getenv('LLM_MAX_TOKENS') else 4000,
            request_timeout=int(os.getenv('LLM_REQUEST_TIMEOUT', '600')),
            cache_seed=int(os.getenv('LLM_CACHE_SEED')) if os.getenv('LLM_CACHE_SEED') else None,
            cache_enable=os.getenv('LLM_CACHE_ENABLE', 'true').lower() == 'true',
            cache_path=os.getenv('LLM_CACHE_PATH', '/tmp/autogen-playwright-cache'),
            max_consecutive_empty=int(os.getenv('LLM_MAX_CONSECUTIVE_EMPTY', '3')),
            max_total_tokens=max_total_tokens
        )