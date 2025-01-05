from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    """Base configuration for LLM providers."""
    model_name: str = Field(..., description="Name of the model to use")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    streaming: bool = Field(False, description="Whether to stream the response")
    additional_kwargs: Dict[str, Any] = Field(default_factory=dict, description="Additional provider-specific parameters")

class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._validate_config()
        self._initialize()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration."""
        pass
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the LLM provider."""
        pass
    
    @abstractmethod
    async def generate(self, 
                      prompt: str, 
                      system_message: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> str:
        """Generate text from the LLM."""
        pass
    
    @abstractmethod
    async def generate_stream(self,
                            prompt: str,
                            system_message: Optional[str] = None,
                            temperature: Optional[float] = None,
                            max_tokens: Optional[int] = None):
        """Stream text generation from the LLM."""
        pass
    
    @abstractmethod
    async def batch_generate(self,
                           prompts: List[str],
                           system_message: Optional[str] = None,
                           temperature: Optional[float] = None,
                           max_tokens: Optional[int] = None) -> List[str]:
        """Generate multiple responses in parallel."""
        pass 