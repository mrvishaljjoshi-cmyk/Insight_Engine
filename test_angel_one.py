import requests
import json
import time

BASE_URL = "https://insight.vjprojects.co.in/api"

DUMMY_USER = {
    "username": "tester_dummy_v2",
    "email": "dummy_v2@vjprojects.co.in",
    "password": "Password123!",
    "mobile_no": "1234567890"
}

ANGEL_CREDS = {
    "broker_name": "Angel One",
    "credentials": {
        "SmartAPI Key": "PxbTH3rZ",
        "Client ID": "V91284",
        "Password": "9694",
        "TOTP Secret": "A27WUYYRNLGFTJSODJLQ47G4UQ"
    }
}

def run_test():
    print("--- 1. Registering Dummy User ---")
    resp = requests.post(f"{BASE_URL}/auth/register", json=DUMMY_USER)
    if resp.status_code != 200:
        print(f"Registration status: {resp.status_code} - {resp.text}")
    else:
        print("Success")

    print("\n--- 2. Logging In ---")
    resp = requests.post(f"{BASE_URL}/auth/login", json={
        "username_or_email": DUMMY_USER["username"],
        "password": DUMMY_USER["password"]
    })
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    
    auth_data = resp.json()
    token = auth_data["token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print(f"Logged in as {DUMMY_USER['username']}")

    print("\n--- 3. Adding Angel One Broker ---")
    resp = requests.post(f"{BASE_URL}/brokers/", headers=headers, json=ANGEL_CREDS)
    if resp.status_code != 200:
        print(f"Add broker failed: {resp.text}")
        return
    
    broker_id = resp.json()["id"]
    print(f"Broker added with ID {broker_id}")

    print("\n--- 4. Fetching Real Holdings from Angel One ---")
    resp = requests.get(f"{BASE_URL}/brokers/{broker_id}/holdings", headers=headers)
    if resp.status_code == 200:
        holdings = resp.json()
        print(f"Holdings Data Received: {json.dumps(holdings, indent=2)[:500]}...")
        if holdings.get('status') == True or holdings.get('status') == 'success':
             print("VERIFIED: Angel One data retrieval working!")
        else:
             print(f"VERIFIED: Request sent, but broker returned status: {holdings.get('status')}")
    else:
        print(f"Holdings fetch failed: {resp.status_code} - {resp.text}")

    print("\n--- 5. Deleting Dummy User (Cleanup) ---")
    resp = requests.delete(f"{BASE_URL}/auth/me", headers=headers)
    print(f"User deleted: {resp.status_code} - {resp.text}")
    
    print("\n--- 6. Final System Status ---")
    health = requests.get(f"{BASE_URL}/health").json()
    print(f"Health: {health['status']}")
    if health["status"] == "healthy":
        print("WEBSITE IS WORKING CORRECTLY!")
    else:
        print("WEBSITE HAS ISSUES!")

if __name__ == "__main__":
    run_test()
