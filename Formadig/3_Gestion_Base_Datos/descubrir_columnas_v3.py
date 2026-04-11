import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

potential_columns = [
    "id", "nombre", "nombre_completo", "beneficiario", "full_name", "fullName",
    "curp", "curp_beneficiario",
    "escuela", "plantel", "institucion", "localidad", "sede", 
    "tutor", "nombre_tutor", "padre_tutor", "tutorName",
    "estatus", "estado", "status",
    "tipo_apoyo", "sector", "programa",
    "created_at", "fecha", "fecha_registro", "date", "timestamp"
]

print("STARTING DETAILED COLUMN CHECK for desayunos_sieb...")
for col in potential_columns:
    try:
        supabase.table('desayunos_sieb').select(col).limit(1).execute()
        print(f"✅ COLUMN FOUND: {col}")
    except Exception as e:
        # No imprimir errores para mantener la salida limpia
        pass
print("CHECK FINISHED.")
