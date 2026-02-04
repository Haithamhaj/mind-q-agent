import logging
import os
from typing import AsyncGenerator, Optional
import openai
from mind_q_agent.llm import LLMProvider, ModelConfig

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """
    Provider for OpenAI API (and compatible APIs like Groq, DeepSeek).
    """

    def __init__(self, config: ModelConfig):
        self.config = config
        api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API Key is missing. Set OPENAI_API_KEY env or pass in config.")
        
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=config.api_base # Optional support for custom base URL
        )

    def get_provider_name(self) -> str:
        return "openai"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 2048,
                stream=False
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI generate failed: {e}")
            raise

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        messages = []
        if system_prompt:
             messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens or 2048,
                stream=True
            )
            
            async for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
                    
        except Exception as e:
            logger.error(f"OpenAI stream failed: {e}")
            raise

    async def close(self):
        await self.client.close()
