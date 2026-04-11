from supabase import create_client, Client

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

potential_columns = [
    "id", "nombre", "nombre_completo", "beneficiario", "fullName",
    "curp", "curp_beneficiario",
    "escuela", "plantel", "institucion", "localidad", "sede", 
    "tutor", "nombre_tutor", "padre_tutor", "tutorName",
    "estatus", "estado", "status",
    "tipo_apoyo", "sector", "programa",
    "created_at", "fecha", "fecha_registro", "date"
]

existing = []
for col in potential_columns:
    try:
        supabase.table('desayunos_sieb').select(col).limit(1).execute()
        existing.append(col)
    except:
        pass

print("SCHEMA DISCOVERY for desayunos_sieb:")
print(", ".join(existing))
