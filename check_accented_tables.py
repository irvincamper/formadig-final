from supabase import create_client, Client
import json

# Script de verificación de tablas con acentos
SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Verificando las tablas que vimos en tu captura
        tables = ["desayunos_fríos", "desayunos_calientes", "desayunos_eaeyd"]
        results = {}
        
        for table in tables:
            try:
                res = supabase.table(table).select('*').limit(5).execute()
                results[table] = {
                    "exists": True,
                    "count": len(res.data) if res.data else 0,
                    "sample": res.data[0] if res.data else None
                }
            except Exception as e:
                results[table] = {"exists": False, "error": str(e)}
        
        print("--- VERIFICACIÓN DE TABLAS (SUPABASE) ---")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error Global: {e}")

if __name__ == "__main__":
    main()
