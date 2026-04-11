from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# =========================================================
# 🔴 INSTALACIÓN REQUERIDA: pip install supabase
# =========================================================
try:
    from supabase import create_client, Client
except ImportError:
    print("CRÍTICO: Debes ejecutar 'pip install supabase' en tu terminal.")
    exit(1)

# =========================================================
# REEMPLAZA ESTAS VARIABLES CON LOS DATOS DE TU PROYECTO SUPABASE
# =========================================================
SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"

# Si has pegado las claves, intenta conectar
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"ATENCIÓN: Claves de Supabase inválidas o vacías. Error: {e}")
    supabase = None

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    if not supabase:
         return jsonify({"error": "Las claves de Supabase no se han configurado"}), 500

    # 1. Verificar Autorización (Solo Admin/Director puede crear usuarios)
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "No autorizado. Se requiere token de sesión."}), 401
    
    token = auth_header.split(' ')[1]
    try:
        # Validar el token con Supabase
        user_res = supabase.auth.get_user(token)
        requester = user_res.user
        if not requester:
            return jsonify({"error": "Sesión inválida o expirada."}), 401
            
        # Verificar rol del solicitante en la tabla perfiles
        admin_check = supabase.table('perfiles').select('rol').eq('id', requester.id).execute()
        perfil_data = getattr(admin_check, 'data', [])
        
        if not perfil_data or perfil_data[0].get('rol') not in ['admin', 'directora', 'desarrollador']:
             # Si no está en perfiles, checar metadata por si acaso
             role_meta = requester.user_metadata.get('role')
             if role_meta not in ['admin', 'directora', 'desarrollador']:
                return jsonify({"error": "Permisos insuficientes. Solo el Director puede crear usuarios."}), 403
    except Exception as e:
        print(f"Error verificando permisos: {e}")
        return jsonify({"error": "Error al verificar permisos de administrador."}), 401

    # 2. Proceder con el registro una vez autorizado
    data = request.json
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    full_name = data.get('full_name', '')

    if not email or not password or not role:
        return jsonify({"error": "Faltan credenciales o el rol asignado"}), 400

    try:
        # Crea el usuario en Supabase Auth y guarda su Rol y Nombre en sus Metadata
        res = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": { 
                    "role": role,
                    "nombre_completo": full_name
                }
            }
        })

        # Intentar crear/actualizar la fila en la tabla `perfiles` para asegurar el rol
        try:
            user_obj = getattr(res, 'user', None)
            user_id = user_obj.id if user_obj else None
            if user_id:
                # El esquema espera `nombre_usuario`, usaremos el email como tal
                supabase.table('perfiles').upsert({
                    "id": user_id,
                    "nombre_usuario": email,
                    "nombre_completo": full_name,
                    "rol": role or 'usuario_traslados'
                }).execute()
        except Exception as e:
            print('AVISO: No se pudo upsert en perfiles:', e)

        # Si Supabase te exige confirmación de correo, res.user seguirá activo una vez comprobado.
        return jsonify({"message": "✅ Usuario creado en Supabase Auth", "user_id": res.user.id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/auth/login', methods=['POST'])
def login_user():
    if not supabase:
         return jsonify({"error": "Las claves de Supabase no se han configurado en login_backend.py"}), 500

    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Faltan credenciales"}), 400

    try:
        # Verifica el usuario en Supabase
        res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        # Extraemos el Token de Sesión JWT oficial
        user = res.user
        session_token = res.session.access_token if res.session else None
        role = None
        nombre_completo = None

        # Intentar leer el rol y nombre desde la tabla `perfiles`
        try:
            user_id = user.id if user else None
            if user_id:
                perfil_res = supabase.table('perfiles').select('rol, nombre_completo').eq('id', user_id).execute()
                perfil_data = getattr(perfil_res, 'data', [])
                
                if perfil_data and len(perfil_data) > 0:
                    role = perfil_data[0].get('rol')
                    nombre_completo = perfil_data[0].get('nombre_completo')
                else:
                    role = user.user_metadata.get('role') if user and hasattr(user, 'user_metadata') else None
        except Exception as e:
            print('AVISO: No se pudo leer perfil:', e)

        payload = {
            "message": "Login exitoso",
            "role": role,
            "nombre_completo": nombre_completo,
            "session": {"access_token": session_token}
        }
        if not role:
            payload['warning'] = 'Usuario autorizado pero sin rol asignado.'

        return jsonify(payload), 200
        
    except Exception as e:
        print("Login Fallido:", e)
        # Devolvemos el error real para depuración (luego se puede simplificar)
        error_msg = str(e)
        if "Email not confirmed" in error_msg:
             return jsonify({"error": "⚠️ Correo no confirmado. Revisa tu bandeja de entrada o desactiva la confirmación en Supabase."}), 401
        return jsonify({"error": f"Error de autenticación: {error_msg}"}), 401

if __name__ == '__main__':
    print("🛡️ Módulo de Login/Supabase escuchando en el puerto 5001...")
    # Solo para dev local (debug=True), recuerda cambiar en producción
    app.run(port=5001, debug=True)
