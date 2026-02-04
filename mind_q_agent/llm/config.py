from pydantic import BaseModel, Field
from typing import Optional, Dict

class ModelConfig(BaseModel):
    """
    Configuration for an LLM Model.
    """
    provider: str = Field(..., description="Provider name (ollama, openai, etc)")
    model_name: str = Field(..., description="Specific model identifier (e.g. llama3, gpt-4)")
    api_key: Optional[str] = Field(None, description="API Key for cloud providers")
    api_base: Optional[str] = Field(None, description="Base URL for API (e.g. custom Ollama host)")
    temperature: float = Field(0.7, description="Randomness of output")
    max_tokens: int = Field(2048, description="Maximum tokens to generate")
    
    class Config:
        env_prefix = "LLM_" 

class LLMSettings(BaseModel):
    """
    Global LLM Settings.
    """
    default_model: ModelConfig
    fallback_model: Optional[ModelConfig] = None
