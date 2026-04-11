import requests
import json

GEMINI_API_KEY = "AIzaSyD1FhiP8ZdGIpwPdHz3NMFHFWASea1xGUo"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

payload = {
    "contents": [{
        "parts": [{ "text": "Hola, ¿cómo estás?" }]
    }]
}

try:
    response = requests.post(GEMINI_URL, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
