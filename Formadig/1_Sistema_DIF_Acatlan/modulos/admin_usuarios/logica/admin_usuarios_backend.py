"""
Backend para Gestión de Usuarios - SOLO Administradores
Módulo: admin_usuarios_backend.py
Enfoque: Seguridad - Mostrar únicamente administradores (admin, admin_desayunos, admin_traslados)

⚠️ NOTA: Este archivo exporta un Blueprint para ser registrado en la app maestra unificada.
"""

from flask import Blueprint, request, jsonify
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
    print(f"   Los usuarios se crearán directamente en tabla (sin Auth)")

# Roles permitidos - SOLO administradores
ALLOWED_ROLES = ['admin', 'admin_desayunos', 'admin_traslados']


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
        response = supabase.table('perfiles').select('*').in_('rol', ALLOWED_ROLES).execute()
        
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
    Endpoint POST para crear nuevo administrador.
    
    FLUJO CRÍTICO DE DOS PASOS:
    1️⃣  Crear usuario en Supabase Auth (email/password) → obtiene UUID
    2️⃣  Insertar en tabla perfiles CON id=UUID (SIN email ni password)
    
    JSON ESPERADO DEL FRONTEND:
    {
        "nombre_usuario": "director",           // Campo 'Usuario' del form
        "nombre_completo": "Juan García López", // Campo 'Nombre Completo'
        "email": "juan@example.com",            // Campo 'Email de Acceso'
        "password": "MiPassword123",            // Campo 'Contraseña Temporal'
        "rol": "admin",                         // Campo 'Rol' (admin, admin_desayunos, admin_traslados)
        "telefono": "5551234567",               // Campo 'Teléfono'
        "curp": "XXXX000000HXXXXXX00" (opt),   // Optional
        "apellidos": "García López" (opt),      // Optional
        "domicilio": "Calle 123" (opt)          // Optional
    }
    
    ⚠️ IMPORTANTE:
    - Los campos 'email' y 'password' SOLO se usan para crear en Auth.users
    - La tabla 'perfiles' NO tiene columnas email ni password
    - Asegúrate de que el frontend mapea correctamente los nombres de campos
    """
    try:
        data = request.json
        
        print(f"\n📥 === CREACIÓN DE USUARIO ADMIN (Paso 0: Validación) ===")
        print(f"📦 JSON recibido: {data}")
        print(f"📋 Claves recibidas: {list(data.keys()) if data else 'VACÍO'}")
        
        # Validar que se proporcionan los campos requeridos (PASO 0)
        required_fields = ['nombre_usuario', 'nombre_completo', 'email', 'password', 'rol', 'telefono']
        for field in required_fields:
            valor = data.get(field) if data else None
            print(f"   - {field}: {'✅' if valor else '❌'} (valor: {valor})")
            if field not in data or not data[field]:
                print(f"❌ Campo requerido faltante: {field}")
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        
        # Validación crítica: ROL debe estar en la lista permitida
        if data['rol'] not in ALLOWED_ROLES:
            print(f"❌ Rol no permitido: {data['rol']}")
            return jsonify({
                'error': f"Rol no permitido. Use: {', '.join(ALLOWED_ROLES)}"
            }), 400
        
        print(f"✅ PASO 0: Validaciones pasadas")
        
        # 🔐 CREAR USUARIO EN SUPABASE AUTH CON METADATA
        # El Trigger de Supabase automáticamente insertará en tabla perfiles
        try:
            print(f"\n🔐 === CREANDO USUARIO EN AUTH (con user_metadata) ===")
            print(f"Email: {data['email'].strip().lower()}")
            print(f"Password: {'*' * len(data['password'])} ({len(data['password'])} caracteres)")
            
            auth_response = supabase_admin.auth.admin.create_user({
                "email": data['email'].strip().lower(),
                "password": data['password'],
                "email_confirm": True,
                "user_metadata": {
                    "nombre_usuario": data.get('nombre_usuario', ''),
                    "nombre_completo": data.get('nombre_completo', ''),
                    "rol": data.get('rol', ''),
                    "curp": data.get('curp', ''),
                    "telefono": data.get('telefono', ''),
                    "domicilio": data.get('domicilio', ''),
                    "apellidos": data.get('apellidos', ''),
                    "clave_elector": data.get('clave_elector', '')
                }
            })
            
            user_uuid = auth_response.user.id
            print(f"✅ ÉXITO: Usuario Auth creado con UUID: {user_uuid}")
            print(f"   El Trigger de Supabase insertará automáticamente en tabla perfiles")
            
            return jsonify({
                'message': 'Administrador creado exitosamente ✅',
                'user_id': user_uuid
            }), 200
            
        except Exception as e:
            error_real = str(e)
            print(f"🔥 ERROR AL CREAR USUARIO: {error_real}")
            return jsonify({"error": error_real}), 400
        
    except Exception as e:
        print(f"\n❌ === ERROR CRÍTICO EN CREAR_USUARIO ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500


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
        data = request.json
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
        usuario_response = supabase.table('perfiles').select('*').eq('id', id).execute()
        
        if not usuario_response.data or len(usuario_response.data) == 0:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        usuario = usuario_response.data[0]
        
        # Verificar que el usuario actual es un administrador
        if usuario['rol'] not in ALLOWED_ROLES:
            return jsonify({
                'error': 'Solo se pueden actualizar administradores'
            }), 403
        
        # Actualizar en la tabla perfiles
        response = supabase.table('perfiles').update(update_data).eq('id', id).execute()
        
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
    try:
        # Validar que el usuario a eliminar tiene un rol permitido
        usuario_response = supabase.table('perfiles').select('*').eq('id', id).execute()
        
        if not usuario_response.data or len(usuario_response.data) == 0:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        usuario = usuario_response.data[0]
        
        # Verificar que el usuario tiene un rol permitido
        if usuario['rol'] not in ALLOWED_ROLES:
            return jsonify({
                'error': 'No se puede eliminar un usuario que no es administrador'
            }), 403
        
        # Eliminar de la tabla perfiles
        supabase.table('perfiles').delete().eq('id', id).execute()
        
        return jsonify({
            'message': f'Administrador {usuario["nombre_usuario"]} eliminado exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al eliminar usuario: {str(e)}'}), 500


# ============================================================================
# NOTA: El blueprint 'admin_usuarios_bp' se registra en la app maestra
# ============================================================================
