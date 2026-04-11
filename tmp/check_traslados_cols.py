
import os
import sys

# Path to find supabase config
sys.path.append(os.path.join(os.getcwd(), "Formadig", "1_Sistema_DIF_Acatlan", "modulos", "sms", "logica"))
from sms_backend import supabase

try:
    if supabase:
        res = supabase.table('traslados').select("*").limit(1).execute()
        if res.data:
            print("Columnas en 'traslados':", res.data[0].keys())
        else:
            print("La tabla 'traslados' está vacía o no tiene registros de prueba.")
except Exception as e:
    print(f"Error: {e}")
