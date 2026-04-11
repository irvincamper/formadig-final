from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
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

@app.route('/api/traslados', methods=['GET'])
def obtener_registros():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500
    
    try:
        res = supabase.table('traslados').select('*').order('fecha_cita', desc=False).execute()
        return jsonify({"traslados": res.data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/traslados', methods=['POST'])
def nuevo_registro():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    
    # Validar campos obligatorios según el nuevo schema de traslados
    required_fields = ['paciente_nombre', 'paciente_curp', 'destino', 'cita_fecha', 'cita_hora']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    try:
        # Mapeo de campos del Frontend al Schema SQL de Supabase
        supabase_data = {
            "paciente_nombre": data.get('paciente_nombre'),
            "paciente_curp": data.get('paciente_curp'),
            "acompanante_nombre": data.get('acompanante_nombre'),
            "destino_hospital": data.get('destino'),
            "fecha_cita": data.get('cita_fecha'),
            "hora_salida": data.get('cita_hora'),
            "lugares_requeridos": data.get('lugares_requeridos', 2),
            "estatus": data.get('estatus', 'Programado')
        }

        # Insertar en Supabase
        res = supabase.table('traslados').insert(supabase_data).execute()
        new_transfer = res.data[0]
        
        # El historial_traslados ya no existe en el nuevo schema, se remueve.

        print(f"🚑 Traslado agendado: {data['paciente_nombre']}")
        return jsonify({"message": "Guardado exitosamente en Supabase", "data": new_transfer}), 201
    except Exception as e:
        print(f"❌ Error al guardar traslado: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/traslados/<string:record_id>', methods=['PUT', 'PATCH'])
def actualizar_traslado(record_id):
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    try:
        update_data = {
            "fecha_cita": data.get('cita_fecha'),
            "hora_salida": data.get('cita_hora'),
            "lugares_requeridos": data.get('lugares_requeridos', 2),
            "estatus": data.get('estatus', 'Programado')
        }
        res = supabase.table('traslados').update(update_data).eq('id', record_id).execute()
        if not res.data:
            return jsonify({"error": "Registro no encontrado para actualizar"}), 404
            
        print(f"✅ Traslado actualizado para el registro ID: {record_id}")
        return jsonify({"message": "Traslado actualizado correctamente", "data": res.data[0]}), 200
    except Exception as e:
        print(f"❌ Error al actualizar traslado: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚑 Servidor Python iniciado en el puerto 5004 - Traslados (SUPABASE READY)")
    app.run(host='0.0.0.0', port=5004, debug=False, use_reloader=False)
