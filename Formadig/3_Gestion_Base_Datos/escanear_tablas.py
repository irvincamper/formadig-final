import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

potential_tables = [
    "desayunos", "beneficiarios", "padron_sieb", "registros_sieb",
    "desayunos_frios", "desayunos_calientes", "espacios_eaeyd",
    "padron_beneficiarios", "programas_sociales", "sieb_2025",
    "desayunos_sieb_2025", "sieb_desayunos", "dif_beneficiarios"
]

found_tables = []
for table in potential_tables:
    try:
        supabase.table(table).select('id').limit(1).execute()
        found_tables.append(table)
    except Exception as e:
        # print(f"Table {table} not found or no 'id' column: {e}")
        pass

print("SCAN RESULTS:")
print(json.dumps(found_tables, indent=2))
