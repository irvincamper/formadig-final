import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def main():
    tables = ['desayunos_frios', 'desayunos_fríos', 'desayunos_eaeyd']
    print("--- INVESTIGACIÓN DE IDs ---")
    for t in tables:
        try:
            res = supabase.table(t).select('*').execute()
            if res.data:
                print(f"\nTABLA: {t} ({len(res.data)} registros)")
                for r in res.data:
                    id_val = r.get('Identificación') or r.get('id') or r.get('uuid')
                    print(f" - ID: '{id_val}' | Tipo Apoyo: {r.get('tipo_apoyo')}")
                    # Mostramos todas las columnas que podrían ser el ID
                    id_candidates = {k: v for k, v in r.items() if 'id' in k.lower() or 'uuid' in k.lower() or 'identificación' in k.lower()}
                    print(f"   Candidatos ID: {id_candidates}")
            else:
                print(f"\nTABLA: {t} (VACÍA)")
        except Exception as e:
            print(f"\nTABLA: {t} (ERROR: {e})")

if __name__ == "__main__":
    main()
