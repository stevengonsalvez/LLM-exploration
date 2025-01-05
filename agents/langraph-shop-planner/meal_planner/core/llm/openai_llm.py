from typing import Any, Dict, List, Optional
import openai
from openai import AsyncOpenAI
from .base import BaseLLM, LLMConfig

class OpenAIConfig(LLMConfig):
    """OpenAI-specific configuration."""
    api_key: str
    organization: Optional[str] = None

class OpenAILLM(BaseLLM):
    """OpenAI implementation of the LLM interface."""
    
    def _validate_config(self) -> None:
        if not isinstance(self.config, OpenAIConfig):
            raise ValueError("Config must be an instance of OpenAIConfig")
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
    
    def _initialize(self) -> None:
        self.client = AsyncOpenAI(
            api_key=self.config.api_key,
            organization=self.config.organization
        )
    
    async def generate(self,
                      prompt: str,
                      system_message: Optional[str] = None,
                      temperature: Optional[float] = None,
                      max_tokens: Optional[int] = None) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            **self.config.additional_kwargs
        )
        return response.choices[0].message.content
    
    async def generate_stream(self,
                            prompt: str,
                            system_message: Optional[str] = None,
                            temperature: Optional[float] = None,
                            max_tokens: Optional[int] = None):
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        stream = await self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
            stream=True,
            **self.config.additional_kwargs
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    
    async def batch_generate(self,
                           prompts: List[str],
                           system_message: Optional[str] = None,
                           temperature: Optional[float] = None,
                           max_tokens: Optional[int] = None) -> List[str]:
        responses = []
        for prompt in prompts:
            response = await self.generate(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens
            )
            responses.append(response)
        return responses 