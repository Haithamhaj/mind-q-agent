from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, AsyncGenerator
from fastapi.responses import StreamingResponse

import logging
from mind_q_agent.rag.context import ContextBuilder
from mind_q_agent.llm.config import ModelConfig

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

logger = logging.getLogger(__name__)

# Request Model
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "llama3" # Default model
    provider: Optional[str] = "ollama"
    temperature: Optional[float] = 0.7
    stream: bool = False

# Response Model (non-streaming)
class ChatResponse(BaseModel):
    response: str
    context_used: bool = True
    sources: List[str] = []

# Dependency (Singleton-like)
from mind_q_agent.llm.providers.ollama import OllamaProvider
from mind_q_agent.llm.providers.openai import OpenAIProvider
from mind_q_agent.llm.providers.gemini import GeminiProvider
from mind_q_agent.llm.providers.llamacpp import LlamaCppProvider

# Dependency (Singleton-like)
class ChatService:
    def __init__(self):
        self.context_builder = ContextBuilder()
    
    def _get_provider(self, provider_name: str, config: ModelConfig):
        if provider_name == "ollama":
            return OllamaProvider(config)
        elif provider_name == "openai":
            return OpenAIProvider(config)
        elif provider_name == "gemini":
            return GeminiProvider(config)
        elif provider_name == "llamacpp":
            return LlamaCppProvider(config)
        else:
             raise ValueError(f"Provider {provider_name} not supported")
        
    async def get_response(self, req: ChatRequest):
        # 1. Build Context
        system_prompt = self.context_builder.build_system_prompt(req.message)
        
        # 2. Init Provider
        config = ModelConfig(
            provider=req.provider,
            model_name=req.model,
            temperature=req.temperature
        )
        
        provider = self._get_provider(req.provider, config)
            
        try:
            if req.stream:
                return provider.stream(req.message, system_prompt=system_prompt)
            else:
                response_text = await provider.generate(req.message, system_prompt=system_prompt)
                return ChatResponse(response=response_text)
        finally:
             if not req.stream:
                 await provider.close()

# Initialize Service
try:
    chat_service = ChatService()
except Exception as e:
    logger.error(f"Failed to init ChatService: {e}")
    chat_service = None

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Chat with Mind-Q (RAG enabled).
    """
    if not chat_service:
        raise HTTPException(status_code=500, detail="Chat service not initialized")
        
    try:
        # For non-streaming, we return JSON
        if not req.stream:
            return await chat_service.get_response(req)
        
        # For streaming, we need a StreamingResponse
        else:
            # We need to manage the provider lifecycle differently for streaming
            # Re-creating provider logic here for simplicity of generator
            
            async def event_generator():
                # 1. Context
                system_prompt = chat_service.context_builder.build_system_prompt(req.message)
                
                # 2. Provider
                config = ModelConfig(
                    provider=req.provider,
                    model_name=req.model,
                    temperature=req.temperature
                )
                
                # Use the new factory method (conceptually, though _get_provider is instance method)
                # Ideally ChatService should expose a get_provider method publically or we duplicate logic for now (KISS)
                if req.provider == "ollama":
                     provider = OllamaProvider(config)
                elif req.provider == "openai":
                     provider = OpenAIProvider(config)
                elif req.provider == "gemini":
                     provider = GeminiProvider(config)
                elif req.provider == "llamacpp":
                     provider = LlamaCppProvider(config)
                else:
                     raise ValueError(f"Provider {req.provider} not supported")
                
                try:
                    async for chunk in provider.stream(req.message, system_prompt=system_prompt):
                        yield chunk
                finally:
                    await provider.close()

            return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
