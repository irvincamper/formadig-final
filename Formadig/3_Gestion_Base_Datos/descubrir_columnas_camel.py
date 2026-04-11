import os
from supabase import create_client, Client
import json

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

potential_columns = [
    "id", "nombre_completo", "beneficiaryName", "fullName",
    "curp", "localidad", "address",
    "tutor", "tutorName", "tutor_nombre", "nombre_tutor",
    "estado", "status", "estatus",
    "tipo_apoyo", "sector", "program",
    "fecha_registro", "created_at", "date", "registrationDate"
]

found = []
for col in potential_columns:
    try:
        supabase.table('desayunos_sieb').select(col).limit(1).execute()
        found.append(col)
    except:
        pass

with open('schema_camel.txt', 'w') as f:
    json.dump(found, f, indent=2)

print("FILE schema_camel.txt WRITTEN.")
