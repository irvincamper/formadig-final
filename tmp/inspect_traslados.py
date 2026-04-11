
import os
import sys

# Add path to import sms_backend config
sys.path.append(os.path.join(os.getcwd(), "Formadig", "1_Sistema_DIF_Acatlan", "modulos", "sms", "logica"))
from sms_backend import supabase

try:
    if supabase:
        # Check current columns of 'traslados'
        res = supabase.table('traslados').select("*").limit(1).execute()
        if res.data:
            print(f"Columnas actuales en 'traslados': {list(res.data[0].keys())}")
        else:
            print("No se encontraron registros en 'traslados' para inspeccionar columnas.")
except Exception as e:
    print(f"Error: {e}")
