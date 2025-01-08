import os
import logging
from typing import Dict, Any, Optional
from .config import LLMConfig
from autogen import Cache

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class LoggedCache(Cache):
    """Cache implementation that logs hits and misses"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    def get(self, key: str) -> Optional[Dict]:
        result = super().get(key)
        if result is not None:
            self.logger.info(f"Cache HIT for key: {key[:50]}...")
        else:
            self.logger.info(f"Cache MISS for key: {key[:50]}...")
        return result

    def put(self, key: str, value: Dict):
        self.logger.info(f"Caching response for key: {key[:50]}...")
        return super().put(key, value)

class LLMProvider:
    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()
        self._set_provider_env_vars()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing LLM with provider: {self.config.provider}, model: {self.config.model}")
        
    def _set_provider_env_vars(self):
        """Map LLM_API_KEY to provider-specific environment variables"""
        provider_env_mapping = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'azure': 'AZURE_OPENAI_API_KEY',
            'cerebras': 'CEREBRAS_API_KEY'
        }
        
        if env_var := provider_env_mapping.get(self.config.provider):
            os.environ[env_var] = self.config.api_key
    
    def get_config(self) -> Dict[str, Any]:
        base_config = {
            "temperature": self.config.temperature,
            "timeout": self.config.request_timeout
        }
        
        if self.config.cache_enable:
            cache_kwargs = {}
            if self.config.cache_path:
                cache_kwargs['cache_path_root'] = self.config.cache_path
                self.logger.info(f"Using cache path: {self.config.cache_path}")
            base_config["cache"] = LoggedCache.disk(**cache_kwargs)
            if self.config.cache_seed is not None:
                base_config["cache_seed"] = self.config.cache_seed
                self.logger.info(f"Using cache seed: {self.config.cache_seed}")
        else:
            self.logger.warning("Cache is disabled!")
        
        if self.config.max_tokens:
            base_config["max_tokens"] = self.config.max_tokens
            
        provider_specific = {
            "openai": {
                "model": self.config.model,
            },
            "anthropic": {
                "model": self.config.model,
                "timeout": self.config.request_timeout,
            },
            "azure": {
                "deployment_name": self.config.model,
                "timeout": self.config.request_timeout,
            },
            "cerebras": {
                "model": self.config.model,
                "api_type": "cerebras",
                "timeout": self.config.request_timeout,
            }
        }
        
        return {**base_config, **provider_specific.get(self.config.provider, {})}