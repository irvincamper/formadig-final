import os
import requests
import json

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyD1FhiP8ZdGIpwPdHz3NMFHFWASea1xGUo")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"

try:
    response = requests.get(GEMINI_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
