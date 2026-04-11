import sys
import json
import traceback

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    sys.exit(1)

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"ATENCIÓN: Claves de Supabase inválidas o vacías. Error: {e}")
    sys.exit(1)

print("Intentando crear usuario...")
try:
    res = supabase.auth.sign_up({
        "email": "test_error_repro@gmail.com",
        "password": "password123",
        "options": {
            "data": { "role": "admin_desayunos_frios" }
        }
    })
    print(f"Success: {res}")
except Exception as e:
    print("Error ocurrido:")
    print(str(e))
    traceback.print_exc()
