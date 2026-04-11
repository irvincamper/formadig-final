import requests
import json

def test_sms_api():
    url = "http://localhost:5009/api/sms/send"
    payload = {
        "phone": "5512345678",
        "message": "Mensaje de prueba desde Antigravity",
        "user_id": "test_user"
    }
    
    try:
        print("Enviando petición de prueba al backend...")
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error de conexión: {e}. ¿Está el backend corriendo?")

if __name__ == "__main__":
    test_sms_api()
