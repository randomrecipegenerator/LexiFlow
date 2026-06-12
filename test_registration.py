
import httpx
import json

URL = "http://localhost:8000/api/api/desktop/folders/register"
API_KEY = "lf_desktop_69c23418a598d2c60c359f0dadb24326565618661cf46c897e2f06e4ed9e5c6f"

payload = {
    "local_path": "/home/user/test-folder",
    "label": "Test Folder",
    "watch_subfolders": True,
    "file_extensions": [".pdf", ".docx"]
}

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

try:
    response = httpx.post(URL, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
