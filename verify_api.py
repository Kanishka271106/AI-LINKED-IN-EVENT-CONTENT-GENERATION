import requests
import time

BASE_URL = "http://localhost:8000"

def test_api():
    print("--- Verifying API Health ---")
    try:
        r = requests.get(f"{BASE_URL}/api/health")
        print(f"Health: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Server not reachable: {e}")
        return

    print("\n--- Verifying Auth Status ---")
    r = requests.get(f"{BASE_URL}/api/auth/status")
    print(f"Auth Status: {r.status_code} - {r.json()}")

    print("\n--- Verifying Stats ---")
    r = requests.get(f"{BASE_URL}/api/stats")
    stats = r.json()
    print(f"Stats: {stats}")

    print("\n--- Verifying Auth URL Generation ---")
    r = requests.get(f"{BASE_URL}/api/auth/linkedin")
    auth_data = r.json()
    print(f"Auth URL: {auth_data.get('auth_url')[:50]}...")
    if "openid" in auth_data.get('auth_url') and "email" in auth_data.get('auth_url'):
        print("[OK] New scopes found in Auth URL")
    else:
        print("[FAIL] Missing modern scopes in Auth URL")

if __name__ == "__main__":
    test_api()
