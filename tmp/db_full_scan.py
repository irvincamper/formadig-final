import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        tables = [
            "hospitales", "chatbot_conocimiento", "traslados", 
            "desayunos_sieb", "desayunos_calientes", "desayunos_frios",
            "espacios_eaeyd", "perfiles", "atencion_ciudadana"
        ]
        
        found = {}
        for table in tables:
            try:
                res = supabase.table(table).select("*", count="exact").limit(1).execute()
                found[table] = {
                    "count": res.count if res.count is not None else 0,
                    "columns": list(res.data[0].keys()) if res.data else []
                }
            except Exception as e:
                pass
        
        print(json.dumps(found, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
