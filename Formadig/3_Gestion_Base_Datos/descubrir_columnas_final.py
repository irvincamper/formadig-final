from supabase import create_client, Client
import json

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

potential_columns = [
    "id", "nombre", "nombre_completo", "beneficiario", "full_name",
    "curp", "curp_beneficiario",
    "escuela", "plantel", "institucion", "localidad", "sede", 
    "tutor", "nombre_tutor", "padre_tutor",
    "estatus", "estado", "status",
    "tipo_apoyo", "sector", "programa",
    "fecha_registro", "created_at", "fecha", "date"
]

found = []
for col in potential_columns:
    try:
        supabase.table('desayunos_sieb').select(col).limit(1).execute()
        found.append(col)
    except:
        pass

with open('schema_final.txt', 'w') as f:
    json.dump(found, f, indent=2)

print("FILE schema_final.txt WRITTEN SUCCESSFULLY.")
