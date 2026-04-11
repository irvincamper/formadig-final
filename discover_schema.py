from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # We will try to fetch one row from each table to see the schema
        tables = ["desayunos_fríos", "desayunos_calientes"]
        results = {}
        
        for table in tables:
            try:
                # Use a simple select without order to avoid column mismatch errors
                res = supabase.table(table).select("*").limit(1).execute()
                if res.data:
                    results[table] = {
                        "exists": True,
                        "columns": list(res.data[0].keys()),
                        "sample_data": res.data[0]
                    }
                else:
                    results[table] = {"exists": True, "data": "Table is empty or RLS blocked access"}
            except Exception as e:
                results[table] = {"exists": False, "error": str(e)}

        print("--- SCHEMA DISCOVERY ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
