import requests

try:
    response = requests.get('http://localhost:5008/api/chatbot/export?table=traslados&format=excel')
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    if response.status_code == 200:
        with open('c:\\Users\\erick\\Downloads\\Formadig (2)\\tmp\\test_export.xlsx', 'wb') as f:
            f.write(response.content)
        print("File saved successfully.")
    else:
        print(f"Error content: {response.text}")
except Exception as e:
    print(f"Error: {e}")
