from dotenv import load_dotenv
load_dotenv()
from flask import Blueprint, request, jsonify
import os
from datetime import datetime

try:
    from flask_cors import CORS
except ImportError:
    print("AVISO: flask-cors no encontrado. Instalando o simulando...")
    CORS = None

try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    print("AVISO: 'pip install twilio' no encontrado. El modo real de SMS no funcionará.")

# Crear Blueprint para SMS
sms_bp = Blueprint('sms', __name__, url_prefix='/api/sms')

@sms_bp.route('/ping', methods=['GET'], strict_slashes=False)
def ping():
    return jsonify({
        "status": "online",
        "message": "SMS Backend DIF Acatlan is running",
        "port": 5009
    })

# =========================================================
# 🏗️ CONFIGURACIÓN (REEMPLAZAR CON TUS CLAVES)
# =========================================================
# Conexión Supabase (Uso de SERVICE_ROLE_KEY para bypass RLS)
SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

# Configuración Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

try:
    # Se prefiere SERVICE_ROLE_KEY para evitar errores 42501 (RLS) en backend
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
except Exception as e:
    print(f"Error Supabase: {e}")
    supabase = None

@sms_bp.route('/send', methods=['POST'], strict_slashes=False)
def send_sms():
    data = request.json
    phone = data.get('phone')
    message_text = data.get('message')
    registrado_por = data.get('user_id', 'anonimo')

    if not phone or not message_text:
        return jsonify({"error": "Teléfono y mensaje son obligatorios"}), 400

    # Normalizar teléfono (Asegurar +52 para México si no tiene prefijo)
    if not phone.startswith('+'):
        phone = f"+52{phone}"

    status = "Enviado"
    error_msg = None
    
    # --- MODO SIMULACIÓN / REAL ---
    # Si las credenciales empiezan con AC_ o están vacías, usamos Mock
    is_mock = (TWILIO_ACCOUNT_SID.startswith('AC_TU_') or 
               not TWILIO_ACCOUNT_SID or 
               'TwilioClient' not in globals())
    
    if is_mock:
        print(f"[MOCK SMS] Enviando a {phone}: {message_text}")
        # Simulamos éxito
    else:
        try:
            client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            # Usar la API de Messaging en lugar de Verify
            message = client.messages.create(
                body=message_text,
                from_="+14786661928",
                to=phone
            )
            status = "Enviado"
            print(f"SMS Messaging enviado. SID: {message.sid}")
        except Exception as e:
            status = "Error"
            error_msg = str(e)
            print(f"Error enviando SMS: {e}")

    # LOGUEO EN SUPABASE (Historial para el DIF)
    if supabase:
        try:
            # Usar fecha formateada con zona horaria (mínimo Z) o dejar que la DB la gestione
            log_data = {
                "fecha": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "telefono": phone,
                "mensaje": message_text,
                "estatus": status,
                "error": error_msg,
                "enviado_por": registrado_por
            }
            res = supabase.table('sms_logs').insert(log_data).execute()
            
            if hasattr(res, 'error') and res.error:
                print(f"❌ ERROR DB: {res.error}")
            else:
                print(f"✅ Log guardado en Supabase (ID: {res.data[0].get('id') if res.data else 'N/A'})")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO AL GUARDAR LOG: {e}")

    return jsonify({
        "message": "Operación completada",
        "status": status,
        "mode": "Mock" if is_mock else "Real",
        "error": error_msg
    })

@sms_bp.route('/history', methods=['GET'], strict_slashes=False)
def get_history():
    if not supabase:
        return jsonify({"error": "Sin conexión a DB"}), 500
    
    try:
        res = supabase.table('sms_logs').select("*").order('fecha', desc=True).limit(50).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sms_bp.route('/traslados', methods=['GET'], strict_slashes=False)
def get_traslados_for_sms():
    if not supabase:
        return jsonify({"error": "Sin conexión a DB"}), 500
    try:
        from datetime import date
        hoy = date.today().isoformat()  # 'YYYY-MM-DD'
        response = supabase.table('traslados') \
            .select('id, paciente_nombre, telefono_principal, fecha_viaje, hora_cita, estatus, destino_hospital') \
            .eq('estatus', 'ACEPTADO') \
            .gte('fecha_viaje', hoy) \
            .order('fecha_viaje', desc=False) \
            .execute()

        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@sms_bp.route('/webhook', methods=['POST'], strict_slashes=False)
def sms_webhook():
    incoming_msg = request.values.get('Body', '').strip().upper()
    sender_phone = request.values.get('From', '') # p.ej. +52775...
    
    print(f"📥 Webhook SMS Recibido de {sender_phone}: {incoming_msg}")
    
    if supabase:
        try:
            # 1. Registrar el mensaje entrante directo en el Historial de SMS
            log_data = {
                "fecha": datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
                "telefono": sender_phone,
                "mensaje": f"[Respuesta del Ciudadano]: {incoming_msg}",
                "estatus": "Recibido",
                "enviado_por": "Paciente"
            }
            res_log = supabase.table('sms_logs').insert(log_data).execute()
            if hasattr(res_log, 'error') and res_log.error:
                print(f"❌ Error al guardar log del webhook: {res_log.error}")

            # 2. Buscar el registro más reciente en estado ACEPTADO que coincida con el teléfono
            # Importante: Como no podemos hacer un OR complejo fácil en select, traemos los recientes
            res = supabase.table('traslados').select('id, telefono_principal, telefono_secundario').eq('estado', 'ACEPTADO').execute()

            
            target_id = None
            local_phone = sender_phone.replace('+52', '').replace('+1', '') # Por si en DB no tiene lada
            
            for r in res.data:
                t1 = str(r.get('telefono_principal') or '')
                t2 = str(r.get('telefono_secundario') or '')
                if sender_phone in t1 or local_phone in t1 or sender_phone in t2 or local_phone in t2:
                    target_id = r['id']
                    break
                    
            if target_id:
                if incoming_msg in ['SI', 'SÍ', 'S', 'YES', 'CONFIRMO']:
                    supabase.table('traslados').update({'estado': 'CONFIRMADO'}).eq('id', target_id).execute()
                    print(f"✅ Webhook: Traslado {target_id} CONFIRMADO.")
                elif incoming_msg in ['NO', 'N', 'CANCELAR', 'RECHAZO']:
                    supabase.table('traslados').update({'estado': 'RECHAZADO'}).eq('id', target_id).execute()
                    print(f"❌ Webhook: Traslado {target_id} RECHAZADO por el usuario.")
            else:
                print(f"⚠️ Webhook: No se encontró un traslado ACEPTADO para el número {sender_phone}.")

        except Exception as e:
            print(f"❌ Webhook BD Error: {e}")

    # Respuesta neutra para el webhook
    return '<?xml version="1.0" encoding="UTF-8"?><Response></Response>', 200, {'Content-Type': 'application/xml'}

# ============================================================================
# NOTA: El blueprint 'sms_bp' se registra en la app maestra
# ============================================================================

if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    try:
        from flask_cors import CORS
        CORS(app)
    except ImportError:
        pass
        
    app.register_blueprint(sms_bp)
    
    port = int(os.environ.get("PORT", 5009))
    print(f"Iniciando SMS Web Service en el puerto {port}...")
    app.run(host='0.0.0.0', port=port)
