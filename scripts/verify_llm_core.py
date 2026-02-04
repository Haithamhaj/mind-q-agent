
import sys
import asyncio
from typing import AsyncGenerator, Optional
from mind_q_agent.llm import LLMProvider, ModelConfig, LLMSettings

# 1. Test Config Model
try:
    config = ModelConfig(
        provider="ollama", 
        model_name="llama3"
    )
    print(f"[PASS] ModelConfig created: {config.provider}/{config.model_name}")
except Exception as e:
    print(f"[FAIL] ModelConfig creation failed: {e}")
    sys.exit(1)

# 2. Test Interface Implementation
class MockProvider(LLMProvider):
    def get_provider_name(self) -> str:
        return "mock"
        
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return f"Mock response to: {prompt}"
        
    async def stream(self, prompt: str, system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        yield "Mock "
        yield "stream"

async def test_provider():
    provider = MockProvider()
    
    # Test Generate
    res = await provider.generate("hello")
    if res == "Mock response to: hello":
        print("[PASS] LLMProvider generate() contract valid")
    else:
        print(f"[FAIL] generate() returned: {res}")
        sys.exit(1)
        
    # Test Stream
    chunks = []
    async for chunk in provider.stream("hello"):
        chunks.append(chunk)
    
    if "".join(chunks) == "Mock stream":
         print("[PASS] LLMProvider stream() contract valid")
    else:
         print(f"[FAIL] stream() returned: {chunks}")
         sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_provider())
    print("✅ LLM Core Verification SUCCESSFUL")
