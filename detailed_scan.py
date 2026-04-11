from supabase import create_client, Client
import json
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # We will try common variations including those in the screenshot
        tables_to_check = [
            "desayunos_eaeyd", 
            "desayunos_calientes", 
            "desayunos_fríos", 
            "desayunos_frios", 
            "desayunos_sieb", 
            "registros_sieb",
            "sieb_2025",
            "padron_sieb"
        ]
        
        results = {}
        for table in tables_to_check:
            try:
                # Use count='exact' to get total number of rows regardless of filters
                res = supabase.table(table).select("*", count='exact').limit(1).execute()
                results[table] = {
                    "exists": True,
                    "count": res.count if res.count is not None else len(res.data),
                    "sample": res.data[0] if res.data else None
                }
            except Exception as e:
                # Keep track of error to see if it's "not found" or "forbidden"
                results[table] = {"exists": False, "error": str(e)}
        
        print("--- DETAILED TABLE DATA SCAN ---")
        # Ensure utf-8 output handling
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
