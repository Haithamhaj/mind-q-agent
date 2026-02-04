
import requests
import sys
import json

# Config
PORT = 8779
BASE_URL = f"http://127.0.0.1:{PORT}"

def run_tests():
    print(f"Running tests against {BASE_URL}...")
    
    # 1. Get OpenAPI JSON
    try:
        r = requests.get(f"{BASE_URL}/api/v1/openapi.json")
        assert r.status_code == 200
        schema = r.json()
        
        # Check basic structure
        if "openapi" in schema and "paths" in schema:
            print("[PASS] Fetch OpenAPI JSON")
        else:
            print("[FAIL] Invalid OpenAPI JSON")
            return False
            
        # Check Operation IDs (should be tag-name style)
        # e.g. "documents-upload_document"
        paths = schema["paths"]
        
        has_custom_ids = False
        for path, methods in paths.items():
            for method, op in methods.items():
                op_id = op.get("operationId", "")
                if "-" in op_id:
                    has_custom_ids = True
                    break
            if has_custom_ids:
                break
        
        if has_custom_ids:
             print("[PASS] Custom Operation IDs found (n8n friendly)")
        else:
             print("[WARN] Custom Operation IDs NOT found")
             
    except Exception as e:
        print(f"[FAIL] Fetch OpenAPI: {e}")
        return False

    return True

if __name__ == "__main__":
    if run_tests():
        print("\n✅ OpenAPI Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ OpenAPI Verification FAILED")
        sys.exit(1)
