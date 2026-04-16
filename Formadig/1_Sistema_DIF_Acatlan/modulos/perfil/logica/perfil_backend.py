from flask import Blueprint, request, jsonify
from supabase import create_client
import os
from datetime import datetime

# Inicializar Blueprint
perfil_bp = Blueprint('perfil', __name__, url_prefix='/api/perfil')

# Inicializar Supabase CON CLAVE SERVICE ROLE (para permitir actualizaciones de Auth)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ctiqbycbkcftwuqgzxjb.supabase.co')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Como fallback si no hay service role, usamos la pública (pero no podrá cambiar contraseñas via Admin API)
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY if SUPABASE_SERVICE_ROLE_KEY else SUPABASE_KEY)

def get_auth_user(token):
    """Verifica el token y retorna el objeto de usuario."""
    try:
        res = supabase.auth.get_user(token)
        return res.user
    except Exception as e:
        print(f"Error autenticando token: {e}")
        return None

# ============================================================================
# GET / - Obtener perfil del usuario actual
# ============================================================================
@perfil_bp.route('/', methods=['GET'], strict_slashes=False)
def obtener_perfil():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No autorizado'}), 401
    
    token = auth_header.split(' ')[1]
    user = get_auth_user(token)
    
    if not user:
        return jsonify({'error': 'Sesión inválida'}), 401

    try:
        response = supabase.table('perfiles').select('*').eq('id', user.id).single().execute()
        if not response.data:
            # Si no hay perfil, devolvemos datos básicos del usuario de Auth
            return jsonify({
                'id': user.id,
                'email': user.email,
                'nombre_completo': user.user_metadata.get('nombre_completo', 'Usuario'),
                'rol': user.user_metadata.get('role', 'usuario')
            }), 200
        
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PUT / - Actualizar datos del perfil
# ============================================================================
@perfil_bp.route('/', methods=['PUT', 'PATCH'], strict_slashes=False)
def actualizar_perfil():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No autorizado'}), 401
    
    token = auth_header.split(' ')[1]
    user = get_auth_user(token)
    if not user:
        return jsonify({'error': 'Sesión inválida'}), 401

    data = request.json
    if not data:
        return jsonify({'error': 'No hay datos'}), 400

    update_data = {}
    if 'nombre_completo' in data: update_data['nombre_completo'] = data['nombre_completo']
    if 'telefono' in data: update_data['telefono'] = data['telefono']

    try:
        response = supabase.table('perfiles').update(update_data).eq('id', user.id).execute()
        return jsonify({'message': 'Perfil actualizado', 'data': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# POST /password - Cambiar contraseña
# ============================================================================
@perfil_bp.route('/password', methods=['POST'], strict_slashes=False)
def cambiar_password():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No autorizado'}), 401
    
    token = auth_header.split(' ')[1]
    # Nota: Para cambiar la contraseña del usuario actual via Admin API necesitamos Service Role
    # O podemos intentar que el propio usuario la cambie si el cliente Python soporta set_session
    
    data = request.json
    new_password = data.get('password')
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'La contraseña debe tener al menos 6 caracteres'}), 400

    try:
        # En Supabase Python, si tenemos Service Role podemos usar admin.update_user_by_id
        if SUPABASE_SERVICE_ROLE_KEY:
            user = get_auth_user(token)
            if not user: return jsonify({'error': 'Sesion invalida'}), 401
            
            supabase.auth.admin.update_user_by_id(
                user.id,
                attributes={"password": new_password}
            )
            return jsonify({'message': 'Contraseña actualizada exitosamente'}), 200
        else:
            return jsonify({'error': 'Service Role Key no configurada para cambios de seguridad'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500
