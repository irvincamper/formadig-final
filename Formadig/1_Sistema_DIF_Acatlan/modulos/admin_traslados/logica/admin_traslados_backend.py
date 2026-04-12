from flask import Blueprint, request, jsonify
import requests
import os
from datetime import datetime

# Crear Blueprint para traslados
traslados_bp = Blueprint('traslados', __name__, url_prefix='/api/traslados')

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL o SUPABASE_KEY no configuradas en variables de entorno")
    raise RuntimeError("Supabase credentials not configured")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Conectado a Supabase - Traslados")
except Exception as e:
    print(f"ATENCIÓN: Error conectando a Supabase: {e}")
    supabase = None

@traslados_bp.route('/', methods=['GET'], strict_slashes=False)
def obtener_registros():
    if not supabase:
        return jsonify({"error": "Supabase no configurado"}), 500
    try:
        # Obtener rol y email del usuario desde headers
        user_email = request.headers.get('X-User-Email', '')
        user_role = request.headers.get('X-User-Role', '').strip().lower()
        
        print(f"📋 GET /api/traslados → user_email={user_email}, user_role={user_role}")
        
        # Determinar si es admin o usuario normal
        is_admin = user_role in ['admin', 'admin_traslados', 'directora', 'desarrollador']
        
        # Construir la consulta base
        query = supabase.table('traslados').select('*').order('fecha_solicitud', desc=True).limit(1000)
        
        # Si NO es admin, filtrar por registrado_por usando el email del usuario
        if not is_admin and user_email:
            try:
                # Buscar el ID del usuario en la tabla perfiles usando el email
                perfil_res = supabase.table('perfiles').select('id').eq('nombre_usuario', user_email).execute()
                perfil_data = getattr(perfil_res, 'data', [])
                
                if perfil_data and len(perfil_data) > 0:
                    user_id = perfil_data[0].get('id')
                    print(f"🔍 Usuario encontrado: email={user_email}, id={user_id}")
                    query = query.eq('registrado_por', user_id)
                else:
                    print(f"⚠️ Usuario {user_email} no encontrado en perfiles, sin registros para mostrar")
                    return jsonify({"traslados": []}), 200
            except Exception as e:
                print(f"❌ Error buscando usuario en perfiles: {e}")
                # Si hay error, retornar lista vacía para no exponer datos
                return jsonify({"traslados": []}), 200
        
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

        print(f"✅ Retornando {len(traslados_mapeados)} registros (admin={is_admin}, user={user_email})")
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
        if auth_header and auth_header.startswith('Bearer '):
            headers["Authorization"] = auth_header
            # Extraer UUID del Token para inyectarlo y evitar crash del trigger si es null
            try:
                import base64, json
                token = auth_header.split(' ')[1]
                payload = token.split('.')[1]
                pad = '=' * (-len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload + pad).decode('utf-8'))
                admin_uuid = decoded.get('sub')
                
                # Fetch el registro actual para ver si le falta el usuario (registros de adm)
                url_get = f"{SUPABASE_URL}/rest/v1/traslados?select=registrado_por&id=eq.{target_id}"
                rg = requests.get(url_get, headers={"apikey": SUPABASE_KEY, "Authorization": auth_header})
                if rg.status_code == 200 and rg.json():
                    if not rg.json()[0].get('registrado_por'):
                        # PRE-PATCH: Asignar usuario primero sin tocar estatus para que OLD.registrado_por ya no sea null
                        url_patch = f"{SUPABASE_URL}/rest/v1/traslados?id=eq.{target_id}"
                        requests.patch(url_patch, json={'registrado_por': admin_uuid}, headers=headers, proxies={"http": None, "https": None})
            except Exception as e:
                print(f"Error parseando JWT / Pre-Patch: {e}")
        else:
            headers["Authorization"] = f"Bearer {SUPABASE_KEY}" # Fallback anon key

        # Hacemos el parche manual para inyectar el token específico del usuario y pasar RLS
        url = f"{SUPABASE_URL}/rest/v1/traslados?id=eq.{target_id}"
        r = requests.patch(url, json=update_data, headers=headers, proxies={"http": None, "https": None})
        
        if r.status_code >= 400:
            return jsonify({"error": f"Supabase rechazó la operación: {r.text}"}), r.status_code

        res_data = r.json()
        if not res_data:
            return jsonify({"error": "⚠️ BLOQUEADO POR SUPABASE: La tabla 'traslados' tiene activado el Row Level Security (RLS) que impide actualizar registros. Ve a tu panel de Supabase > Authentication > Policies y crea una política UPDATE, o desactiva RLS."}), 404
            
        print(f"✅ Traslado actualizado ID: {target_id}")
        
        # --- DISPARAR SMS AUTOMÁTICO AL ACEPTAR ---
        if update_data.get('estatus') == 'ACEPTADO':
            try:
                rec = res_data[0]
                tel = rec.get('telefono_principal') or rec.get('telefono_secundario')
                fecha_v = rec.get('fecha_viaje', '')
                hora_c = rec.get('hora_cita', '')
                if tel:
                    msg_texto = f"DIF Acatlan: Tu traslado esta programado el dia {fecha_v} a las {hora_c}. ¿Confirmas que asistiras ese dia y a la hora acordada? Responde SI o NO."
                    
                    def enviar_sms_async(telefono, mensaje):
                        try:
                            requests.post('http://localhost:5009/api/sms/send', json={
                                'phone': telefono,
                                'message': mensaje,
                                'user_id': 'Bot Traslados'
                            }, timeout=5)
                        except Exception as e:
                            print(f"Error enviando SMS asíncrono: {e}")
                            
                    import threading
                    threading.Thread(target=enviar_sms_async, args=(tel, msg_texto)).start()
                    print(f"📲 Auto-SMS de confirmación disparado para {tel}")
            except Exception as e:
                print(f"Error procesando auto-SMS: {e}")

        return jsonify({"message": f"¡Traslado #{target_id} agendado correctamente!", "data": res_data[0]}), 200
    except Exception as e:
        print(f"❌ Error al actualizar traslado: {e}")
        return jsonify({"error": f"Error de conectividad/servidor: {str(e)}"}), 500

# ============================================================================
# NOTA: El blueprint 'traslados_bp' se registra en la app maestra
# ============================================================================
