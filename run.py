import os
import sys
import importlib.util
from flask import Flask, send_from_directory, redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# ========================================
# CONFIGURACIÓN BASE
# ========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Formadig", "1_Sistema_DIF_Acatlan")
PORT = int(os.getenv("PORT", 10000))

print("\n" + "=" * 80)
print("FORMADIG - Sistema de Gestión DIF Acatlán")
print("=" * 80)
print(f"[INFO] BASE_DIR:     {BASE_DIR}")
print(f"[INFO] FRONTEND_DIR: {FRONTEND_DIR}")
print(f"[INFO] PUERTO:       {PORT}")
print("=" * 80)


# ========================================
# 1. APP FRONTEND (Estáticos)
# ========================================
print("\n[STEP 1/3] Creando app Flask para el Frontend...")

front_app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

@front_app.route('/', defaults={'path': ''})
@front_app.route('/<path:path>')
def serve_frontend(path):
    """Sirve archivos estáticos. Raíz redirige a login."""
    if not path:
        return redirect('/modulos/login/vistas/login.html')
    
    full_path = os.path.join(FRONTEND_DIR, path)
    if os.path.isdir(full_path):
        try:
            return front_app.send_static_file(os.path.join(path, 'index.html'))
        except:
            pass
    
    return send_from_directory(FRONTEND_DIR, path)

print("[OK] ✅ Frontend app creado")


# ========================================
# 2. IMPORTAR BACKEND (Login)
# ========================================
print("[STEP 2/3] Importando Backend de Login...")

backend_app = None
try:
    # La carpeta comienza con número, así que usamos importlib
    backend_path = os.path.join(FRONTEND_DIR, "modulos", "login", "logica", "login_backend.py")
    
    spec = importlib.util.spec_from_file_location("login_backend", backend_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules['login_backend'] = module
    spec.loader.exec_module(module)
    
    backend_app = getattr(module, 'app', None)
    
    if backend_app:
        print("[OK] ✅ Backend importado correctamente")
        print(f"[OK]    Tipo: {type(backend_app)}")
    else:
        print("[ERROR] ❌ Backend no tiene atributo 'app'")
        
except FileNotFoundError:
    print(f"[ERROR] ❌ Archivo no encontrado: {backend_path}")
    print("[WARN] Continuando en modo FRONTEND-ONLY")
except ImportError as e:
    print(f"[ERROR] ❌ Import error: {e}")
    print("[WARN] Continuando en modo FRONTEND-ONLY")
except Exception as e:
    print(f"[ERROR] ❌ Error: {type(e).__name__}: {e}")
    print("[WARN] Continuando en modo FRONTEND-ONLY")


# ========================================
# 3. CONSTRUIR APP WSGI CON DISPATCHER
# ========================================
print("[STEP 3/3] Construyendo app WSGI con DispatcherMiddleware...")

if backend_app is not None:
    # Montar el backend en /api
    # Rutas: /api/auth/login, /api/auth/register, etc.
    app = DispatcherMiddleware(front_app, {
        '/api': backend_app
    })
    print("[OK] ✅ DispatcherMiddleware configurado:")
    print("    - '/'    → Frontend (estáticos)")
    print("    - '/api' → Backend (autenticación)")
else:
    # Fallback: solo frontend
    app = front_app
    print("[WARN] ⚠️  FRONTEND-ONLY (sin backend)")

# VALIDACIÓN
if app is None:
    print("[FATAL] ❌ ERROR: app es None")
    sys.exit(1)

print("\n[OK] ✅ Variable 'app' lista para Gunicorn")
print("     Comando: gunicorn run:app --workers 1 --threads 2 --worker-class gthread --bind 0.0.0.0:$PORT")
print("=" * 80 + "\n")

# ========================================
# DESARROLLO LOCAL
# ========================================
if __name__ == "__main__":
    print("[LOCAL DEV] Iniciando servidor local...")
    print(f"[LOCAL DEV] URL: http://localhost:{PORT}")
    print("[LOCAL DEV] Presiona Ctrl+C para detener\n")
    
    run_simple(
        "0.0.0.0",
        PORT,
        app,
        use_debugger=True,
        use_reloader=True
    )