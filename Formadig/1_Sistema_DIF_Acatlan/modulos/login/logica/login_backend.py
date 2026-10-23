from flask import Blueprint, request, jsonify
import os

# =========================================================
# 🔴 INSTALACIÓN REQUERIDA: pip install supabase
# =========================================================
try:
    from supabase import create_client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

# Cliente independiente por solicitud: ninguna sesión se comparte entre usuarios.
from clinical.repository import public_key
from clinical.security import trusted_role, request_identity
from clinical.validation import ClinicalError
from urllib.parse import urlparse


def login_client():
    missing = [name for name in ('SUPABASE_URL', 'SUPABASE_KEY')
               if not os.getenv(name, '').strip()]
    if missing:
        return None, 'Falta configuración: ' + ', '.join(missing) + '.'
    parsed = urlparse(os.environ['SUPABASE_URL'])
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.path or parsed.query or parsed.fragment):
        return None, 'SUPABASE_URL debe ser una URL HTTPS válida sin ruta ni credenciales.'
    if not public_key(os.environ['SUPABASE_KEY']):
        return None, 'SUPABASE_KEY debe ser una clave pública; no se admite una clave privilegiada.'
    try:
        return create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY']), None
    except Exception:
        return None, 'Configuración de Supabase inválida. Revisa SUPABASE_URL y SUPABASE_KEY.'

# Crear Blueprint para autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# =========================================================
# RUTA DE PRUEBA DE VIDA - Confirmamos que el backend está online
# =========================================================
@auth_bp.route('/', methods=['GET'], strict_slashes=False)
def health():
    """Endpoint de prueba - confirmamos que el backend está online."""
    return jsonify({
        "status": "backend_online",
        "message": "El backend de login está funcionando correctamente."
    }), 200

@auth_bp.route('/register', methods=['POST'], strict_slashes=False)
def register_user():
    # La ruta heredada escribe roles editables; usar Gestión de Usuarios verificada.
    return jsonify(error='Registro heredado bloqueado. Utiliza Gestión de Usuarios con una sesión administrativa verificada.'), 403


@auth_bp.route('/login', methods=['POST'], strict_slashes=False)
def login_user():
    supabase, configuration_error = login_client()
    if configuration_error:
        return jsonify(error=configuration_error, code='CONFIGURATION_ERROR'), 503

    data = request.get_json(silent=True) or {}
    if not isinstance(data, dict):
        return jsonify(error='Se requiere un objeto JSON.'), 400
    email = data.get('email')
    password = data.get('password')

    if not isinstance(email, str) or not isinstance(password, str) or not email.strip() or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    try:
        # Verifica el usuario en Supabase
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Extraemos el Token de Sesión JWT oficial
        user = supabase.auth.get_user(res.session.access_token).user if res.session else None
        session_token = res.session.access_token if res.session else None
        if not user or not session_token or getattr(user, 'is_anonymous', False):
            return jsonify(error='No se obtuvo una sesión válida.'), 401
        identity = {'id': user.id, 'is_anonymous': getattr(user, 'is_anonymous', False),
                    'app_metadata': getattr(user, 'app_metadata', None)}
        try:
            perfil_res = supabase.table('perfiles').select('id, rol, nombre_completo').eq('id', user.id).execute()
            profiles = getattr(perfil_res, 'data', [])
            profile = profiles[0] if isinstance(profiles, list) and profiles else None
            role = trusted_role(identity, profile)
            nombre_completo = profile.get('nombre_completo')
        except ClinicalError as error:
            return jsonify(error=error.message, code=error.code), error.status
        except Exception:
            return jsonify(error='No se pudo verificar el perfil autorizado.'), 503

        payload = {
            "message": "Login exitoso",
            "role": role,
            "nombre_completo": nombre_completo,
            "session": {"access_token": session_token}
        }

        return jsonify(payload), 200
        
    except Exception as e:
        # No registrar respuestas del proveedor que puedan contener datos sensibles.
        error_msg = str(e)
        if "Email not confirmed" in error_msg:
             return jsonify({"error": "Correo no confirmado. Revisa tu bandeja de entrada."}), 401
        return jsonify({"error": "No se pudo iniciar sesión. Verifica tus credenciales o intenta más tarde."}), 401

# =========================================================
# NOTA: El blueprint 'auth_bp' se registra en la app maestra
# =========================================================


@auth_bp.after_request
def private_auth_response(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@auth_bp.get('/me')
def current_identity():
    try:
        token, identity, profile, role = request_identity()
        return jsonify(role=role, nombre_completo=profile.get('nombre_completo'))
    except ClinicalError as error:
        return jsonify(error=error.message, code=error.code), error.status
    except Exception:
        return jsonify(error='No se pudo verificar la sesión.'), 503
