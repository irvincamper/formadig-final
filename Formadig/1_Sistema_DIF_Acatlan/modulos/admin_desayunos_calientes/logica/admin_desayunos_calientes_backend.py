from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

# Lógica de Backend de Python - Desayunos Calientes (V8: FINAL ROBUST FIX)
app = Flask(__name__)
CORS(app)

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"
global_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/desayunos_calientes', methods=['GET'])
def obtener_registros():
    try:
        candidate_tables = ['desayunos_calientes', 'desayunos_eaeyd']
        responses = []
        for table in candidate_tables:
            try:
                res = global_client.table(table).select('*').execute()
                if table == 'desayunos_eaeyd':
                    responses.extend([r for r in res.data if r.get('tipo_apoyo') == 'Calientes'])
                else:
                    responses.extend(res.data)
            except: continue
        
        desayunos_mapeados = []
        for r in responses:
            record_id = r.get('Identificación') or r.get('id') or r.get('uuid')
            nombre = r.get('nombres') or r.get('nombre') or r.get('nombre_beneficiario') or ''
            apell = r.get('apellidos') or r.get('apellido') or ''
            nombre_completo = f"{nombre} {apell}".strip()
            if not nombre_completo:
                nombre_completo = r.get('bordillo') or r.get('curp') or f"Caliente #{str(record_id)[:8] if record_id else '?'}"
            
            desayunos_mapeados.append({
                "id": str(record_id),
                "nombre_beneficiario": nombre_completo,
                "nombres": nombre, 
                "apellidos": apell,
                "curp": r.get('curp') or r.get('bordillo'),
                "fecha_nacimiento": r.get('fecha_nacimiento') or r.get('nacimiento'),
                "sexo": r.get('sexo') or r.get('genero'),
                "estado_civil": r.get('estado_civil') or 'Soltero(a)',
                
                # Datos de Salud
                "peso_menor": r.get('peso_menor') or r.get('peso'),
                "estatura_menor": r.get('estatura_menor') or r.get('estatura') or r.get('talla'),
                
                # Socioeconómico
                "nivel_estudios": r.get('nivel_estudios') or r.get('estudios'),
                "ingreso_mensual": r.get('ingreso_mensual') or r.get('ingreso_familiar') or r.get('ingreso'),
                "situacion_vulnerabilidad": r.get('situacion_vulnerabilidad') or r.get('vulnerabilidad'),
                
                # Ubicación
                "localidad": r.get('localidad') or r.get('comunidad'),
                "tipo_asentamiento": r.get('tipo_asentamiento') or 'Colonia',
                "cp": r.get('cp') or r.get('codigo_postal'),
                "referencias": r.get('referencias') or r.get('vialidades'),
                
                # Tutor
                "tutor": r.get('tutor_nombre') or r.get('tutor'),
                "clave_elector_tutor": r.get('clave_elector_tutor') or r.get('clave_elector') or r.get('ine_tutor'),
                "telefono": r.get('telefono') or r.get('celular'),
                
                # Documentos
                "url_curp": r.get('url_curp') or r.get('url_doc_curp') or r.get('curp_url'),
                "url_comprobante_salud": r.get('url_comprobante_salud') or r.get('url_doc_salud') or r.get('url_salud'),
                "url_ine_tutor": r.get('url_ine_tutor') or r.get('url_doc_ine_tutor') or r.get('url_ine') or r.get('foto_ine_url'),
                "url_comprobante_domicilio": r.get('url_comprobante_domicilio') or r.get('comprobante_domicilio') or r.get('url_comprobante'),
                "url_foto_infante": r.get('url_foto_infante') or r.get('foto_infante') or r.get('url_foto'),
                
                "escuela": r.get('escuela') or r.get('plantel') or 'No asignada',
                "estatus": r.get('estatus') or 'Pendiente'
            })
        return jsonify({"desayunos": desayunos_mapeados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/desayunos_calientes/<string:record_id>', methods=['PUT', 'PATCH'])
def dictamen_registro(record_id):
    data = request.json
    if not data:
        return jsonify({"error": "No hay datos para actualizar"}), 400
    
    try:
        # BÚSQUEDA DEL REGISTRO PARA ENCONTRAR TABLA E ID CORRECTO
        target_table = None
        id_col = None
        for table in ['desayunos_calientes', 'desayunos_eaeyd']:
            for col in ['Identificación', 'id', 'uuid']:
                try:
                    check = global_client.table(table).select('*').eq(col, record_id).execute()
                    if check.data:
                        target_table = table; id_col = col; break
                except: continue
            if target_table: break
        
        if not target_table:
            return jsonify({"error": "No se encontró el registro"}), 404

        # Construir el objeto de actualización basado en lo recibido
        # Mapeamos los campos del frontend a los nombres probables de la base de datos
        update_payload = {}
        
        # Mapeo de campos comunes (JS -> DB)
        field_mapping = {
            "nombre_beneficiario": "nombres",
            "nombres": "nombres",
            "apellidos": "apellidos",
            "curp": "curp",
            "fecha_nacimiento": "fecha_nacimiento",
            "sexo": "sexo",
            "estado_civil": "estado_civil",
            "peso_menor": "peso",
            "estatura_menor": "talla",
            "nivel_estudios": "nivel_estudios",
            "ingreso_mensual": "ingreso_mensual",
            "localidad": "localidad",
            "tipo_asentamiento": "tipo_asentamiento",
            "cp": "codigo_postal",
            "referencias": "referencias",
            "tutor": "tutor_nombre",
            "clave_elector_tutor": "ine_tutor",
            "telefono": "tutor_telefono",
            "escuela": "escuela",
            "estatus": "estatus"
        }

        for frontend_key, db_key in field_mapping.items():
            if frontend_key in data:
                update_payload[db_key] = data[frontend_key]

        # Si viene 'situacion_vulnerabilidad', intentar ponerlo en la columna que exista
        if 'situacion_vulnerabilidad' in data:
            update_payload['situacion_vulnerabilidad'] = data['situacion_vulnerabilidad']

        if not update_payload:
            return jsonify({"error": "No se enviaron campos válidos para actualizar"}), 400

        # ACTUALIZACIÓN EN SUPABASE
        res = global_client.table(target_table).update(update_payload).eq(id_col, record_id).execute()
            
        return jsonify({"message": "¡Cambios guardados exitosamente!", "data": res.data}), 200
    except Exception as e:
        print(f"Error en PUT: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🍲 Backend Calientes (V8 FINAL) iniciado en puerto 5006")
    app.run(host='0.0.0.0', port=5006, debug=False, use_reloader=False)
