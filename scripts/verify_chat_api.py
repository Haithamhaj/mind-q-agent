
import requests
import sys
import json

# Config
PORT = 8781
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1/chat"

# We know qwen2.5:3b is installed
MODEL = "qwen2.5:3b"

def run_tests():
    print(f"Running tests against {BASE_URL}...")
    
    # 1. Non-Streaming Chat
    print(f"Sending chat request (model={MODEL})...")
    try:
        payload = {
            "message": "What is Mind-Q? Please correspond.",
            "model": MODEL,
            "provider": "ollama",
            "stream": False
        }
        r = requests.post(BASE_URL, json=payload, timeout=60) # Long timeout for LLM
        
        if r.status_code == 200:
            data = r.json()
            print("[PASS] Chat API response received")
            print(f"Response: {data.get('response', '')[:100]}...")
            
            if data.get("context_used"):
                print("[PASS] Context usage flag is True")
            else:
                print("[WARN] Context usage flag is False (Check ContextBuilder)")
                
        else:
            print(f"[FAIL] Chat API error: {r.status_code} {r.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Chat Request exception: {e}")
        return False

    return True

if __name__ == "__main__":
    if run_tests():
        print("\n✅ Chat Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ Chat Verification FAILED")
        sys.exit(1)
