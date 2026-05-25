import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_vapi_assistant_request():
    print("\nTesting Vapi assistant-request (Clifford Law)...")
    payload = {
        "message": {
            "type": "assistant-request",
            "metadata": {
                "firm_slug": "clifford-law"
            }
        }
    }
    response = requests.post(f"{BASE_URL}/reception/vapi/brain", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_vapi_assistant_request_disabled():
    print("\nTesting Vapi assistant-request (Disabled Voice)...")
    payload = {
        "message": {
            "type": "assistant-request",
            "metadata": {
                "firm_slug": "unknown-firm"
            }
        }
    }
    response = requests.post(f"{BASE_URL}/reception/vapi/brain", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_vapi_end_of_call():
    print("\nTesting Vapi end-of-call-report...")
    payload = {
        "message": {
            "type": "end-of-call-report",
            "call": {
                "customer": {"number": "+13125551234"}
            },
            "transcript": "User: I had a car accident yesterday. My name is John Test. Assistant: I'm sorry to hear that. Can I have your email? User: john@test.com",
            "summary": "Car accident intake for John Test.",
            "assistant": {
                "metadata": {"firm_slug": "clifford-law"}
            }
        }
    }
    response = requests.post(f"{BASE_URL}/reception/vapi/brain", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_postmark_inbound():
    print("\nTesting Postmark inbound (Clifford Law)...")
    payload = {
        "FromName": "Jane Doe",
        "From": "jane@doe.com",
        "Subject": "New Case Inquiry",
        "TextBody": "I was injured in a slip and fall at the grocery store. Please help.",
        "ToFull": [
            {"Email": "intake+clifford-law@lexiflow.co"}
        ]
    }
    response = requests.post(f"{BASE_URL}/reception/postmark/inbound", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    try:
        test_vapi_assistant_request()
        test_vapi_assistant_request_disabled()
        test_vapi_end_of_call()
        test_postmark_inbound()
    except Exception as e:
        print(f"Error: {e}. Is the server running?")
