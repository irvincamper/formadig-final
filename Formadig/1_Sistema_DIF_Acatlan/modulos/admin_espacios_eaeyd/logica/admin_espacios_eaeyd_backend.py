from flask import Blueprint, request, jsonify
import json
import os
import requests
import base64

# Lógica de Backend de Python - Espacios EAEyD (ROBUSTO CON JWT)
# Crear Blueprint para espacios EAEyD
espacios_eaeyd_bp = Blueprint('espacios_eaeyd', __name__, url_prefix='/api/espacios_eaeyd')

from clinical.security import protect_module
from flask import g
from clinical.validation import uuid_value, ClinicalError

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
global_client = protect_module(espacios_eaeyd_bp, ('admin', 'admin_desayunos'))

@espacios_eaeyd_bp.route('/', methods=['GET'], strict_slashes=False)
def obtener_registros():
    try:
        try:
            res = global_client.table('desayunos_eaeyd').select('*').order('fecha_registro', desc=True).limit(1000).execute()
            responses = res.data if res.data else []
        except Exception as e:
            print("Error cargando desayunos_eaeyd:", e)
            responses = []
        
        desayunos_mapeados = []
        for r in responses:
            record_id = r.get('id') or r.get('uuid') or r.get('Identificación')
            nombre = r.get('nombres') or ''
            apell = r.get('apellidos') or ''
            nombre_completo = f"{nombre} {apell}".strip()
            
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
                
                # Ubicación
                "localidad": r.get('localidad') or r.get('comunidad') or r.get('sede'),
                "colonia": r.get('colonia'),
                "tipo_asentamiento": r.get('tipo_asentamiento') or r.get('asentamiento'),
                "municipio": r.get('municipio') or 'Acatlán',
                "estado": r.get('estado') or 'Puebla',
                "cp": r.get('cp') or r.get('codigo_postal'),
                "referencias": r.get('referencias') or r.get('vialidades'),
                
                "tutor": r.get('tutor_nombre'),
                "tutor_nombre": r.get('tutor_nombre'),
                "clave_elector_tutor": r.get('clave_elector_tutor') or r.get('clave_elector') or r.get('ine_responsable'),
                "telefono": r.get('telefono') or r.get('celular'),
                
                # Documentos (claves canónicas del esquema Android)
                "url_curp": r.get('url_curp'),
                "url_salud": r.get('url_salud') or r.get('url_comprobante_salud'),
                "url_ine": r.get('url_ine') or r.get('foto_ine_url') or r.get('url_ine_tutor') or r.get('url_ine_responsable'),
                "url_comprobante_domicilio": r.get('url_comprobante_domicilio'),
                "url_foto_infante": r.get('url_foto_infante'),
                
                "escuela": r.get('eaeyd_nombre') or 'No asignada',
                "eaeyd_nombre": r.get('eaeyd_nombre') or 'No asignada',
                "estatus": r.get('estatus') or 'Pendiente'
            })
        return jsonify({"desayunos": desayunos_mapeados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@espacios_eaeyd_bp.route('/<string:record_id>', methods=['GET'], strict_slashes=False)
def obtener_espacio(record_id):
    """Obtener UN espacio EAEyD específico por ID"""
    try:
        # Buscar en múltiples tablas como hace el PUT
        for table in ['desayunos_eaeyd', 'espacios_eaeyd']:
            for col in ['id', 'uuid', 'Identificación']:
                try:
                    res = global_client.table(table).select('*').eq(col, record_id).limit(1).execute()
                    if res.data:
                        r = res.data[0]
                        print(f"📍 GET /api/espacios_eaeyd/{record_id} → Encontrado en {table}")
                        
                        nombre = r.get('nombres') or r.get('nombre') or ''
                        apell = r.get('apellidos') or r.get('apellido') or ''
                        nombre_completo = f"{nombre} {apell}".strip()
                        if not nombre_completo:
                            nombre_completo = r.get('bordillo') or r.get('curp') or 'S/N'
                        
                        return jsonify({
                            "id": str(r.get('Identificación') or r.get('id') or r.get('uuid')),
                            "nombre_beneficiario": nombre_completo,
                            "nombres": nombre,
                            "apellidos": apell,
                            "curp": r.get('curp') or r.get('bordillo'),
                            "fecha_nacimiento": r.get('fecha_nacimiento') or r.get('nacimiento'),
                            "sexo": r.get('sexo') or r.get('genero'),
                            "estado_civil": r.get('estado_civil') or 'Soltero(a)',
                            "peso_menor": r.get('peso_menor') or r.get('peso'),
                            "estatura_menor": r.get('estatura_menor') or r.get('estatura') or r.get('talla'),
                            "nivel_estudios": r.get('nivel_estudios') or r.get('estudios'),
                            "ingreso_mensual": r.get('ingreso_mensual') or r.get('ingreso_familiar'),
                            "situacion_vulnerabilidad": r.get('situacion_vulnerabilidad'),
                            "localidad": r.get('localidad') or r.get('comunidad') or r.get('sede'),
                            "colonia": r.get('colonia'),
                            "tipo_asentamiento": r.get('tipo_asentamiento') or r.get('asentamiento'),
                            "municipio": r.get('municipio') or 'Acatlán',
                            "estado": r.get('estado') or 'Puebla',
                            "cp": r.get('cp') or r.get('codigo_postal'),
                            "referencias": r.get('referencias') or r.get('vialidades'),
                            "tutor": r.get('tutor_nombre') or r.get('tutor') or r.get('responsable_nombre'),
                            "clave_elector_tutor": r.get('clave_elector_tutor') or r.get('clave_elector'),
                            "telefono": r.get('telefono') or r.get('celular'),
                            "url_curp": r.get('url_curp'),
                            "url_salud": r.get('url_salud') or r.get('url_comprobante_salud'),
                            "url_ine": r.get('url_ine') or r.get('foto_ine_url') or r.get('url_ine_tutor'),
                            "url_comprobante_domicilio": r.get('url_comprobante_domicilio'),
                            "url_foto_infante": r.get('url_foto_infante'),
                            "escuela": r.get('escuela') or r.get('plantel') or 'No asignada',
                            "estatus": r.get('estatus') or 'Pendiente'
                        }), 200
                except:
                    continue
        
        return jsonify({"error": f"Espacio con ID {record_id} no encontrado"}), 404
    except Exception as e:
        print(f"❌ Error en GET /{record_id}: {e}")
        return jsonify({"error": str(e)}), 500

@espacios_eaeyd_bp.route('/<string:record_id>', methods=['PUT', 'PATCH'], strict_slashes=False)
def dictamen_registro(record_id):
    """
    Endpoint PUT/PATCH robusto para actualizar espacios EAEyD.
    Maneja JWT correctamente para pasar RLS.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No hay datos para actualizar"}), 400
    
    try:
        # Tabla e identificador confirmados; no probar aliases ni otras áreas.
        record_id = uuid_value(record_id, 'id')
        target_table = 'desayunos_eaeyd'
        id_col = 'id'
        check = global_client.table(target_table).select('id').eq(id_col, record_id).limit(1).execute()
        if not check.data:
            return jsonify(error='Registro no encontrado o no accesible.'), 404

        # Mapeo de campos (Frontend -> DB)
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
            "estatus": "estatus",
            # CAMPOS DE ARCHIVOS (URL)
            "url_curp": "url_curp",
            "url_comprobante_salud": "url_salud",
            "url_salud": "url_salud",
            "url_ine_tutor": "url_ine",
            "url_ine": "url_ine",
            "url_comprobante_domicilio": "url_comprobante_domicilio",
            "url_foto_infante": "url_foto_infante"
        }

        # Construir payload de actualización
        update_payload = {}
        for frontend_key, db_key in field_mapping.items():
            if frontend_key in data:
                update_payload[db_key] = data[frontend_key]

        if not update_payload:
            return jsonify({"error": "No se enviaron campos válidos para actualizar"}), 400

        # --- MÉTODO ROBUSTO: Usar requests.patch() con JWT para pasar RLS ---
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': 'Bearer ' + request.headers['Authorization'].split()[1],
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }

        # Ejecutar PATCH manual a REST API
        url = f"{SUPABASE_URL}/rest/v1/{target_table}?{id_col}=eq.{record_id}"
        r = requests.patch(url, json=update_payload, headers=headers, timeout=(3, 15), allow_redirects=False)
        
        if r.status_code >= 400:
            # No registrar cuerpos con información de beneficiarios.
            return jsonify(error="La base de datos rechazó la actualización."), r.status_code

        res_data = r.json()
        if not res_data:
            return jsonify({"error": "❌ Registro no actualizado. RLS activo o registro no encontrado"}), 404
            
        print(f"✅ EAEyD {record_id} actualizado en {target_table}")
        return jsonify({"message": "¡Cambios guardados exitosamente!", "data": res_data[0] if res_data else {}}), 200
        
    except ClinicalError as error:
        return jsonify(error=error.message, code=error.code), error.status
    except Exception as e:
        return jsonify(error="No se pudo completar la actualización."), 503

# ============================================================================
# NOTA: El blueprint 'espacios_eaeyd_bp' se registra en la app maestra
# ============================================================================
