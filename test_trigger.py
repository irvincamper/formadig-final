import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Intentar insertar con ABSOLUTAMENTE NADA (solo campos que sabemos que existen o dejar que fallen los obligatorios)
# Si falla por "estado", entonces es un TRIGGER.
print("TESTING MINIMAL INSERT...")
try:
    # Enviamos solo nombre_completo que es lo más básico
    res = supabase.table('desayunos_sieb').insert({"nombre_completo": "Test Trigger"}).execute()
    print("✅ INSERT worked.")
except Exception as e:
    print(f"❌ INSERT ERROR: {e}")
