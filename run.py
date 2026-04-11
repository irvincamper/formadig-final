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
# CONFIGURACIÓN DE MÓDULOS BACKEND
# ========================================
# Estructura: nombre_módulo -> (archivo_backend.py, ruta_dispatcher)
# Descomenta/comenta módulos según necesites
BACKENDS_CONFIG = {
    # ❌ Descomenta para cargar (comentar en línea siguiente para desactivar):
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
    # "desayunos_calientes": ("admin_desayunos_calientes/logica/admin_desayunos_calientes_backend.py", "/api/desayunos_calientes"),
    "sms": ("sms/logica/sms_backend.py", "/api/sms"),
    # "espacios_eaeyd": ("admin_espacios_eaeyd/logica/admin_espacios_eaeyd_backend.py", "/api/espacios"),
    # "usuarios": ("admin_usuarios/logica/admin_usuarios_backend.py", "/api/usuarios"),
}


# ========================================
# FUNCIÓN PARA CARGAR BACKENDS
# ========================================
def cargar_backend(nombre_modulo, ruta_relativa):
    """
    Carga un backend Flask desde un archivo usando importlib.
    
    Args:
        nombre_modulo: nombre único para identificar el módulo
        ruta_relativa: ruta relativa dentro de MODULOS_DIR
        
    Returns:
        objeto Flask app o None si falla
    """
    ruta_completa = os.path.join(MODULOS_DIR, ruta_relativa)
    
    print(f"\n  [→] Cargando: {nombre_modulo}")
    print(f"      Archivo: {ruta_completa}")
    
    if not os.path.exists(ruta_completa):
        print(f"      [ERROR] ❌ Archivo no existe")
        return None
    
    try:
        # Crear especificación del módulo
        spec = importlib.util.spec_from_file_location(
            f"backend_{nombre_modulo}",
            ruta_completa
        )
        
        if spec is None or spec.loader is None:
            print(f"      [ERROR] ❌ No se pudo crear especificación del módulo")
            return None
        
        # Cargar el módulo
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"backend_{nombre_modulo}"] = module
        spec.loader.exec_module(module)
        
        # Extraer el objeto app
        app_obj = getattr(module, 'app', None)
        
        if app_obj is None:
            print(f"      [ERROR] ❌ No se encontró objeto 'app' en el módulo")
            return None
        
        print(f"      [OK] ✅ Backend cargado exitosamente")
        return app_obj
        
    except Exception as e:
        print(f"      [ERROR] ❌ Excepción: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None


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
# 2. CARGAR TODOS LOS BACKENDS
# ========================================
print("\n[STEP 2/3] Cargando backends de módulos...")

backends_cargados = {}
dispatcher_dict = {}

for nombre_modulo, (ruta_relativa, ruta_dispatcher) in BACKENDS_CONFIG.items():
    app_backend = cargar_backend(nombre_modulo, ruta_relativa)
    
    if app_backend is not None:
        backends_cargados[nombre_modulo] = app_backend
        dispatcher_dict[ruta_dispatcher] = app_backend
        print(f"      → Montando en ruta: {ruta_dispatcher}")
    else:
        print(f"      [SKIP] ⚠️  Módulo '{nombre_modulo}' no se cargará")

print(f"\n[SUMMARY] Backends cargados: {len(backends_cargados)}/{len(BACKENDS_CONFIG)}")
if backends_cargados:
    print("  Módulos activos:")
    for nombre in backends_cargados.keys():
        print(f"    ✅ {nombre}")


# ========================================
# 3. CONSTRUIR APP WSGI CON DISPATCHER
# ========================================
print("\n[STEP 3/3] Construyendo app WSGI con DispatcherMiddleware...")

if dispatcher_dict:
    print(f"[OK] Montando {len(dispatcher_dict)} backend(s) en DispatcherMiddleware...")
    
    app = DispatcherMiddleware(front_app, dispatcher_dict)
    
    print("[OK] ✅ DispatcherMiddleware configurado:")
    print("    - '/'         → Frontend (estáticos)")
    for ruta in dispatcher_dict.keys():
        print(f"    - '{ruta}'     → Backend")
    
else:
    print(f"[WARN] ⚠️  NO hay backends cargados")
    print(f"[WARN] Operando en modo FRONTEND-ONLY (sin backend)")
    app = front_app

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