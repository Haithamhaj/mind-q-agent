
import sys
import logging
from mind_q_agent.rag.context import ContextBuilder

# Configure logging to see errors if any
logging.basicConfig(level=logging.INFO)

def test_rag_context():
    print("Testing ContextBuilder...")
    
    try:
        builder = ContextBuilder()
        print("[PASS] ContextBuilder initialized")
    except Exception as e:
        print(f"[FAIL] Init failed: {e}")
        return False
        
    query = "Mind-Q"
    print(f"Building prompt for query: '{query}'...")
    
    try:
        prompt = builder.build_system_prompt(query)
        print("--- Generated Prompt ---")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("------------------------")
        
        if "You are Mind-Q" in prompt:
            print("[PASS] System prompt contains persona")
        else:
             print("[FAIL] System prompt missing persona")
             return False
             
        if "RETRIEVED DOCUMENTS" in prompt or "No specific documents" in prompt:
            print("[PASS] Context section present")
        else:
             print("[FAIL] Context section missing")
             return False
             
    except Exception as e:
        print(f"[FAIL] Build prompt failed: {e}")
        return False

    return True

if __name__ == "__main__":
    if test_rag_context():
        print("\n✅ RAG Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ RAG Verification FAILED")
        sys.exit(1)
