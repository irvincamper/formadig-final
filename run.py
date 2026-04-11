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
# Default 10000 para Render, o 5000 para desarrollo local
PORT = int(os.getenv("PORT", 10000))


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
# CARGA DEL BACKEND DE LOGIN
# ========================================
def _load_login_backend():
    """
    Carga el app Flask/WSGI del backend de Login dinámicamente.
    Este es el único backend que se carga para ahorrar memoria.
    
    Returns:
        El objeto app del backend de login, o None si falla
    """
    backend_path = os.path.join(MODULOS_DIR, "login", "logica", "login_backend.py")
    
    if not os.path.exists(backend_path):
        print(f"[WARN] Backend de Login no encontrado en {backend_path}")
        return None

    try:
        spec = importlib.util.spec_from_file_location("login_backend", backend_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        backend_app = getattr(module, "app", None)
        
        if backend_app:
            print(f"[OK] Backend de Login cargado exitosamente")
        else:
            print(f"[WARN] Backend de Login no exporta 'app'")
        
        return backend_app
    except Exception as exc:
        print(f"[ERROR] Error cargando backend de Login: {exc}")
        return None


# ========================================
# APP WSGI FINAL
# ========================================
# Cargar solo el backend de Login para minimizar uso de memoria
login_app = _load_login_backend()

# DispatcherMiddleware enruta:
# - / → front_app (sirve estáticos)
# - /api → login_app (backend de autenticación)
if login_app:
    app = DispatcherMiddleware(front_app, {'/api': login_app})
else:
    # Si falla la carga del backend, solo sirve el frontend
    app = front_app
    print("[WARN] Operando en modo frontend-only (sin backend de Login)")


# ========================================
# DESARROLLO LOCAL
# ========================================
if __name__ == "__main__":
    print("=" * 60)
    print("FORMADIG - Sistema de Gestión DIF Acatlán")
    print("=" * 60)
    print(f"Escuchando en 0.0.0.0:{PORT}")
    print(f"Estáticos servidos desde: {FRONTEND_DIR}")
    print(f"Backend de Login montado en: /api")
    print("Presiona Ctrl+C para detener.")
    print("=" * 60)
    
    run_simple(
        "0.0.0.0",
        PORT,
        app,
        use_debugger=True,
        use_reloader=True
    )