import os
import sys
import importlib.util
from flask import Flask, send_from_directory, redirect
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# ========================================
# CARGAR VARIABLES DE ENTORNO
# ========================================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  AVISO: python-dotenv no instalado. Las variables .env serán ignoradas.")
    print("   Instala con: pip install python-dotenv")

# ========================================
# CONFIGURACIÓN BASE
# ========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Formadig", "1_Sistema_DIF_Acatlan")
MODULOS_DIR = os.path.join(FRONTEND_DIR, "modulos")
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
# 2. CARGAR BACKENDS MODULARES
# ========================================
print("\n[STEP 2/3] Cargando backends de módulos...")

def cargar_backend(nombre, ruta_relativa):
    """Carga un backend usando importlib"""
    ruta_completa = os.path.join(MODULOS_DIR, ruta_relativa)
    
    if not os.path.exists(ruta_completa):
        print(f"  ⚠️  {nombre}: archivo no encontrado ({ruta_completa})")
        return None
    
    try:
        spec = importlib.util.spec_from_file_location(f"backend_{nombre}", ruta_completa)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"backend_{nombre}"] = module
        spec.loader.exec_module(module)
        app_obj = getattr(module, 'app', None)
        if app_obj:
            print(f"  ✅ {nombre} cargado → {ruta_relativa}")
            return app_obj
        else:
            print(f"  ❌ {nombre}: no tiene objeto 'app'")
            return None
    except Exception as e:
        print(f"  ❌ {nombre}: {type(e).__name__}: {str(e)[:50]}")
        return None

# Diccionario de backends a cargar
backends_config = {
    "login": ("login/logica/login_backend.py", "/api"),
    "chatbot": ("chatbot/logica/chatbot_backend.py", "/api/chatbot"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
    "desayunos_calientes": ("admin_desayunos_calientes/logica/admin_desayunos_calientes_backend.py", "/api/desayunos_calientes"),
    "espacios_eaeyd": ("admin_espacios_eaeyd/logica/admin_espacios_eaeyd_backend.py", "/api/espacios_eaeyd"),
    "sms": ("sms/logica/sms_backend.py", "/api/sms"),
    "admin_usuarios": ("admin_usuarios/logica/admin_usuarios_backend.py", "/api"),
}

# Cargar backends
dispatcher_dict = {}
backends_activos = []

for nombre, (ruta, prefijo) in backends_config.items():
    app_backend = cargar_backend(nombre, ruta)
    if app_backend:
        dispatcher_dict[prefijo] = app_backend
        backends_activos.append(nombre)

print(f"\n  Total cargado: {len(backends_activos)}/{len(backends_config)}")
if backends_activos:
    print(f"  Backends: {', '.join(backends_activos)}")


# ========================================
# 3. CONSTRUIR APP WSGI CON DISPATCHER
# ========================================
print("\n[STEP 3/3] Construyendo app WSGI con DispatcherMiddleware...")

if dispatcher_dict:
    app = DispatcherMiddleware(front_app, dispatcher_dict)
    print("[OK] ✅ DispatcherMiddleware configurado:")
    print("     - '/'  → Frontend")
    for ruta in dispatcher_dict.keys():
        print(f"     - '{ruta}' → Backend")
else:
    print("[WARN] ⚠️  NO hay backends. Modo FRONTEND-ONLY")
    app = front_app

if app is None:
    print("[FATAL] ❌ ERROR: app es None")
    sys.exit(1)

print("\n[OK] ✅ Variable 'app' lista para Gunicorn")
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