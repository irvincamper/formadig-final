import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    res = supabase.table('desayunos_sieb').select('*').limit(5).execute()
    if res.data:
        print("DATA FOUND IN desayunos_sieb:")
        for row in res.data:
            print(list(row.keys()))
            print(row)
    else:
        print("TABLE desayunos_sieb IS EMPTY.")
except Exception as e:
    print(f"ERROR SELECTING ALL: {e}")
