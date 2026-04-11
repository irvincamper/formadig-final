from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

# Lógica de Backend de Python
app = Flask(__name__)
# Permitir que el HTML de cualquier Origen pueda enviar datos (Localhost)
CORS(app)

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

# =========================================================
# REEMPLAZA ESTAS VARIABLES CON LOS DATOS DE TU PROYECTO SUPABASE
# =========================================================
SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"ATENCIÓN: Claves de Supabase inválidas o vacías. Error: {e}")
    supabase = None

@app.route('/api/desayunos_frios', methods=['GET'])
def obtener_registros():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500
    
    try:
        # Consultar la tabla desayunos_sieb filtrando por tipo_apoyo
        # Usamos 'fecha_registro' para el ordenamiento según el esquema real
        res = supabase.table('desayunos_sieb').select('*').eq('tipo_apoyo', 'Frios').order('fecha_registro', desc=True).execute()
        return jsonify({"desayunos": res.data}), 200
    except Exception as e:
        print(f"❌ Error GET Frios: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/desayunos_frios', methods=['POST'])
def nuevo_registro():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    
    # Validar campos obligatorios que el Admin debe aprobar
    required_fields = ['nombre_beneficiario', 'curp', 'escuela', 'tutor', 'estatus']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    try:
        print(f"DEBUG: Intentando insertar en desayunos_sieb (Frios): {data.get('nombre_beneficiario')}")
        # Mapeo de campos del Frontend al Schema SQL real de Supabase (SIEB 2025)
        # Nota: Se han eliminado 'tutor' y 'estado' porque no existen en la tabla física
        supabase_data = {
            "nombre_completo": data.get('nombre_beneficiario'),
            "curp": data.get('curp'),
            "localidad": data.get('escuela'),
            "tipo_apoyo": "Frios",
            "fecha_registro": datetime.now().isoformat()
        }

        # Insertar en Supabase
        res = supabase.table('desayunos_sieb').insert(supabase_data).execute()
        
        print(f"✅ Supabase OK: {res.data[0]['id'] if res.data else 'Sin data'}")
        return jsonify({"message": "Guardado exitosamente en Supabase", "data": res.data[0]}), 201
    except Exception as e:
        print(f"❌ ERROR Supabase Frios: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/desayunos_frios/<string:record_id>', methods=['PUT', 'PATCH'])
def dictamen_registro(record_id):
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    try:
        # Solo actualizamos el dictamen del administrador
        update_data = {
            "localidad": data.get('escuela') # Se mapea a localidad en el esquema real
        }
        res = supabase.table('desayunos_sieb').update(update_data).eq('id', record_id).execute()
        if not res.data:
            return jsonify({"error": "Registro no encontrado para actualizar"}), 404
            
        print(f"✅ Dictamen actualizado para el registro ID: {record_id}")
        return jsonify({"message": "Dictamen guardado correctamente", "data": res.data[0]}), 200
    except Exception as e:
        print(f"❌ Error al actualizar dictamen: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🔥 Servidor Python iniciado en el puerto 5005 - Desayunos Fríos (SUPABASE READY)")
    app.run(host='0.0.0.0', port=5005, debug=False, use_reloader=False)
