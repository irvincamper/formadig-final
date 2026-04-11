import sys
import os
# Set encoding to utf-8 just in case
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Exact names from the screenshot
        tables = ["desayunos_fríos", "desayunos_calientes", "desayunos_eaeyd"]
        results = {}
        
        for table in tables:
            try:
                # Try to count rows properly
                res = supabase.table(table).select("*", count='exact').limit(3).execute()
                results[table] = {
                    "exists": True,
                    "count": res.count if res.count is not None else len(res.data),
                    "data_sample": res.data
                }
            except Exception as e:
                results[table] = {"exists": False, "error": str(e)}
        
        print("--- FINAL DATA SOURCE VERIFICATION ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
