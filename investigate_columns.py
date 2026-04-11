import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

def main():
    tables = ['desayunos_frios', 'desayunos_fríos', 'desayunos_calientes', 'desayunos_eaeyd']
    print("--- INVESTIGACIÓN DE COLUMNAS (DETALLADO) ---")
    for t in tables:
        try:
            # Seleccionamos el primer registro para ver sus llaves (columnas)
            res = supabase.table(t).select('*').limit(1).execute()
            if res.data:
                print(f"\nTABLA: {t}")
                print(f"COLUMNAS: {list(res.data[0].keys())}")
            else:
                print(f"\nTABLA: {t} (VACÍA - No puedo ver columnas)")
        except Exception as e:
            print(f"\nTABLA: {t} (ERROR: {e})")

if __name__ == "__main__":
    main()
