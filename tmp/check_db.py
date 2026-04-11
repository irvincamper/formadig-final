from supabase import create_client

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== ESTRUCTURA DE desayunos_eaeyd ===\n")
try:
    r = supabase.table("desayunos_eaeyd").select("*").limit(3).execute()
    print(f"Total accesibles ahora: {len(r.data)}")
    if r.data:
        print(f"Columnas: {list(r.data[0].keys())}")
        for i, rec in enumerate(r.data):
            print(f"\nRegistro {i+1}: {rec}")
    else:
        print("Sin datos aun, pero mostrando columnas via insert vacio...")
except Exception as ex:
    print(f"Error: {ex}")

print("\n=== TRASLADOS - Estructura ===\n")
try:
    r2 = supabase.table("traslados").select("*").limit(3).execute()
    print(f"Total registros traslados: {len(r2.data)}")
    if r2.data:
        print(f"Columnas: {list(r2.data[0].keys())}")
        for i, rec in enumerate(r2.data):
            print(f"\nRegistro {i+1}: {rec}")
    else:
        print("Traslados vaco por ahora")
except Exception as ex:
    print(f"Error traslados: {ex}")
