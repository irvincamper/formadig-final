from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime

# Crear Blueprint para traslados
traslados_bp = Blueprint('traslados', __name__, url_prefix='/api/traslados')

from clinical.security import protect_module
from flask import g, current_app

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = protect_module(traslados_bp, ('admin', 'admin_traslados'))

@traslados_bp.route('/', methods=['GET'], strict_slashes=False)
def obtener_registros():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500
    try:
        # El guard ya comprobó el rol y vinculó el cliente al JWT verificado.
        query = supabase.table('traslados').select('*').order('fecha_solicitud', desc=True).limit(1000)

        res = query.execute()
        
        # Mapear columnas reales de DB -> JSON response (SIN FALLBACKS, SOLO CAMPOS EXACTOS)
        traslados_mapeados = []
        for r in res.data:
            traslados_mapeados.append({
                # IDs y meta
                "id": r.get('id'),
                "registrado_por": r.get('registrado_por'),
                "fecha_solicitud": r.get('fecha_solicitud'),
                # Paciente
                "paciente_nombre": r.get('paciente_nombre'),
                "paciente_curp": r.get('paciente_curp'),
                "paciente_edad": r.get('paciente_edad'),
                "paciente_domicilio": r.get('paciente_domicilio'),
                # Ubicación
                "localidad": r.get('localidad'),
                "colonia": r.get('colonia'),
                "tipo_asentamiento": r.get('tipo_asentamiento'),
                "codigo_postal": r.get('codigo_postal') or r.get('cp'),
                "referencias": r.get('referencias'),
                # Destino
                "destino_hospital": r.get('destino_hospital'),
                # Fecha y hora (exactos del schema)
                "fecha_viaje": r.get('fecha_viaje'),
                "hora_cita": r.get('hora_cita'),
                # Contacto
                "telefono_principal": r.get('telefono_principal'),
                "telefono_secundario": r.get('telefono_secundario'),
                # Acompañante
                "acompanante_nombre": r.get('acompanante_nombre'),
                "acompanante_clave_elector": r.get('acompanante_clave_elector'),
                "acompanante_entidad": r.get('acompanante_entidad'),
                # Estatus y logística
                "estatus": r.get('estatus', 'Pendiente'),
                "kilometraje_salida": r.get('kilometraje_salida'),
                "kilometraje_llegada": r.get('kilometraje_llegada'),
                # Documentos
                "url_doc_beneficiario": r.get('url_doc_beneficiario'),
                "url_doc_acompanante": r.get('url_doc_acompanante'),
                "url_foto_infante": r.get('url_foto_infante'),
                "url_comprobante_domicilio": r.get('url_comprobante_domicilio'),
                "lugares_requeridos": r.get('lugares_requeridos', 2),
            })

        # No registrar información de usuarios ni datos de solicitudes.
        return jsonify({"traslados": traslados_mapeados}), 200
    except Exception as e:
        print(f"❌ Error al obtener traslados: {e}")
        return jsonify({"error": str(e)}), 500

@traslados_bp.route('/', methods=['POST'], strict_slashes=False)
def nuevo_registro():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    required_fields = ['paciente_nombre', 'paciente_curp', 'destino_hospital', 'fecha_viaje', 'hora_cita']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"El campo '{field}' es obligatorio"}), 400

    try:
        supabase_data = {
            "registrado_por": g.web_identity["id"],
            "paciente_nombre":   data.get('paciente_nombre'),
            "paciente_curp":     data.get('paciente_curp'),
            "paciente_domicilio": data.get('paciente_domicilio'),
            "acompanante_nombre": data.get('acompanante_nombre'),
            "destino_hospital":  data.get('destino_hospital'),
            "fecha_viaje":       data.get('fecha_viaje'),
            "hora_cita":         data.get('hora_cita'),
            "telefono_principal": data.get('telefono_principal'),
            "estatus":           data.get('estatus', 'Pendiente'),
        }
        res = supabase.table('traslados').insert(supabase_data).execute()
        if res.data:
            print(f"✅ Traslado guardado: ID {res.data[0]['id']}")
        return jsonify({"message": "Traslado guardado exitosamente", "data": res.data[0] if res.data else {}}), 201
    except Exception as e:
        print(f"❌ Error al guardar traslado: {e}")
        return jsonify({"error": str(e)}), 500

@traslados_bp.route('/<string:record_id>', methods=['GET'], strict_slashes=False)
def obtener_traslado(record_id):
    """Obtener UN traslado específico por ID"""
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500
    
    try:
        target_id = int(record_id) if record_id.isdigit() else record_id
        res = supabase.table('traslados').select('*').eq('id', target_id).execute()
        
        if not res.data:
            return jsonify({"error": f"Traslado con ID {record_id} no encontrado"}), 404
        
        traslado = res.data[0]
        print(f"📍 GET /api/traslados/{record_id} → Traslado cargado: {traslado.get('paciente_nombre', 'N/A')}")
        
        return jsonify(traslado), 200
    except Exception as e:
        print(f"❌ Error al obtener traslado {record_id}: {e}")
        return jsonify({"error": str(e)}), 500

@traslados_bp.route('/<string:record_id>', methods=['PUT', 'PATCH'], strict_slashes=False)
def actualizar_traslado(record_id):
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500

    data = request.json
    try:
        target_id = int(record_id) if record_id.isdigit() else record_id

        # Mapear los datos exactamente como vienen del frontend (nombres correctos de columnas)
        update_data = {
            "paciente_nombre":     data.get('paciente_nombre'),
            "paciente_curp":       data.get('paciente_curp'),
            "paciente_domicilio":  data.get('paciente_domicilio'),
            "destino_hospital":    data.get('destino_hospital'),
            "fecha_viaje":         data.get('fecha_viaje'),
            "hora_cita":           data.get('hora_cita'),
            "telefono_principal":  data.get('telefono_principal'),
            "telefono_secundario": data.get('telefono_secundario'),
            "acompanante_clave_elector": data.get('acompanante_clave_elector'),
            "acompanante_nombre":  data.get('acompanante_nombre'),
            "estatus":             data.get('estatus', 'Programado').strip().upper() if data.get('estatus') else 'Programado'
        }
        
        # Limpiar valores None para evitar sobreescribir con nulos si no vienen en el request
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        # Extraer el JWT enviado desde el frontend
        auth_header = request.headers.get('Authorization')
        headers = {
            "apikey": SUPABASE_KEY,
            "Content-Type": "application/json",
            "Prefer": "return=representation" # Para obtener el objeto actualizado
        }
        headers['Authorization'] = auth_header
        # Conservar propietario móvil: no preasignar el registro al administrador.
        # Hacemos el parche manual para inyectar el token específico del usuario y pasar RLS
        url = f"{SUPABASE_URL}/rest/v1/traslados?id=eq.{target_id}"
        r = requests.patch(url, json=update_data, headers=headers, timeout=(3,15), allow_redirects=False)
        
        if r.status_code >= 400:
            return jsonify(error="Supabase no autorizó o no pudo completar la actualización."), r.status_code

        res_data = r.json()
        if not res_data:
            return jsonify(error="No se aplicó la actualización; verifica autorización y existencia del registro."), 409
            
        print(f"✅ Traslado actualizado ID: {target_id}")
        
        sms_status = 'not_requested'
        if update_data.get('estatus') == 'ACEPTADO':
            from clinical.sms_security import automatic_sms
            sms_status = automatic_sms(current_app._get_current_object(), auth_header.split()[1], res_data[0])

        return jsonify({"message": f"¡Traslado #{target_id} agendado correctamente!", "data": res_data[0], "sms_status": sms_status}), 200
    except Exception as e:
        print(f"❌ Error al actualizar traslado: {e}")
        return jsonify({"error": f"Error de conectividad/servidor: {str(e)}"}), 500

# ============================================================================
# NOTA: El blueprint 'traslados_bp' se registra en la app maestra
# ============================================================================
