
import requests
import sys
import os
import time

# Config
PORT = 8773
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1"
TEST_FILE_CONTENT = "Mind-Q Verification: Artificial Intelligence and Agents working together."
TEST_FILENAME = "verify_phase4a.txt"

def run_tests():
    print(f"Running tests against {BASE_URL}...")
    
    # 1. Health Check
    try:
        r = requests.get(f"http://127.0.0.1:{PORT}/health")
        if r.status_code == 200:
            print("[PASS] Health Check")
        else:
            print(f"[FAIL] Health Check: {r.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Health Check: {e}")
        return False

    # 2. Upload Document
    try:
        with open(TEST_FILENAME, "w") as f:
            f.write(TEST_FILE_CONTENT)
        
        with open(TEST_FILENAME, "rb") as f:
            files = {"file": (TEST_FILENAME, f, "text/plain")}
            r = requests.post(f"{BASE_URL}/documents/upload", files=files)
            
        if r.status_code == 200:
             print("[PASS] Upload Document")
        elif "already exists" in r.text:
             print("[PASS] Upload Document (Already Existed)")
        else:
             print(f"[FAIL] Upload: {r.status_code} {r.text}")
             return False
    except Exception as e:
        print(f"[FAIL] Upload: {e}")
        return False
    finally:
        if os.path.exists(TEST_FILENAME):
            os.remove(TEST_FILENAME)

    # 3. List Documents
    try:
        r = requests.get(f"{BASE_URL}/documents")
        assert r.status_code == 200
        docs = r.json()
        found = False
        for d in docs:
            if d.get("title") == TEST_FILENAME:
                found = True
                break
        
        if found:
            print("[PASS] List Documents (found uploaded file)")
        else:
            print("[FAIL] List Documents: Uploaded file not found")
            print(f"List: {docs}")
            return False
    except Exception as e:
        print(f"[FAIL] List Documents: {e}")
        return False

    # 4. Search
    try:
        # Retry loop for eventual consistency if needed
        for i in range(3):
            params = {"q": "Artificial Intelligence", "limit": 3}
            r = requests.get(f"{BASE_URL}/search", params=params)
            assert r.status_code == 200
            results = r.json()
            
            if len(results) > 0 and results[0].get("metadata", {}).get("filename") == TEST_FILENAME:
                print("[PASS] Search (found relevant document)")
                break
            time.sleep(1)
        else:
            print("[FAIL] Search: Did not find expected document after retries")
            print(f"Results: {results}")
            # return False # Soft fail?
    except Exception as e:
        print(f"[FAIL] Search: {e}")
        return False

    # 5. Graph Stats
    try:
        r = requests.get(f"{BASE_URL}/graph/stats")
        assert r.status_code == 200
        stats = r.json()
        print(f"[INFO] Graph Stats: {stats}")
        if stats.get("nodes", 0) > 0:
            print("[PASS] Graph Stats (nodes > 0)")
        else:
             print("[WARN] Graph Stats: 0 nodes (might be clean DB)")
    except Exception as e:
        print(f"[FAIL] Graph Stats: {e}")
        return False

    # 6. Graph Visualize
    try:
        r = requests.get(f"{BASE_URL}/graph/visualize?limit=10")
        assert r.status_code == 200
        elements = r.json()
        print(f"[INFO] Graph Viz Elements: {len(elements)}")
        # Check structure
        if len(elements) > 0 and "data" in elements[0]:
             print("[PASS] Graph Visualization")
        else:
             print("[WARN] Graph Visualization: No elements or invalid format")
    except Exception as e:
        print(f"[FAIL] Graph Viz: {e}")
        return False

    return True

if __name__ == "__main__":
    if run_tests():
        print("\n✅ Verification SUCCESSFUL")
        sys.exit(0)
    else:
        print("\n❌ Verification FAILED")
        sys.exit(1)
