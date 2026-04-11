from supabase import create_client, Client
import json
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # We can't easily list tables with the client, so we try many variants
        variants = [
            "desayunos_frios", "desayunos_fríos", "desayunos_calientes", 
            "desayunos_eaeyd", "traslados", "traslados_eaeyd",
            "beneficiarios", "padroneaeyd"
        ]
        
        results = {}
        for v in variants:
            try:
                # Query 1 record without order
                res = supabase.table(v).select("*", count="exact").limit(1).execute()
                results[v] = {"status": "SUCCESS", "count": res.count, "sample": res.data[0] if res.data else "EMPTY"}
            except Exception as e:
                results[v] = {"status": "ERROR", "msg": str(e)}

        print("--- DATABASE DIAGNOSTIC ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
