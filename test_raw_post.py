import requests
import json
from datetime import datetime
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

payload = {
    "nombre_completo": "CURL INTEGRATION TEST",
    "curp": "CURL999999HDFRRN01",
    "localidad": "Sede Central Curl",
    "tipo_apoyo": "Calientes",
    "fecha_registro": datetime.now().isoformat()
}

url = f"{SUPABASE_URL}/rest/v1/desayunos_sieb?select=id&limit=1"

print(f"GETTING FROM {url}...")
try:
    r = requests.get(url, headers=headers)
    print(f"STATUS: {r.status_code}")
    print(f"RESPONSE: {r.text}")
except Exception as e:
    print(f"ERROR: {e}")
