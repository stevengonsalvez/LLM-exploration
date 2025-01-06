import os
from typing import Dict, Any, Optional
from .config import LLMConfig

class LLMProvider:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()
        self._set_provider_env_vars()
        
    def _set_provider_env_vars(self):
        """Map LLM_API_KEY to provider-specific environment variables"""
        provider_env_mapping = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'azure': 'AZURE_OPENAI_API_KEY'
        }
        
        if env_var := provider_env_mapping.get(self.config.provider):
            os.environ[env_var] = self.config.api_key
    
    def get_config(self) -> Dict[str, Any]:
        base_config = {
            "temperature": self.config.temperature,
        }
        
        if self.config.max_tokens:
            base_config["max_tokens"] = self.config.max_tokens
            
        provider_specific = {
            "openai": {
                "model": self.config.model,
                "timeout": self.config.request_timeout,
            },
            "anthropic": {
                "model": self.config.model,
                "timeout": self.config.request_timeout,
            },
            "azure": {
                "deployment_name": self.config.model,
                "timeout": self.config.request_timeout,
            }
        }
        
        return {**base_config, **provider_specific.get(self.config.provider, {})} 