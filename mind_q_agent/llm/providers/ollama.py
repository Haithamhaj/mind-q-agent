import httpx
import json
import logging
from typing import AsyncGenerator, Optional
from mind_q_agent.llm import LLMProvider, ModelConfig

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """
    Provider for local Ollama instances.
    Default URL: http://localhost:11434
    """
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.base_url = config.api_base or "http://localhost:11434"
        self.client = httpx.AsyncClient(timeout=60.0) # Increased timeout for LLM gen

    def get_provider_name(self) -> str:
        return "ollama"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate complete response from Ollama.
        """
        url = f"{self.base_url}/api/generate"
        
        # Prepare payload
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens or 2048
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
            
        except httpx.ConnectError:
            logger.error(f"Failed to connect to Ollama at {self.base_url}. Is it running?")
            raise RuntimeError("Ollama connection failed")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Stream response from Ollama.
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.config.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens or 2048
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            async with self.client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
                        
        except httpx.ConnectError:
            logger.error(f"Failed to connect to Ollama at {self.base_url}")
            raise RuntimeError("Ollama connection failed")
        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise

    async def close(self):
        await self.client.aclose()
