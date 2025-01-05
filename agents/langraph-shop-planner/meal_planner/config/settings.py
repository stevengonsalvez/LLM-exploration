import os
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(0.7, env="OPENAI_TEMPERATURE")
    
    # Application Settings
    min_meals_per_day: int = Field(3, env="MIN_MEALS_PER_DAY")
    max_meals_per_day: int = Field(5, env="MAX_MEALS_PER_DAY")
    expiry_warning_days: int = Field(7, env="EXPIRY_WARNING_DAYS")
    confidence_threshold: float = Field(0.8, env="CONFIDENCE_THRESHOLD")
    
    # Storage Settings
    upload_dir: str = Field("uploads", env="UPLOAD_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration."""
        return {
            "api_key": self.openai_api_key,
            "model_name": self.openai_model,
            "temperature": self.openai_temperature
        }
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        os.makedirs(self.upload_dir, exist_ok=True)

# Global settings instance
settings = Settings() 