from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional, Dict, Any, List

class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers (Ollama, OpenAI, etc.)
    Ensures a consistent interface for the rest of the application.
    """

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a complete response for the given prompt.
        """
        pass

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        """
        Stream response chunks for the given prompt.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the unique name of the provider (e.g. 'ollama', 'openai').
        """
        pass
