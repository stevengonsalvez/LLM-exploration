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
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable must be set")
            
        return cls(
            provider=os.getenv('LLM_PROVIDER', 'openai'),
            api_key=api_key,
            model=os.getenv('LLM_MODEL', 'gpt-4'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS')) if os.getenv('LLM_MAX_TOKENS') else None,
            request_timeout=int(os.getenv('LLM_REQUEST_TIMEOUT', '600'))
        ) 