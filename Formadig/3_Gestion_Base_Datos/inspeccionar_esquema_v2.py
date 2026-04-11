import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    print("--- Inspecting desayunos_sieb ---")
    res = supabase.table('desayunos_sieb').select('*').limit(1).execute()
    if res.data:
        print("Data found:")
        print(json.dumps(res.data[0], indent=2))
    else:
        print("No data found in desayunos_sieb.")
        
    print("\n--- Inspecting desayunos_frios ---")
    res2 = supabase.table('desayunos_frios').select('*').limit(1).execute()
    if res2.data:
        print("Data found in desayunos_frios:")
        print(json.dumps(res2.data[0], indent=2))
    else:
        print("No data found in desayunos_frios or table doesn't exist.")

except Exception as e:
    print(f"ERROR: {e}")
