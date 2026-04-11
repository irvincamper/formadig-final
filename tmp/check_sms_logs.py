
import os
import sys

# Añadir el path para importar sms_backend
sys.path.append(os.path.join(os.getcwd(), "Formadig", "1_Sistema_DIF_Acatlan", "modulos", "sms", "logica"))

from sms_backend import supabase

try:
    if supabase:
        res = supabase.table('sms_logs').select("*").execute()
        print(f"Total registros en sms_logs: {len(res.data)}")
        for r in res.data:
            print(r)
    else:
        print("Error: Supabase no está configurado.")
except Exception as e:
    print(f"Error al consultar: {e}")
