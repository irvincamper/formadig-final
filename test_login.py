from supabase import create_client, Client
import sys

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    email = "test_error_repro@gmail.com"
    password = "password123"
    
    print(f"Intentando Iniciar Sesión con {email}...")
    res = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    print(f"Login Exitoso: {res.user.id}")
except Exception as e:
    print(f"Login Fallido: {e}")
