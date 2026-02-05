import asyncio
import os
from mind_q_agent.llm.config import ModelConfig
from mind_q_agent.llm.providers.llamacpp import LlamaCppProvider

async def main():
    print("Testing LlamaCpp Provider...")
    
    # Ensure model path is set
    model_path = os.getenv("LLAMACPP_MODEL_PATH", "./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf")
    print(f"Target Model Path: {model_path}")
    
    if not os.path.exists(model_path):
        print(f"WARNING: Model file not found at {model_path}")
        print("Please download a GGUF model and place it there, or set LLAMACPP_MODEL_PATH.")
        return

    config = ModelConfig(
        provider="llamacpp",
        model_name="local-model",
        temperature=0.7,
        max_tokens=100
    )

    try:
        provider = LlamaCppProvider(config)
        
        prompt = "Hello! Who are you?"
        print(f"\nUser: {prompt}")
        
        response = await provider.generate(prompt)
        print(f"AI: {response}")
        
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
