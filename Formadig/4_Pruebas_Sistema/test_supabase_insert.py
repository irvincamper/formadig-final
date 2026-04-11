from supabase import create_client, Client
from datetime import datetime
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase_data = {
    "nombre_completo": "Test Sem Data",
    "curp": "TEST111111HDFRRN01",
    "localidad": "Sede Test Sem Data",
    "tipo_apoyo": "Calientes"
}

print(f"PROBANDO INSERCIÓN CON: {json.dumps(supabase_data, indent=2)}")

try:
    res = supabase.table('desayunos_sieb').insert(supabase_data).execute()
    print("✅ INSERCIÓN EXITOSA!")
    print(res.data)
except Exception as e:
    print(f"❌ FALLÓ LA INSERCIÓN: {e}")
