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
# Sólo clave pública y JWT verificado por petición; sin fallback privilegiado.
from clinical.security import protect_module
from flask import g

@sms_bp.before_request
def restrict_callback():
    if request.path.rstrip('/').endswith('/webhook'):
        from clinical.sms_security import receive_webhook
        return receive_webhook()

supabase = protect_module(sms_bp, ('admin','admin_traslados','psicologo','dentista'), restrict_tables=True)

# Configuración Twilio
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

@sms_bp.route('/send', methods=['POST'], strict_slashes=False)
def send_sms():
    data = request.json
    phone = data.get('phone')
    message_text = data.get('message')
    registrado_por = g.web_identity['id']

    if not phone or not message_text:
        return jsonify({"error": "Teléfono y mensaje son obligatorios"}), 400

    # Normalizar teléfono (Asegurar +52 para México si no tiene prefijo)
    if not phone.startswith('+'):
        phone = f"+52{phone}"

    status = "Enviado"
    error_msg = None

   # --- MODO SIMULACIÓN / REAL ---
    # Si las credenciales empiezan con AC_ o están vacías, usamos Mock
    is_mock = (not TWILIO_ACCOUNT_SID or
               TWILIO_ACCOUNT_SID.startswith('AC_TU_') or
               'TwilioClient' not in globals())

    if is_mock:
        print("[MOCK SMS] Ensayo sin envío externo")
        # Simulamos éxito
    else:
        try:
            client = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            # Usar la API de Messaging en lugar de Verify
            message = client.messages.create(
                body=message_text,
                from_=TWILIO_PHONE_NUMBER,
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
    return jsonify(error='El callback sólo se procesa mediante el receptor seguro.'), 503

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
