import requests
import json

def test_simulation(port, endpoint, label):
    url = f"http://localhost:{port}/api/{endpoint}"
    payload = {
        "nombre_beneficiario": f"Test Omega " + "999",
        "curp": "TEST000000HDFRRN01",
        "escuela": "Sede Central Test",
        "tutor": "Tutor Test",
        "estatus": "Pendiente"
    }
    
    print(f"Testing {label} at {url}...")
    try:
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing {label}: {e}")

if __name__ == "__main__":
    # Test Calientes (5006)
    test_simulation(5006, "desayunos_calientes", "Calientes")
