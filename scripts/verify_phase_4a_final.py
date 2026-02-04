
import requests
import sys
import os
import json
import asyncio
import websockets
import time
from multiprocessing import Process

# Config
PORT = 8780
BASE_URL = f"http://127.0.0.1:{PORT}/api/v1"
WS_URL = f"ws://127.0.0.1:{PORT}/api/v1/ws/events"

def print_result(name, passed, detail=None):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} [{name}] {detail if detail else ''}")
    return passed

def test_api_endpoints():
    all_passed = True
    
    print("\n--- REST API Tests ---")
    
    # 1. Health
    try:
        r = requests.get(f"http://127.0.0.1:{PORT}/health")
        all_passed &= print_result("Health Check", r.status_code == 200)
    except Exception as e:
        print_result("Health Check", False, str(e))
        all_passed = False

    # 2. Preferences (Set/Get)
    try:
        r = requests.patch(f"{BASE_URL}/preferences", json={"theme": "test_theme"})
        all_passed &= print_result("Preferences Update", r.status_code == 200)
    except: all_passed = False

    # 3. Documents (Upload)
    try:
        with open("test_final.txt", "w") as f: f.write("Final Verification Document")
        with open("test_final.txt", "rb") as f:
            r = requests.post(f"{BASE_URL}/documents/upload", files={"file": ("test_final.txt", f, "text/plain")})
        all_passed &= print_result("Document Upload", r.status_code == 200 or "already exists" in r.text)
    except Exception as e:
        print_result("Document Upload", False, str(e))
        all_passed = False
    finally:
        if os.path.exists("test_final.txt"): os.remove("test_final.txt")

    # 4. Search
    try:
        r = requests.get(f"{BASE_URL}/search", params={"q": "Verification"})
        all_passed &= print_result("Search", r.status_code == 200)
    except: all_passed = False

    # 5. Graph Analytics
    try:
        r = requests.get(f"{BASE_URL}/graph/analytics")
        all_passed &= print_result("Analytics", r.status_code == 200 and "summary" in r.json())
    except: all_passed = False

    # 6. Concepts (Boost - expecting 404 or 200, just connectivity check mostly)
    try:
        r = requests.post(f"{BASE_URL}/concepts/NotExistingConcept/boost")
        # 404 is acceptable logic, 200 is acceptable logic. 500 is fail.
        all_passed &= print_result("Concept Boost", r.status_code in [200, 404])
    except: all_passed = False

    # 7. System Backup
    try:
        r = requests.get(f"{BASE_URL}/system/backup")
        all_passed &= print_result("System Backup", r.status_code == 200)
    except: all_passed = False

    # 8. OpenAPI
    try:
        r = requests.get(f"{BASE_URL}/openapi.json")
        all_passed &= print_result("OpenAPI Spec", r.status_code == 200)
    except: all_passed = False

    return all_passed

async def test_websocket():
    print("\n--- WebSocket Tests ---")
    try:
        async with websockets.connect(WS_URL) as ws:
            print_result("WS Connection", True)
            # We won't wait for events here to keep it fast, just connection check
            return True
    except Exception as e:
        print_result("WS Connection", False, str(e))
        return False

def run_all():
    print(f"Starting Final Verification Phase 4A on port {PORT}...")
    
    # Run REST tests
    rest_result = test_api_endpoints()
    
    # Run WS tests
    ws_result = asyncio.run(test_websocket())
    
    if rest_result and ws_result:
        print("\n🎉 ALL SYSTEMS GO! Phase 4A Verified.")
        sys.exit(0)
    else:
        print("\n⚠️ SOME CHECKS FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(2) 
    run_all()
