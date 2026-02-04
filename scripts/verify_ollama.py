
import sys
import asyncio
import httpx
from mind_q_agent.llm import ModelConfig
from mind_q_agent.llm.providers.ollama import OllamaProvider

async def test_ollama():
    print("Testing Ollama Connection...")
    
    # 1. Check if Ollama is running
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://localhost:11434")
            if resp.status_code == 200:
                print("[PASS] Ollama server is reachable")
            else:
                print(f"[FAIL] Ollama server returned {resp.status_code}")
                return False
    except Exception as e:
        print(f"[FAIL] Could not connect to Ollama: {e}")
        print("💡 Tip: proper installation required. Run 'ollama serve' in a separate terminal.")
        return False

    # 2. Test Generation (assuming 'llama3.2' or 'llama3' or 'tinyllama' exists)
    # We will try a few common model names
    models_to_try = ["qwen2.5:3b", "llama3.2", "llama3", "mistral", "tinyllama", "gemma:2b"]
    
    provider = None
    working_model = None

    for model in models_to_try:
        print(f"Trying model: {model}...")
        config = ModelConfig(provider="ollama", model_name=model)
        prov = OllamaProvider(config)
        try:
            # Simple ping generation
            res = await prov.generate("Say 'pass'", system_prompt="You are a test bot.")
            print(f"[PASS] Generation successful with model '{model}'")
            print(f"      Response: {res.strip()}")
            provider = prov
            working_model = model
            break
        except Exception as e:
            if "not found" in str(e) or "pull" in str(e):
                print(f"      Model '{model}' not found or failed.")
            else:
                 print(f"      Error: {e}")
            await prov.close()
    
    if not provider:
        print("[FAIL] Could not generate with any common model.")
        print("💡 Tip: Run 'ollama pull llama3' or check your installed models with 'ollama list'.")
        return False

    # 3. Test Streaming
    print(f"Testing Streaming with {working_model}...")
    try:
        print("Stream: ", end="", flush=True)
        async for chunk in provider.stream("Count to 3"):
            print(chunk, end="", flush=True)
        print("\n[PASS] Streaming successful")
    except Exception as e:
        print(f"\n[FAIL] Streaming failed: {e}")
        return False
    finally:
        await provider.close()

    return True

if __name__ == "__main__":
    if asyncio.run(test_ollama()):
        print("\n✅ Ollama Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ Ollama Verification FAILED")
        sys.exit(1)
