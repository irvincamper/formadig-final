from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    # We query information_schema.columns via SQL using a trick if possible, 
    # but the anon key usually doesn't have access.
    # Instead, let's just inspect the GET results of ALL tables and PRINT ALL KEYS.
    
    tables = ['desayunos_frios', 'desayunos_fríos', 'desayunos_calientes', 'desayunos_eaeyd']
    print("--- INSPECCIÓN PROFUNDA DE CAMPOS ---")
    for t in tables:
        try:
            res = supabase.table(t).select('*').limit(3).execute()
            if res.data:
                print(f"\nTablares: {t}")
                for i, r in enumerate(res.data):
                    print(f"  Registro {i+1} llaves: {list(r.keys())}")
            else:
                print(f"\nTablares: {t} (SIN REGISTROS)")
        except Exception as e:
            print(f"\nTablares: {t} (ERROR: {e})")

if __name__ == "__main__":
    main()
