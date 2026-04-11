"""
Backend para Gestión de Usuarios - SOLO Administradores
Módulo: admin_usuarios_backend.py
Enfoque: Seguridad - Mostrar únicamente administradores (admin, admin_desayunos, admin_traslados)
"""

from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os
from datetime import datetime

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

# Inicializar Blueprint
admin_usuarios_bp = Blueprint('admin_usuarios', __name__, url_prefix='/admin_usuarios')

# Inicializar Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ctiqbycbkcftwuqgzxjb.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Roles permitidos - SOLO administradores
ALLOWED_ROLES = ['admin', 'admin_desayunos', 'admin_traslados']


# ============================================================================
# GET / - Obtener lista de administradores (Filtrado por rol)
# ============================================================================
@admin_usuarios_bp.route('/', methods=['GET'])
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
@admin_usuarios_bp.route('/', methods=['POST'])
def crear_usuario():
    """
    Endpoint POST para crear nuevo administrador.
    Validación: ROL debe ser uno de los permitidos.
    """
    try:
        data = request.json
        
        # Validar que se proporcionan los campo requeridos
        required_fields = ['nombre_usuario', 'nombre_completo', 'rol', 'telefono']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Campo requerido faltante: {field}'}), 400
        
        # Validación crítica: ROL debe estar en la lista permitida
        if data['rol'] not in ALLOWED_ROLES:
            return jsonify({
                'error': f"Rol no permitido. Use: {', '.join(ALLOWED_ROLES)}"
            }), 400
        
        # Preparar datos del nuevo usuario
        nuevo_usuario = {
            'nombre_usuario': data['nombre_usuario'],
            'nombre_completo': data['nombre_completo'],
            'rol': data['rol'],
            'telefono': data['telefono'],
            'curp': data.get('curp', ''),
            'apellidos': data.get('apellidos', ''),
            'clave_elector': data.get('clave_elector', ''),
            'domicilio': data.get('domicilio', ''),
            'fecha_creacion': datetime.now().isoformat()
        }
        
        # Insertar en la tabla perfiles
        response = supabase.table('perfiles').insert(nuevo_usuario).execute()
        
        return jsonify({
            'message': 'Administrador creado exitosamente',
            'usuario': response.data[0] if response.data else nuevo_usuario
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500


# ============================================================================
# DELETE /<id> - Eliminar administrador
# ============================================================================
@admin_usuarios_bp.route('/<id>', methods=['DELETE'])
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
# Registro del Blueprint en la app
# ============================================================================
app.register_blueprint(admin_usuarios_bp)
