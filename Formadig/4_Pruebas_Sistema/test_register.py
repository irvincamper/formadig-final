from supabase import create_client, Client
import sys
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    email = "1@gmail.com"
    password = "password123"
    
    print(f"Intentando Registrar a {email}...")
    res = supabase.auth.sign_up({
        "email": email,
        "password": password,
        "options": {
            "data": { 
                "role": "admin_traslados",
                "nombre_completo": "Test User 1"
            }
        }
    })
    print(f"Registro Exitoso en Auth: {res.user.id}")
    
    # Intentar Upsert en perfiles
    print("Intentando Upsert en perfiles...")
    prof_res = supabase.table('perfiles').upsert({
        "id": res.user.id,
        "nombre_usuario": email,
        "nombre_completo": "Test User 1",
        "rol": 'admin_traslados'
    }).execute()
    print(f"Upsert Exitoso: {prof_res.data}")
    
except Exception as e:
    print(f"Fallo en Registro: {e}")
