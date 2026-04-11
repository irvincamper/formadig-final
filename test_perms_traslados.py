import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

test_data = {
    "nombre_beneficiario": "TEST PERMISOS",
    "curp": "TEST000000X",
    "fecha_traslado": "2026-03-23"
}

print(f"TESTING INSERT TO traslados...")
try:
    res = supabase.table('traslados').insert(test_data).execute()
    print("✅ TEST traslados SUCCESSFUL!")
    print(res.data)
except Exception as e:
    print(f"❌ TEST traslados FAILED: {e}")
