
import requests
import sys
import json

# Config
PORT = 8777
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1/graph"

def run_tests():
    print(f"Running tests against {BASE_URL}...")
    
    # 1. Analytics Endpoint
    try:
        r = requests.get(f"{BASE_URL}/analytics")
        assert r.status_code == 200
        data = r.json()
        
        print("[INFO] Analytics Data:")
        print(json.dumps(data, indent=2))
        
        if "summary" in data and "top_concepts" in data:
            print("[PASS] Analytics Structure Valid")
        else:
            print("[FAIL] Analytics Structure Invalid")
            return False
            
    except Exception as e:
        print(f"[FAIL] Analytics: {e}")
        return False

    return True

if __name__ == "__main__":
    if run_tests():
        print("\n✅ Analytics Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ Analytics Verification FAILED")
        sys.exit(1)
