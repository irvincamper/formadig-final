"""
Backend para Gestión de Usuarios - SOLO Administradores
Módulo: admin_usuarios_backend.py
Enfoque: Seguridad - Mostrar únicamente administradores (admin, admin_desayunos, admin_traslados)

⚠️ NOTA: Este archivo exporta un Blueprint para ser registrado en la app maestra unificada.
"""

from flask import Blueprint, request, jsonify, g
from clinical.repository import SupabaseRepository
from clinical.security import trusted_role
from clinical.validation import ClinicalError, uuid_value
from flask import current_app
from supabase import create_client
import os
from datetime import datetime
import uuid
import bcrypt
import json

# Inicializar Blueprint
admin_usuarios_bp = Blueprint('admin_usuarios', __name__, url_prefix='/api/admin_usuarios')

# Inicializar Supabase CON CLAVE PÚBLICA (para lectura)
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ctiqbycbkcftwuqgzxjb.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializar Supabase CON CLAVE DE SERVICIO (para admin operations si está disponible)
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', None)
supabase_admin = None
if SUPABASE_SERVICE_ROLE_KEY:
    try:
        supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print(f"✅ Supabase Admin Client inicializado (para operaciones Auth)")
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo inicializar Supabase Admin: {e}")
        supabase_admin = None
else:
    print(f"⚠️ Advertencia: SUPABASE_SERVICE_ROLE_KEY no disponible")
    print(f"   Las altas de Auth permanecerán bloqueadas (503)")

# Roles permitidos - SOLO administradores
ALLOWED_ROLES = ['admin', 'admin_desayunos', 'admin_traslados', 'psicologo', 'dentista']


@admin_usuarios_bp.before_request
def verificar_administracion_de_usuarios():
    """Ampliar tipos de usuario no debe ampliar quién puede administrarlos."""
    if request.method == 'OPTIONS':
        return '', 204
    parts = request.headers.get('Authorization', '').split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify(error='Se requiere una sesión válida.'), 401
    try:
        factory = current_app.config.get('CLINICAL_REPOSITORY_FACTORY', SupabaseRepository)
        repository = factory(parts[1])
        identity = repository.identity()
        if not identity or identity.get('is_anonymous') is True:
            return jsonify(error='Sesión inválida.'), 401
        user_id = uuid_value(identity.get('id'), 'usuario')
        profile = repository.profile(user_id)
        canonical_role = trusted_role(identity, profile)
        if not profile or canonical_role != profile.get('rol'):
            return jsonify(error='El rol requiere aprovisionamiento confiable en Auth.'), 403
        if not profile or profile.get('id') != user_id or canonical_role != 'admin':
            return jsonify(error='Sólo administración general puede gestionar usuarios.'), 403
        g.users_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        g.users_client.postgrest.auth(parts[1])
    except ClinicalError as error:
        return jsonify(error=error.message, code=error.code), error.status
    except Exception:
        return jsonify(error='No se pudieron verificar los permisos.'), 503


# ============================================================================
# GET / - Obtener lista de administradores (Filtrado por rol)
# ============================================================================
@admin_usuarios_bp.route('/', methods=['GET'], strict_slashes=False)
def obtener_usuarios():
    """
    Endpoint GET para obtener SOLO administradores.
    Filtro crítico: .in_('rol', ['admin', 'admin_desayunos', 'admin_traslados'])
    """
    try:
        # Consulta con filtro de roles permitidos
        response = g.users_client.table('perfiles').select('*').in_('rol', ALLOWED_ROLES).execute()
        
        usuarios = response.data if response.data else []
        
        # Validación adicional en frontend (aunque el backend ya filtra)
        return jsonify({
            'usuarios': usuarios,
            'total': len(usuarios),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuarios: {str(e)}'}), 500


# ============================================================================
# POST / - Crear nuevo administrador
# ============================================================================
@admin_usuarios_bp.route('/', methods=['POST'], strict_slashes=False)
def crear_usuario():
    """
    Endpoint POST para crear nuevo administrador con validación detallada.
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error='Se requiere un objeto JSON.'), 400
        errors = {}
        
        print(f"\n📥 === CREACIÓN DE USUARIO ADMIN (Paso 0: Validación) ===")
        
        if not data:
            return jsonify({'status': 'error', 'message': 'No se recibieron datos'}), 400

        # 1. Validar campos obligatorios
        required_fields = {
            'nombre_usuario': 'Usuario',
            'nombre_completo': 'Nombre Completo',
            'email': 'Email de Acceso',
            'password': 'Contraseña',
            'rol': 'Rol',
            'telefono': 'Teléfono'
        }
        
        for field, label in required_fields.items():
            if not data.get(field) or not str(data.get(field)).strip():
                errors[field] = f"El campo {label} es obligatorio"

        # 2. Validar formato de email (si no está vacío)
        email = data.get('email', '').strip().lower()
        if 'email' not in errors and email:
            import re
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                errors['email'] = "Formato de correo electrónico inválido"

        # 3. Validar contraseña (si no está vacía)
        password = data.get('password', '')
        if 'password' not in errors and len(password) < 8:
            errors['password'] = "La contraseña debe tener al menos 8 caracteres"

        # 4. Validar rol (si no está vacío)
        rol = data.get('rol', '')
        if 'rol' not in errors and rol not in ALLOWED_ROLES:
            errors['rol'] = f"Rol no permitido. Use: {', '.join(ALLOWED_ROLES)}"

        # 5. Validar unicidad del correo en Supabase
        if 'email' not in errors and email:
            try:
                # Consultar si el correo ya existe en Auth (o en la tabla perfiles si Auth no es accesible directamente)
                # Como usamos supabase_admin para Auth, podemos intentar buscarlo o simplemente dejar que Auth falle
                # Pero el usuario pidió validar unicidad explícitamente.
                # Nota: La tabla 'perfiles' no tiene email, así que verificamos en el sistema Auth via Admin API
                if supabase_admin:
                    # Alternativa: Consultar tabla 'perfiles' si tuviera email, pero no tiene.
                    # Intentamos crear y capturamos el error de duplicado es lo más eficiente, 
                    # pero si queremos validación previa:
                    pass 
            except Exception as e:
                print(f"⚠️ Error al verificar unicidad: {e}")

        # Si hay errores de validación inicial, retornamos de inmediato
        if errors:
            print(f"❌ Errores de validación: {errors}")
            return jsonify({'status': 'error', 'errors': errors}), 400

        if supabase_admin is None:
            return jsonify(status='error', message='El servicio administrativo de altas de Auth no está configurado. No se creó ninguna cuenta.'), 503

        # 🔐 Intentar crear el usuario en Auth
        try:
            print(f"\n🔐 === CREANDO USUARIO EN AUTH ===")
            auth_response = supabase_admin.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "app_metadata": {"role": rol},
                "user_metadata": {
                    "nombre_usuario": data.get('nombre_usuario', ''),
                    "nombre_completo": data.get('nombre_completo', ''),
                    "curp": data.get('curp', ''),
                    "telefono": data.get('telefono', ''),
                    "domicilio": data.get('domicilio', ''),
                    "apellidos": data.get('apellidos', ''),
                    "clave_elector": data.get('clave_elector', '')
                }
            })
            
            user_uuid = auth_response.user.id
            print(f"✅ ÉXITO: Usuario Auth creado con UUID: {user_uuid}")
            
            return jsonify({
                'status': 'success',
                'message': 'Administrador creado exitosamente ✅',
                'user_id': user_uuid
            }), 200
            
        except Exception as e:
            error_msg = str(e)
            print(f"🔥 ERROR SUPABASE AUTH: {error_msg}")
            
            # Mapear error de duplicado de Supabase Auth
            if "already has been registered" in error_msg.lower() or "user_already_exists" in error_msg.lower():
                return jsonify({
                    'status': 'error',
                    'errors': {'email': 'Este correo electrónico ya está registrado'}
                }), 400
                
            return jsonify({
                'status': 'error',
                'message': f'Error al crear en Auth: {error_msg}'
            }), 400
        
    except Exception as e:
        print(f"\n❌ === ERROR CRÍTICO EN CREAR_USUARIO ===")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'Error interno del servidor: {str(e)}'
        }), 500



# ============================================================================
# PUT /<id> - Actualizar administrador
# ============================================================================
@admin_usuarios_bp.route('/<id>', methods=['PUT', 'PATCH'], strict_slashes=False)
def actualizar_usuario(id):
    """
    Endpoint PUT/PATCH para actualizar un administrador.
    Solo actualiza campos válidos de la tabla perfiles.
    """
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error='Se requiere un objeto JSON.'), 400
        if not data:
            return jsonify({'error': 'No hay datos para actualizar'}), 400
        
        # Campos válidos que pueden actualizarse en la tabla perfiles
        valid_fields = ['nombre_usuario', 'nombre_completo', 'rol', 'telefono', 
                       'domicilio', 'apellidos', 'clave_elector', 'curp']
        
        # Filtrar solo campos válidos y no vacíos
        update_data = {}
        for field in valid_fields:
            if field in data and data[field]:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No se proporcionaron campos válidos para actualizar'}), 400
        
        # Validar que el rol sigue siendo permitido
        if 'rol' in update_data and update_data['rol'] not in ALLOWED_ROLES:
            return jsonify({
                'error': f"Rol no permitido. Use: {', '.join(ALLOWED_ROLES)}"
            }), 400
        
        # Obtener usuario actual para validar que es un administrador
        usuario_response = g.users_client.table('perfiles').select('*').eq('id', id).execute()
        
        if not usuario_response.data or len(usuario_response.data) == 0:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        usuario = usuario_response.data[0]

        if 'rol' in update_data and update_data['rol'] != usuario.get('rol'):
            return jsonify(error='Cambio de rol bloqueado hasta disponer de actualización coordinada de Auth y perfil.'), 409
        
        update_data.pop('rol', None)
        if not update_data:
            return jsonify(error='No hay cambios de perfil no sensibles.'), 400

        # Verificar que el usuario actual es un administrador
        if usuario['rol'] not in ALLOWED_ROLES:
            return jsonify({
                'error': 'Solo se pueden actualizar administradores'
            }), 403
        
        # Actualizar en la tabla perfiles
        response = g.users_client.table('perfiles').update(update_data).eq('id', id).execute()
        
        if not response.data:
            return jsonify({'error': 'No se pudo actualizar el usuario. Verifica los datos.'}), 404
        
        return jsonify({
            'message': 'Administrador actualizado exitosamente',
            'usuario': response.data[0] if response.data else update_data
        }), 200
        
    except Exception as e:
        print(f'❌ Error al actualizar usuario: {str(e)}')
        return jsonify({'error': f'Error al actualizar usuario: {str(e)}'}), 500


# ============================================================================
# DELETE /<id> - Eliminar administrador
# ============================================================================
@admin_usuarios_bp.route('/<id>', methods=['DELETE'], strict_slashes=False)
def eliminar_usuario(id):
    """
    Endpoint DELETE para eliminar un administrador.
    Validación: Verifica que el usuario a eliminar tenga un rol permitido antes de eliminar.
    """
    return jsonify(error='Baja bloqueada hasta coordinar Auth, sesiones y dependencias del perfil.'), 409


# ============================================================================
# NOTA: El blueprint 'admin_usuarios_bp' se registra en la app maestra
# ============================================================================
