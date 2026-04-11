import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Intentar obtener un registro sin filtros ni ordenamiento para ver qué campos trae
    res = supabase.table('desayunos_sieb').select('*').limit(1).execute()
    if res.data:
        print("COLUMNS FOUND IN desayunos_sieb:")
        print(json.dumps(list(res.data[0].keys()), indent=2))
    else:
        print("TABLE desayunos_sieb IS EMPTY. Trying to insert a test record to see schema errors...")
        test_data = {"nombre_beneficiario": "TEST"}
        res_test = supabase.table('desayunos_sieb').insert(test_data).execute()
        print("Inserted test record successfully. Columns:")
        print(json.dumps(list(res_test.data[0].keys()), indent=2))
except Exception as e:
    print(f"ERROR: {e}")
