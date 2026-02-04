
import requests
import sys
import json

# Config
PORT = 8775
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1/preferences"

def run_tests():
    print(f"Running tests against {BASE_URL}...")
    
    # 1. Update Preference
    try:
        payload = {"theme": "dark", "language": "en"}
        r = requests.patch(BASE_URL, json=payload)
        assert r.status_code == 200
        data = r.json()
        if data.get("theme") == "dark" and data.get("language") == "en":
            print("[PASS] Update Preferences")
        else:
            print(f"[FAIL] Update Preferences: {data}")
            return False
    except Exception as e:
        print(f"[FAIL] Update Preferences: {e}")
        return False

    # 2. Get Preferences
    try:
        r = requests.get(BASE_URL)
        assert r.status_code == 200
        data = r.json()
        if data.get("theme") == "dark":
            print("[PASS] Get Preferences")
        else:
            print(f"[FAIL] Get Preferences: {data}")
            return False
    except Exception as e:
        print(f"[FAIL] Get Preferences: {e}")
        return False

    return True

if __name__ == "__main__":
    if run_tests():
        print("\n✅ Preferences Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ Preferences Verification FAILED")
        sys.exit(1)
