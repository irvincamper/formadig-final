import os
import importlib.util
from flask import Flask, send_from_directory, redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# ========================================
# CONFIGURACIÓN BASE
# ========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Formadig", "1_Sistema_DIF_Acatlan")
MODULOS_DIR = os.path.join(FRONTEND_DIR, "modulos")

# Puerto: Lee de variable de entorno (Render asigna PORT automáticamente)
# Default 5000 para desarrollo local
PORT = int(os.getenv("PORT", 5000))


# ========================================
# APP PRINCIPAL PARA ESTÁTICOS
# ========================================
front_app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')


@front_app.route('/', defaults={'path': ''})
@front_app.route('/<path:path>')
def serve_frontend(path):
    """
    Sirve archivos estáticos del frontend.
    La raíz redirige a la pantalla de login.
    """
    if not path:
        return redirect('/modulos/login/vistas/login.html')

    full_path = os.path.join(FRONTEND_DIR, path)
    
    # Si es un directorio, intenta servir index.html
    if os.path.isdir(full_path):
        return front_app.send_static_file(os.path.join(path, 'index.html'))

    return send_from_directory(FRONTEND_DIR, path)


# ========================================
# CARGA DINÁMICA DE BACKENDS
# ========================================
def _load_backend_app(name, backend_path):
    """
    Carga un app Flask/WSGI desde un archivo Python dinámicamente.
    
    Args:
        name: Nombre del backend (para logging)
        backend_path: Ruta absoluta al archivo del backend
        
    Returns:
        El objeto app del backend, o None si falla la carga
    """
    if not os.path.exists(backend_path):
        print(f"[WARN] Backend '{name}' no encontrado en {backend_path}")
        return None

    try:
        spec = importlib.util.spec_from_file_location(name, backend_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        backend_app = getattr(module, "app", None)
        
        if backend_app:
            print(f"[OK] Backend '{name}' cargado exitosamente")
        else:
            print(f"[WARN] Backend '{name}' no exporta 'app'")
        
        return backend_app
    except Exception as exc:
        print(f"[ERROR] Error cargando backend '{name}': {exc}")
        return None


# ========================================
# CONFIGURAR BACKENDS
# ========================================
backends_config = {
    "auth": os.path.join(MODULOS_DIR, "login", "logica", "login_backend.py"),
    "traslados": os.path.join(MODULOS_DIR, "admin_traslados", "logica", "admin_traslados_backend.py"),
    "desayunos-frios": os.path.join(MODULOS_DIR, "admin_desayunos_frios", "logica", "admin_desayunos_frios_backend.py"),
    "desayunos-calientes": os.path.join(MODULOS_DIR, "admin_desayunos_calientes", "logica", "admin_desayunos_calientes_backend.py"),
    "espacios-eaeyd": os.path.join(MODULOS_DIR, "admin_espacios_eaeyd", "logica", "admin_espacios_eaeyd_backend.py"),
    "chatbot": os.path.join(MODULOS_DIR, "chatbot", "logica", "chatbot_backend.py"),
    "sms": os.path.join(MODULOS_DIR, "sms", "logica", "sms_backend.py"),
}

# Cargar todos los backends disponibles
backends_mounted = {}
for name, path in backends_config.items():
    backend_app = _load_backend_app(name, path)
    if backend_app:
        route = f"/api/{name}"
        backends_mounted[route] = backend_app


# ========================================
# APP WSGI FINAL
# ========================================
# DispatcherMiddleware permite servir múltiples apps bajo diferentes rutas.
# front_app sirve estáticos en /, backends sirven en /api/<nombre>
app = DispatcherMiddleware(front_app, backends_mounted)


# ========================================
# DESARROLLO LOCAL
# ========================================
if __name__ == "__main__":
    print("=" * 60)
    print("FORMADIG - Sistema de Gestión DIF Acatlán")
    print("=" * 60)
    print(f"Iniciando servidor en http://localhost:{PORT}")
    print(f"Estáticos servidos desde: {FRONTEND_DIR}")
    print(f"Backends montados: {list(backends_mounted.keys())}")
    print("Presiona Ctrl+C para detener.")
    print("=" * 60)
    
    run_simple(
        "127.0.0.1",
        PORT,
        app,
        use_debugger=True,
        use_reloader=True
    )