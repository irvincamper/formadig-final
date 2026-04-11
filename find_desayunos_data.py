from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Comprehensive list of tables mentioned in various scripts
        potential_tables = [
            "desayunos_eaeyd", "desayunos_frios", "desayunos_calientes",
            "desayunos_sieb", "sieb_desayunos", "beneficiarios_desayunos",
            "padron_desayunos"
        ]
        
        found = {}
        for table in potential_tables:
            try:
                res = supabase.table(table).select("*", count="exact").limit(5).execute()
                if res.count is not None and res.count > 0:
                    found[table] = {
                        "count": res.count,
                        "sample_tipo_apoyo": [r.get("tipo_apoyo") for r in res.data if "tipo_apoyo" in r]
                    }
                elif res.data: # Fallback if count is not returned
                    found[table] = {
                        "count": len(res.data),
                        "sample_tipo_apoyo": [r.get("tipo_apoyo") for r in res.data if "tipo_apoyo" in r]
                    }
            except:
                pass
        
        print("--- EXTENDED TABLE DISCOVERY ---")
        print(json.dumps(found, indent=2))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
