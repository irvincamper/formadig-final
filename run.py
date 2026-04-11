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
backend_path = os.path.join(FRONTEND_DIR, "modulos", "login", "logica", "login_backend.py")
print(f"[DEBUG] Ruta del backend: {backend_path}")
print(f"[DEBUG] ¿Existe? {os.path.exists(backend_path)}")

try:
    # La carpeta comienza con número, así que usamos importlib
    spec = importlib.util.spec_from_file_location("login_backend", backend_path)
    
    if spec is None:
        print("[ERROR] ❌ spec es None")
        raise Exception("No se pudo crear la especificación del módulo")
    
    if spec.loader is None:
        print("[ERROR] ❌ spec.loader es None")
        raise Exception("spec.loader es None")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules['login_backend'] = module
    spec.loader.exec_module(module)
    print("[OK] ✅ Módulo ejecutado")
    
    backend_app = getattr(module, 'app', None)
    
    if backend_app:
        print("[OK] ✅ Backend importado correctamente")
        print(f"[OK]    Tipo: {type(backend_app)}")
        print(f"[OK]    Rutas del backend: {list(backend_app.url_map.iter_rules())[:5]}")
    else:
        print("[ERROR] ❌ Backend no tiene atributo 'app'")
        print(f"[DEBUG] Atributos del módulo: {[a for a in dir(module) if not a.startswith('_')][:10]}")
        
except FileNotFoundError as fnf:
    print(f"[ERROR] ❌ Archivo no encontrado: {fnf}")
    print("[WARN] Continuando en modo FRONTEND-ONLY")
    import traceback
    traceback.print_exc()
except ImportError as ie:
    print(f"[ERROR] ❌ Import error: {ie}")
    print("[WARN] Continuando en modo FRONTEND-ONLY")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"[ERROR] ❌ Error: {type(e).__name__}: {e}")
    print("[WARN] Continuando en modo FRONTEND-ONLY")
    import traceback
    traceback.print_exc()


# ========================================
# 3. CONSTRUIR APP WSGI CON DISPATCHER
# ========================================
print("[STEP 3/3] Construyendo app WSGI con DispatcherMiddleware...")

if backend_app is not None:
    print(f"[OK] Backend app cargado. Montando en ruta /api...")
    
    # Montar el backend en /api
    # Rutas: /api/auth/login, /api/auth/register, etc.
    app = DispatcherMiddleware(front_app, {
        '/api': backend_app
    })
    print("[OK] ✅ DispatcherMiddleware configurado:")
    print("    - '/'    → Frontend (estáticos)")
    print("    - '/api' → Backend (autenticación)")
    print(f"[DEBUG] Type de app: {type(app)}")
    print(f"[DEBUG] App es: {app}")
else:
    print(f"[WARN] ⚠️  Backend NO se cargó")
    print(f"[WARN] Operando en modo FRONTEND-ONLY (sin backend)")
    print(f"[WARN] Las rutas /api/* no estarán disponibles")
    app = front_app
    print(f"[DEBUG] Usando solo front_app")

# VALIDACIÓN
if app is None:
    print("[FATAL] ❌ ERROR: app es None")
    sys.exit(1)

print("\n[OK] ✅ Variable 'app' lista para Gunicorn")
print("=" * 80)

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