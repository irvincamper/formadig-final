from flask import Blueprint, request, jsonify
import json
import os
import requests
import base64

# Lógica de Backend de Python - Espacios EAEyD (ROBUSTO CON JWT)
# Crear Blueprint para espacios EAEyD
espacios_eaeyd_bp = Blueprint('espacios_eaeyd', __name__, url_prefix='/api/espacios_eaeyd')

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")
global_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@espacios_eaeyd_bp.route('/', methods=['GET'])
def obtener_registros():
    try:
        candidate_tables = ['desayunos_eaeyd', 'espacios_eaeyd']
        responses = []
        for table in candidate_tables:
            try:
                res = global_client.table(table).select('*').limit(1000).eq('tipo_apoyo', 'EAEyD').execute()
                responses.extend(res.data)
            except: continue
        
        desayunos_mapeados = []
        for r in responses:
            record_id = r.get('Identificación') or r.get('id') or r.get('uuid')
            nombre = r.get('nombres') or r.get('nombre') or r.get('nombre_beneficiario') or ''
            apell = r.get('apellidos') or r.get('apellido') or ''
            nombre_completo = f"{nombre} {apell}".strip()
            if not nombre_completo:
                nombre_completo = r.get('bordillo') or r.get('curp') or f"EAEyD #{str(record_id)[:8] if record_id else '?'}"
            
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
                "localidad": r.get('localidad') or r.get('comunidad') or r.get('sede'),
                "tipo_asentamiento": r.get('tipo_asentamiento') or 'Colonia',
                "cp": r.get('cp') or r.get('codigo_postal'),
                "referencias": r.get('referencias') or r.get('vialidades'),
                
                # Responsable (usado el mismo mapeo de tutor por consistencia en JS)
                "tutor": r.get('tutor_nombre') or r.get('tutor') or r.get('responsable_nombre'),
                "clave_elector_tutor": r.get('clave_elector_tutor') or r.get('clave_elector') or r.get('ine_responsable'),
                "telefono": r.get('telefono') or r.get('celular'),
                
                # Documentos
                "url_curp": r.get('url_curp') or r.get('url_doc_curp') or r.get('curp_url'),
                "url_comprobante_salud": r.get('url_comprobante_salud') or r.get('url_doc_salud') or r.get('url_salud'),
                "url_ine_tutor": r.get('url_ine_tutor') or r.get('url_doc_ine_tutor') or r.get('url_ine_responsable') or r.get('url_ine') or r.get('foto_ine_url'),
                "url_comprobante_domicilio": r.get('url_comprobante_domicilio') or r.get('comprobante_domicilio') or r.get('url_comprobante'),
                "url_foto_infante": r.get('url_foto_infante') or r.get('foto_infante') or r.get('url_foto'),
                
                "escuela": r.get('escuela') or r.get('plantel') or 'No asignada',
                "estatus": r.get('estatus') or 'Pendiente'
            })
        return jsonify({"desayunos": desayunos_mapeados}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@espacios_eaeyd_bp.route('/<string:record_id>', methods=['GET'])
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
                            "tipo_asentamiento": r.get('tipo_asentamiento') or 'Colonia',
                            "cp": r.get('cp') or r.get('codigo_postal'),
                            "referencias": r.get('referencias') or r.get('vialidades'),
                            "tutor": r.get('tutor_nombre') or r.get('tutor') or r.get('responsable_nombre'),
                            "clave_elector_tutor": r.get('clave_elector_tutor') or r.get('clave_elector'),
                            "telefono": r.get('telefono') or r.get('celular'),
                            "url_curp": r.get('url_curp') or r.get('url_doc_curp'),
                            "url_comprobante_salud": r.get('url_comprobante_salud') or r.get('url_doc_salud'),
                            "url_ine_tutor": r.get('url_ine_tutor') or r.get('url_doc_ine_tutor'),
                            "url_comprobante_domicilio": r.get('url_comprobante_domicilio'),
                            "url_foto_infante": r.get('url_foto_infante') or r.get('foto_infante'),
                            "escuela": r.get('escuela') or r.get('plantel') or 'No asignada',
                            "estatus": r.get('estatus') or 'Pendiente'
                        }), 200
                except:
                    continue
        
        return jsonify({"error": f"Espacio con ID {record_id} no encontrado"}), 404
    except Exception as e:
        print(f"❌ Error en GET /{record_id}: {e}")
        return jsonify({"error": str(e)}), 500

@espacios_eaeyd_bp.route('/<string:record_id>', methods=['PUT', 'PATCH'])
def dictamen_registro(record_id):
    """
    Endpoint PUT/PATCH robusto para actualizar espacios EAEyD.
    Maneja JWT correctamente para pasar RLS.
    """
    data = request.json
    if not data:
        return jsonify({"error": "No hay datos para actualizar"}), 400
    
    try:
        # Determinar tabla y columna de ID
        target_table = None
        id_col = None
        
        for table in ['desayunos_eaeyd', 'espacios_eaeyd']:
            for col in ['id', 'uuid', 'Identificación']:
                try:
                    check = global_client.table(table).select('*').eq(col, record_id).limit(1).execute()
                    if check.data:
                        target_table = table
                        id_col = col
                        break
                except:
                    continue
            if target_table:
                break
        
        if not target_table:
            return jsonify({"error": "No se encontró el registro para actualizar"}), 404

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
            "url_comprobante_salud": "url_comprobante_salud",
            "url_ine_tutor": "url_ine_tutor",
            "url_comprobante_domicilio": "url_comprobante_domicilio",
            "url_foto_infante": "url_foto_infante"
        }

        # Construir payload de actualización
        update_payload = {}
        for frontend_key, db_key in field_mapping.items():
            if frontend_key in data:
                update_payload[db_key] = data[frontend_key]

        if 'situacion_vulnerabilidad' in data:
            update_payload['situacion_vulnerabilidad'] = data['situacion_vulnerabilidad']

        if not update_payload:
            return jsonify({"error": "No se enviaron campos válidos para actualizar"}), 400

        # --- MÉTODO ROBUSTO: Usar requests.patch() con JWT para pasar RLS ---
        auth_header = request.headers.get('Authorization')
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        if auth_header and auth_header.startswith('Bearer '):
            headers["Authorization"] = auth_header
            # Extraer UUID del token JWT para inyectar en el registro
            try:
                token = auth_header.split(' ')[1]
                payload = token.split('.')[1]
                pad = '=' * (-len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload + pad).decode('utf-8'))
                admin_uuid = decoded.get('sub')
                
                # Pre-patch para asignar usuario si no existe
                url_get = f"{SUPABASE_URL}/rest/v1/{target_table}?select={id_col}&{id_col}=eq.{record_id}"
                rg = requests.get(url_get, headers={"apikey": SUPABASE_KEY, "Authorization": auth_header})
                if rg.status_code == 200 and rg.json():
                    if not rg.json()[0].get('usuario_admin'):
                        url_patch = f"{SUPABASE_URL}/rest/v1/{target_table}?{id_col}=eq.{record_id}"
                        requests.patch(url_patch, json={'usuario_admin': admin_uuid}, headers=headers, proxies={"http": None, "https": None})
            except Exception as e:
                print(f"⚠️ Advertencia parseando JWT: {e}")
        else:
            headers["Authorization"] = f"Bearer {SUPABASE_KEY}"  # Fallback

        # Ejecutar PATCH manual a REST API
        url = f"{SUPABASE_URL}/rest/v1/{target_table}?{id_col}=eq.{record_id}"
        r = requests.patch(url, json=update_payload, headers=headers, proxies={"http": None, "https": None})
        
        if r.status_code >= 400:
            print(f"❌ Supabase error: {r.text}")
            return jsonify({"error": f"Supabase rechazó la operación: {r.text}"}), r.status_code

        res_data = r.json()
        if not res_data:
            return jsonify({"error": "❌ Registro no actualizado. RLS activo o registro no encontrado"}), 404
            
        print(f"✅ EAEyD {record_id} actualizado en {target_table}")
        return jsonify({"message": "¡Cambios guardados exitosamente!", "data": res_data[0] if res_data else {}}), 200
        
    except Exception as e:
        print(f"❌ Error crítico en PUT: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================================================
# NOTA: El blueprint 'espacios_eaeyd_bp' se registra en la app maestra
# ============================================================================
