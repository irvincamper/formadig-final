"""
=============================================================================
SERVIDOR PRINCIPAL - FORMADIG v2.1
=============================================================================
Este archivo:
1. Sirve el frontend estático desde Formadig/1_Sistema_DIF_Acatlan
2. Registra TODOS los blueprints bajo /api/
3. Compatible con: gunicorn run:app (válido para Render)
4. Compatible con: python run.py (desarrollo local)
=============================================================================
"""

import os
import sys
import importlib.util
from flask import Flask, send_from_directory, redirect, jsonify
from flask_cors import CORS

# ============================================================================
# CONFIGURACIÓN DE DIRECTORIOS
# ============================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SYSTEM_DIR = os.path.join(BASE_DIR, "Formadig", "1_Sistema_DIF_Acatlan")
MODULES_DIR = os.path.join(SYSTEM_DIR, "modulos")

print("\n" + "="*70)
print("🚀 FORMADIG v2.1 - APLICACIÓN UNIFICADA")
print("="*70)
print(f"   Sistema en: {SYSTEM_DIR}")
print(f"   Módulos en: {MODULES_DIR}")

# ============================================================================
# CREAR APLICACIÓN FLASK
# ============================================================================

app = Flask(__name__, static_folder=SYSTEM_DIR, static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuración
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# ============================================================================
# REGISTRAR TODOS LOS BLUEPRINTS BAJO /api/
# ============================================================================

def register_blueprints():
    """Registra todos los blueprints de módulos bajo /api/"""
    
    blueprints_to_register = [
        ("login", "login", "login_backend", "auth_bp"),
        ("admin_usuarios", "admin_usuarios", "admin_usuarios_backend", "admin_usuarios_bp"),
        ("admin_traslados", "admin_traslados", "admin_traslados_backend", "traslados_bp"),
        ("admin_desayunos_frios", "admin_desayunos_frios", "admin_desayunos_frios_backend", "desayunos_frios_bp"),
        ("admin_desayunos_calientes", "admin_desayunos_calientes", "admin_desayunos_calientes_backend", "desayunos_calientes_bp"),
        ("admin_espacios_eaeyd", "admin_espacios_eaeyd", "admin_espacios_eaeyd_backend", "espacios_eaeyd_bp"),
        ("chatbot", "chatbot", "chatbot_backend", "chatbot_bp"),
        ("sms", "sms", "sms_backend", "sms_bp"),
        ("colonias", "colonias", "colonias_backend", "colonias_bp"),
    ]
    
    registered = 0
    for module_name, module_folder, module_file, bp_name in blueprints_to_register:
        try:
            # Construir ruta completa del archivo del módulo
            module_file_path = os.path.join(MODULES_DIR, module_folder, "logica", f"{module_file}.py")
            
            if not os.path.exists(module_file_path):
                print(f"   ❌ [{module_name}] Archivo no encontrado: {module_file_path}")
                continue
            
            # Importar usando importlib de forma segura
            spec = importlib.util.spec_from_file_location(module_file, module_file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Obtener el blueprint
                if hasattr(module, bp_name):
                    bp = getattr(module, bp_name)
                    app.register_blueprint(bp)
                    print(f"   ✅ [{module_name}] Registrado como blueprint ({bp_name})")
                    registered += 1
                else:
                    print(f"   ❌ [{module_name}] No tiene atributo '{bp_name}'")
            else:
                print(f"   ❌ [{module_name}] No se pudo cargar el spec del módulo")
                
        except Exception as e:
            print(f"   ⚠️ [{module_name}] Error al registrar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return registered

# Registrar blueprints
try:
    total_registered = register_blueprints()
    print(f"\n✅ Total blueprints registrados: {total_registered}/9")
except Exception as e:
    print(f"\n❌ Error registrando blueprints: {e}")
    sys.exit(1)

# ============================================================================
# RUTAS DE HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificación de salud de la aplicación."""
    return jsonify({
        "status": "healthy",
        "service": "FORMADIG v2.1",
        "version": "2.1.0",
        "port": os.environ.get('PORT', 8000)
    }), 200

@app.route('/api/status', methods=['GET'])
def api_status():
    """Estado general de la API."""
    return jsonify({
        "message": "API Unificada FORMADIG funcionando",
        "blueprints_registered": total_registered
    }), 200

# ============================================================================
# RUTA RAÍZ Y SERVICIO DE FRONTEND ESTÁTICO
# ============================================================================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Sirve el frontend estático desde Formadig/1_Sistema_DIF_Acatlan"""
    
    # La raíz redirige al login
    if not path:
        return redirect('/modulos/login/vistas/login.html')

    # Construir la ruta del archivo
    full_path = os.path.join(SYSTEM_DIR, path)
    
    # Si es una carpeta, buscar index.html
    if os.path.isdir(full_path):
        index_path = os.path.join(full_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(SYSTEM_DIR, os.path.join(path, 'index.html'))
        else:
            return jsonify({"error": "index.html not found"}), 404

    # Servir el archivo si existe
    if os.path.exists(full_path):
        return send_from_directory(SYSTEM_DIR, path)
    else:
        return jsonify({"error": "File not found"}), 404

# ============================================================================
# MANEJO DE ERRORES GLOBAL
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado", "status": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor", "status": 500}), 500

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == '__main__':
    # Puerto dinámico desde variable de entorno (para Render)
    port = int(os.environ.get('PORT', 8000))
    host = '0.0.0.0'
    
    print(f"\n" + "="*70)
    print(f"🎯 Iniciando servidor:")
    print(f"   Host: {host}")
    print(f"   Puerto: {port}")
    print(f"   Frontend: {SYSTEM_DIR}")
    print(f"   Debug: False")
    print(f"="*70 + "\n")
    
    app.run(host=host, port=port, debug=False, use_reloader=False)