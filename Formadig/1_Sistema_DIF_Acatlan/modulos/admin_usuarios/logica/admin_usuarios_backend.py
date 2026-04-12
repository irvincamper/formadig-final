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

# Inicializar Blueprint
admin_usuarios_bp = Blueprint('admin_usuarios', __name__, url_prefix='/api/admin_usuarios')

# Inicializar Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ctiqbycbkcftwuqgzxjb.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
        print(f"JSON recibido: {data}")
        
        # Validar que se proporcionan los campos requeridos (PASO 0)
        required_fields = ['nombre_usuario', 'nombre_completo', 'email', 'password', 'rol', 'telefono']
        for field in required_fields:
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
        
        # 🔐 PASO 1: CREAR USUARIO EN SUPABASE AUTH (genera UUID automáticamente)
        try:
            print(f"\n🔐 === PASO 1: CREAR EN AUTH ===")
            print(f"Email: {data['email'].strip().lower()}")
            print(f"Password: {'*' * len(data['password'])} ({len(data['password'])} caracteres)")
            
            auth_response = supabase.auth.admin.create_user({
                "email": data['email'].strip().lower(),  # Normalizar email
                "password": data['password'],
                "email_confirm": True  # Confirmar automáticamente para evitar esperar verificación
            })
            
            # Extraer UUID del usuario creado en Auth
            user_uuid = auth_response.user.id
            print(f"✅ PASO 1 ÉXITO: Usuario Auth creado con UUID: {user_uuid}")
            
        except Exception as auth_error:
            error_message = str(auth_error).lower()
            print(f"❌ PASO 1 ERROR: {error_message}")
            
            # Traducir errores comunes de Supabase Auth de forma más precisa
            if 'user_already_exists' in error_message or 'already registered' in error_message:
                print(f"❌ Email ya registrado: {data['email']}")
                return jsonify({'error': 'Este correo electrónico ya está registrado en el sistema. Por favor, usa otro correo.'}), 400
            elif 'invalid email' in error_message or 'invalid_email' in error_message:
                print(f"❌ Email inválido: {data['email']}")
                return jsonify({'error': 'El formato del correo electrónico es inválido.'}), 400
            elif 'password' in error_message or 'weak_password' in error_message:
                print(f"❌ Contraseña débil")
                return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres con variedad.'}), 400
            else:
                # Error genérico pero informativo
                print(f"❌ Error genérico Auth: {str(auth_error)}")
                return jsonify({'error': f'Error al crear cuenta en el sistema de autenticación: {str(auth_error)}'}), 500
        
        # 📝 PASO 2: PREPARAR DATOS PARA TABLA PERFILES (SIN EMAIL - Email es solo para Auth)
        # ⚠️ IMPORTANTE: La tabla 'perfiles' NO contiene email ni password
        # Esos datos están solo en auth.users
        print(f"\n📝 === PASO 2: PREPARAR DATOS PARA PERFILES ===")
        nuevo_usuario = {
            'id': user_uuid,  # ⭐ CRÍTICO: UUID obtenido del Auth
            'nombre_usuario': data['nombre_usuario'],  # Campo: 'Usuario (ej. director)' del frontend
            'nombre_completo': data['nombre_completo'],
            'rol': data['rol'],
            'telefono': data['telefono'],
            'curp': data.get('curp', ''),
            'apellidos': data.get('apellidos', ''),
            'clave_elector': data.get('clave_elector', ''),
            'domicilio': data.get('domicilio', ''),
            'fecha_creacion': datetime.now().isoformat()
            # ❌ NO INCLUIR: email, password (esos están en auth.users, NO aquí)
        }
        
        print(f"✅ PASO 2: Datos preparados para tabla perfiles:")
        print(f"  - id: {nuevo_usuario['id']}")
        print(f"  - nombre_usuario: {nuevo_usuario['nombre_usuario']}")
        print(f"  - nombre_completo: {nuevo_usuario['nombre_completo']}")
        print(f"  - rol: {nuevo_usuario['rol']}")
        print(f"  - telefono: {nuevo_usuario['telefono']}")
        
        # 💾 PASO 3: INSERTAR EN TABLA PERFILES CON UUID LINKEADO
        try:
            print(f"\n💾 === PASO 3: INSERTAR EN TABLA PERFILES ===")
            print(f"Tabla: 'perfiles'")
            print(f"Registros a insertar: {nuevo_usuario}")
            
            response = supabase.table('perfiles').insert(nuevo_usuario).execute()
            
            print(f"✅ PASO 3 ÉXITO: Datos insertados en perfiles")
            print(f"Respuesta: {response.data}")
            
            return jsonify({
                'message': 'Administrador creado exitosamente ✅',
                'usuario': response.data[0] if response.data else nuevo_usuario,
                'auth_uuid': user_uuid  # Para logging
            }), 201
            
        except Exception as db_error:
            # Si falla la inserción en perfiles, eliminar usuario de Auth para evitar inconsistencia
            print(f"\n❌ === PASO 3 ERROR ===")
            print(f"Error: {str(db_error)}")
            print(f"🗑️ Limpiando: Eliminando usuario Auth {user_uuid} para evitar inconsistencia...")
            
            try:
                supabase.auth.admin.delete_user(user_uuid)
                print(f"✅ Usuario Auth eliminado exitosamente")
            except Exception as cleanup_error:
                print(f"⚠️ Error al eliminar usuario Auth: {cleanup_error}")
            
            # Análisis de error para mensajes más claros
            error_str = str(db_error).lower()
            
            if 'column' in error_str and 'does not exist' in error_str:
                print(f"❌ ERROR: Intento de insertar columna que no existe en la tabla 'perfiles'")
                return jsonify({
                    'error': f'Error de estructura de datos: {str(db_error)}. Asegúrate de que la tabla perfiles tiene las columnas correctas.'
                }), 500
            elif 'duplicate' in error_str or 'unique' in error_str:
                return jsonify({
                    'error': f'El usuario ya existe en el sistema'
                }), 400
            else:
                return jsonify({
                    'error': f'Error al guardar datos en perfiles: {str(db_error)}'
                }), 500
        
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
