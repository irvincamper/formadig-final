from supabase import create_client, Client
import os
import json

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

tables = ['desayunos_calientes', 'desayunos_frios', 'desayunos_eaeyd']

for table in tables:
    print(f"\n--- Columns in {table} ---")
    try:
        res = supabase.table(table).select('*').limit(1).execute()
        if res.data:
            print(json.dumps(list(res.data[0].keys()), indent=2))
        else:
            print("No data found in table.")
    except Exception as e:
        print(f"Error checking {table}: {e}")
