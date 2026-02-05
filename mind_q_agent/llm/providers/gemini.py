import logging
import os
from typing import AsyncGenerator, Optional
import google.generativeai as genai
from mind_q_agent.llm import LLMProvider, ModelConfig

logger = logging.getLogger(__name__)

class GeminiProvider(LLMProvider):
    """
    Provider for Google Gemini API.
    """

    def __init__(self, config: ModelConfig):
        self.config = config
        api_key = config.api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API Key is missing. Set GEMINI_API_KEY env or pass in config.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.model_name)

    def get_provider_name(self) -> str:
        return "gemini"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        # Gemini handles system instructions in model config or prompt engineering
        # For simplicity, we prepend system prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        try:
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generate failed: {e}")
            raise

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        full_prompt = prompt
        if system_prompt:
             full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"

        try:
            response = await self.model.generate_content_async(
                full_prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Gemini stream failed: {e}")
            raise
    
    async def close(self):
        # Gemini client doesn't require explicit close
        pass
