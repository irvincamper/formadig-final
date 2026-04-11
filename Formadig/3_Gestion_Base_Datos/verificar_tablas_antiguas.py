from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

tables = ["desayunos_frios", "desayunos_calientes", "espacios_eaeyd"]

for table in tables:
    print(f"CHECKING TABLE: {table}")
    try:
        res = supabase.table(table).select('*').limit(1).execute()
        if res.data:
            print(f"✅ TABLE {table} EXISTS and has data!")
            print(list(res.data[0].keys()))
        else:
            # Intentar ver si las columnas existen aunque esté vacía
            res_col = supabase.table(table).select('id').limit(1).execute()
            print(f"✅ TABLE {table} EXISTS but is empty.")
    except Exception as e:
        print(f"❌ TABLE {table} NOT FOUND or ERROR: {e}")
