from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # 1. Let's list some known tables
        tables = ["desayunos_eaeyd", "desayunos_frios", "desayunos_calientes"]
        results = {}
        
        for table in tables:
            try:
                res = supabase.table(table).select('*').limit(5).execute()
                results[table] = {
                    "count": len(res.data) if res.data else 0,
                    "sample": res.data[0] if res.data else None
                }
            except Exception as e:
                results[table] = f"Error: {str(e)}"
        
        # 2. If desayunos_eaeyd exists, check unique values for tipo_apoyo
        if "desayunos_eaeyd" in results and isinstance(results["desayunos_eaeyd"], dict):
            try:
                res = supabase.table("desayunos_eaeyd").select("tipo_apoyo").execute()
                unique_types = set(r.get("tipo_apoyo") for r in res.data if r.get("tipo_apoyo"))
                results["unique_tipo_apoyo"] = list(unique_types)
            except:
                pass

        print("--- DB SURVEY RESULTS ---")
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
