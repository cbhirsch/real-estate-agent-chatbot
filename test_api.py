import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test the FastAPI chatbot
def test_chatbot():
    base_url = "http://localhost:8000"
    
    # Get API key from environment
    api_keys = os.getenv("API_KEYS", "").split(",")
    if not api_keys or api_keys[0] == "":
        print("❌ No API keys found in environment. Please set API_KEYS in your .env file")
        return
    
    api_key = api_keys[0]  # Use first API key
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Test health endpoint (no auth required)
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    
    # Test chat endpoint with authentication
    print("\nTesting chat endpoint...")
    chat_data = {
        "message": "Hello! I'm looking for a house in the suburbs.",
        "session_id": "test-session-123"
    }
    
    response = requests.post(f"{base_url}/chat", json=chat_data, headers=headers)
    print(f"Chat response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"AI Response: {result['response']}")
        print(f"Session ID: {result['session_id']}")
    elif response.status_code == 401:
        print("❌ Authentication failed. Check your API key.")
    else:
        print(f"❌ Error: {response.text}")
    
    # Test session retrieval with authentication
    print("\nTesting session retrieval...")
    response = requests.get(f"{base_url}/sessions/test-session-123", headers=headers)
    print(f"Session retrieval: {response.status_code}")
    if response.status_code == 200:
        session = response.json()
        print(f"Session messages: {len(session['messages'])} messages")
    elif response.status_code == 401:
        print("❌ Authentication failed. Check your API key.")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_chatbot() 