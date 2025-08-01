import requests
import json

def test_vapi_webhook():
    base_url = "https://web-production-dd65f.up.railway.app"
    
    # Use the VAPI API key directly
    api_key = "xczNynnGBBvnJv0zHO5A1DkKwQevSTGsRI6W2E"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test VAPI webhook endpoint
    print("Testing VAPI webhook endpoint...")
    vapi_data = {
        "session_id": "vapi-test-session-123",
        "user_message": "Hello! I'm looking for a 3-bedroom house in the suburbs.",
        "context": {
            "call_id": "test-call-123",
            "user_phone": "+1234567890"
        }
    }
    
    response = requests.post(f"{base_url}/vapi/webhook", json=vapi_data, headers=headers)
    print(f"VAPI webhook response: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ VAPI Response: {result['response']}")
        print(f"✅ Session ID: {result['session_id']}")
        print("✅ VAPI webhook is working correctly!")
    elif response.status_code == 401:
        print("❌ Authentication failed. Check your API key.")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_vapi_webhook() 