#!/usr/bin/env python3
"""
Postmark Inbound Webhook Test Script for LexiFlow.

Tests the /api/reception/postmark/inbound endpoint with:
1. A standard inbound email
2. An email with firm-specific routing (firm+slug@lexiflow.co)
3. An email with attachments  
4. A malformed payload (edge case)

Usage:
    python3 test_postmark_inbound.py              # Localhost test
    python3 test_postmark_inbound.py --live       # Test against live URL
"""
import json
import sys
import urllib.request
import urllib.error

STANDARD_INBOUND = {
    "From": "john.doe@example.com",
    "FromName": "John Doe",
    "Subject": "Consultation about car accident",
    "TextBody": "Hi, I was in a car accident last week on I-55. I have neck pain and my car was totaled. Can you help?",
    "HtmlBody": "<html><body><p>Hi, I was in a car accident last week on I-55.</p></body></html>",
    "To": "contact@lexiflow.co",
    "ToFull": [{"Email": "contact@lexiflow.co", "Name": "LexiFlow Legal"}],
    "MailboxHash": "",
    "Date": "2026-06-02T20:55:00Z",
    "OriginalRecipient": "contact@lexiflow.co",
    "MessageID": "test-msg-001",
    "Headers": [
        {"Name": "X-Spam-Status", "Value": "Clean"},
        {"Name": "Message-ID", "Value": "<test-msg-001@example.com>"}
    ],
    "Attachments": []
}

FIRM_SPECIFIC_INBOUND = {
    "From": "sarah.miller@lawfirm.com",
    "FromName": "Sarah Miller",
    "Subject": "Potential PI case referral",
    "TextBody": "I'm referring a potential client who was injured in a construction accident. His name is Mark Williams.",
    "To": "smith+lacien@lexiflow.co",
    "ToFull": [{"Email": "smith+lacien@lexiflow.co", "Name": "Smith LaCien"}],
    "MailboxHash": "lacien",
    "Date": "2026-06-02T21:00:00Z",
    "OriginalRecipient": "smith+lacien@lexiflow.co",
    "MessageID": "test-msg-002",
    "Headers": [],
    "Attachments": []
}

WITH_ATTACHMENTS = {
    "From": "dr.evans@hospital.org",
    "FromName": "Dr. Robert Evans",
    "Subject": "Medical records for patient review",
    "TextBody": "Please find attached the medical records for review.",
    "To": "contact@lexiflow.co",
    "ToFull": [{"Email": "contact@lexiflow.co", "Name": "LexiFlow"}],
    "MailboxHash": "",
    "Date": "2026-06-02T21:05:00Z",
    "MessageID": "test-msg-003",
    "Headers": [],
    "Attachments": [
        {
            "Name": "records.pdf",
            "Content": "JVBERi0xLjcK...",
            "ContentType": "application/pdf",
            "ContentLength": 12345
        }
    ]
}

MALFORMED_PAYLOAD = {
    "From": "test@example.com"
}

def test_endpoint(url: str, name: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return {"name": name, "status": resp.status, "body": json.loads(body) if body else {}, "success": True}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        return {"name": name, "status": e.code, "body": body, "success": False, "error": str(e)}
    except Exception as e:
        return {"name": name, "status": 0, "body": {}, "success": False, "error": str(e)}

def main():
    use_live = "--live" in sys.argv
    base_url = "https://lexiflow.co/api/reception/postmark/inbound" if use_live else "http://localhost:8000/api/reception/postmark/inbound"
    print(f"{'🔴 LIVE' if use_live else '🔵 LOCAL'} ENDPOINT: {base_url}")
    print("=" * 70)

    tests = [
        (STANDARD_INBOUND, "1. Standard Inbound Email"),
        (FIRM_SPECIFIC_INBOUND, "2. Firm-Specific Routing (smith+lacien@lexiflow.co)"),
        (WITH_ATTACHMENTS, "3. Email with Attachments"),
        (MALFORMED_PAYLOAD, "4. Malformed Payload (edge case)"),
    ]

    all_passed = True
    for payload, name in tests:
        print(f"\n📧 TEST: {name}")
        result = test_endpoint(base_url, name, payload)
        if result["success"]:
            print(f"   ✅ Status: {result['status']}")
            if result["body"].get("lead_id"):
                print(f"   ✅ Lead created: ID {result['body']['lead_id']}")
        else:
            print(f"   ❌ Status: {result['status']}: {result.get('error', 'Unknown')}")
            all_passed = False

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED")

if __name__ == "__main__":
    main()