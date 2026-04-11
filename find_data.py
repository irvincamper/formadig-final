from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

def main():
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # List of potential tables from the project scripts
        potential_tables = [
            "desayunos", "beneficiarios", "padron_sieb", "registros_sieb",
            "desayunos_frios", "desayunos_calientes", "espacios_eaeyd",
            "padron_beneficiarios", "programas_sociales", "sieb_2025",
            "desayunos_sieb_2025", "sieb_desayunos", "dif_beneficiarios",
            "desayunos_eaeyd", "traslados", "usuarios", "discapacidad",
            "atencion_ciudadana", "peticiones"
        ]
        
        found = {}
        for table in potential_tables:
            try:
                # Try to count rows
                res = supabase.table(table).select("*", count="exact").limit(1).execute()
                # If it doesn't fail, the table exists
                found[table] = res.count if res.count is not None else 0
            except:
                pass
        
        print("--- DISCOVERED TABLES WITH DATA ---")
        print(json.dumps(found, indent=2))
        
    except Exception as e:
        print(f"Global Error: {e}")

if __name__ == "__main__":
    main()
