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
    
    print(f"[INFO] Intentando cargar backend de Login desde:")
    print(f"       {backend_path}")
    print(f"       (BASE_DIR: {BASE_DIR})")
    
    # Verificar que el archivo existe
    if not os.path.exists(backend_path):
        print(f"[ERROR] Archivo no encontrado: {backend_path}")
        print(f"[INFO] FRONTEND_DIR = {FRONTEND_DIR}")
        print(f"[INFO] MODULOS_DIR = {MODULOS_DIR}")
        
        # Listar contenido para debugging
        try:
            if os.path.exists(MODULOS_DIR):
                print(f"[INFO] Contenido de {MODULOS_DIR}:")
                for item in os.listdir(MODULOS_DIR)[:5]:  # Primeros 5 items
                    print(f"       - {item}")
            else:
                print(f"[ERROR] MODULOS_DIR no existe: {MODULOS_DIR}")
        except Exception as e:
            print(f"[ERROR] No se pudo listar MODULOS_DIR: {e}")
        
        return None

    try:
        # Cargar el módulo dinamicamente
        spec = importlib.util.spec_from_file_location("login_backend", backend_path)
        
        if spec is None or spec.loader is None:
            print(f"[ERROR] No se pudo crear la especificación del módulo para {backend_path}")
            return None
        
        module = importlib.util.module_from_spec(spec)
        
        # Ejecutar el módulo
        spec.loader.exec_module(module)
        print(f"[OK] Módulo login_backend.py ejecutado correctamente")
        
        # Buscar el objeto 'app'
        backend_app = getattr(module, "app", None)
        
        if backend_app is None:
            print(f"[ERROR] El módulo login_backend.py no tiene un atributo 'app'")
            print(f"[INFO] Atributos disponibles en el módulo:")
            attrs = [attr for attr in dir(module) if not attr.startswith('_')]
            for attr in attrs[:10]:  # Mostrar primeros 10 atributos
                print(f"       - {attr}")
            return None
        
        print(f"[OK] Backend de Login cargado exitosamente (app encontrado)")
        return backend_app
        
    except ImportError as ie:
        print(f"[ERROR] Error de importación en login_backend.py: {ie}")
        print(f"[INFO] Verifica que el archivo sea un módulo Python válido")
        return None
    
    except SyntaxError as se:
        print(f"[ERROR] Error de sintaxis en login_backend.py: {se}")
        return None
    
    except Exception as exc:
        print(f"[ERROR] Error inesperado cargando backend de Login:")
        print(f"       Tipo: {type(exc).__name__}")
        print(f"       Mensaje: {exc}")
        import traceback
        traceback.print_exc()
        return None


# ========================================
# APP WSGI FINAL
# ========================================
# Cargar solo el backend de Login para minimizar uso de memoria
login_app = _load_login_backend()

# DispatcherMiddleware enruta:
# - / → front_app (sirve estáticos)
# - /api → login_app (backend de autenticación)
if login_app is not None:
    app = DispatcherMiddleware(front_app, {'/api': login_app})
    print("[OK] App WSGI creado con DispatcherMiddleware (frontend + backend)")
else:
    # Si falla la carga del backend, solo sirve el frontend
    app = front_app
    print("[WARN] App WSGI en modo frontend-only (sin backend de Login)")
    print("[WARN] La app estará disponible, pero las rutas /api no funcionarán")

# Validar que app no sea None (crítico para Gunicorn)
if app is None:
    raise RuntimeError("FATAL: El objeto 'app' es None. No se pudo inicializar la aplicación WSGI.")


# ========================================
# DESARROLLO LOCAL
# ========================================
if __name__ == "__main__":
    print("=" * 70)
    print("FORMADIG - Sistema de Gestión DIF Acatlán")
    print("=" * 70)
    print(f"[INFO] BASE_DIR:       {BASE_DIR}")
    print(f"[INFO] FRONTEND_DIR:   {FRONTEND_DIR}")
    print(f"[INFO] MODULOS_DIR:    {MODULOS_DIR}")
    print(f"[INFO] Puerto:         {PORT}")
    print(f"[INFO] Host:           0.0.0.0")
    print("=" * 70)
    print("[INFO] Escuchando en 0.0.0.0:{PORT}")
    print("[INFO] Accede a http://localhost:{PORT}")
    print("[INFO] Presiona Ctrl+C para detener.")
    print("=" * 70)
    
    run_simple(
        "0.0.0.0",
        PORT,
        app,
        use_debugger=True,
        use_reloader=True
    )