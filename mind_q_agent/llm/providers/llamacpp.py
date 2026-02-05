from typing import AsyncGenerator, Optional, Dict, Any
from mind_q_agent.llm.provider import LLMProvider
from mind_q_agent.llm.config import ModelConfig
from mind_q_agent.api.settings import settings
import logging

logger = logging.getLogger(__name__)

class LlamaCppProvider(LLMProvider):
    """
    Local LLM provider using llama-cpp-python for GGUF models.
    """
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model_path = settings.LLAMACPP_MODEL_PATH
        self.n_ctx = settings.LLAMACPP_N_CTX
        self.n_gpu_layers = settings.LLAMACPP_N_GPU_LAYERS
        self.llm = None
        self._initialize_model()

    def _initialize_model(self):
        try:
            from llama_cpp import Llama
            logger.info(f"Initializing LlamaCpp model from: {self.model_path}")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            logger.info("LlamaCpp model initialized successfully.")
        except ImportError:
            logger.error("llama-cpp-python is not installed. Please install it with `pip install llama-cpp-python`.")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize LlamaCpp model: {e}")
            self.llm = None

    def get_provider_name(self) -> str:
        return "llamacpp"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        if not self.llm:
            raise RuntimeError("LlamaCpp model is not initialized.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.llm.create_chat_completion(
                messages=messages,
                stream=False,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LlamaCpp generation failed: {e}")
            raise

    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        if not self.llm:
            raise RuntimeError("LlamaCpp model is not initialized.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        try:
            stream_response = self.llm.create_chat_completion(
                messages=messages,
                stream=True,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            for chunk in stream_response:
                if "content" in chunk["choices"][0]["delta"]:
                    yield chunk["choices"][0]["delta"]["content"]
                    
        except Exception as e:
            logger.error(f"LlamaCpp streaming failed: {e}")
            raise
