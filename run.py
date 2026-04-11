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
LOGIN_BACKEND_PATH = os.path.join(MODULOS_DIR, "login", "logica", "login_backend.py")

# Puerto: Lee de variable de entorno (Render asigna PORT automáticamente)
# Default 10000 para Render, o 5000 para desarrollo local
PORT = int(os.getenv("PORT", 10000))

# Imprimir configuración al iniciar
print("\n" + "=" * 80)
print("FORMADIG - Sistema de Gestión DIF Acatlán (WSGI Entry Point)")
print("=" * 80)
print(f"[INFO] BASE_DIR =           {BASE_DIR}")
print(f"[INFO] FRONTEND_DIR =       {FRONTEND_DIR}")
print(f"[INFO] MODULOS_DIR =        {MODULOS_DIR}")
print(f"[INFO] LOGIN_BACKEND_PATH = {LOGIN_BACKEND_PATH}")
print(f"[INFO] Puerto =             {PORT}")
print("=" * 80)


# ========================================
# APP PRINCIPAL PARA ESTÁTICOS (Frontend)
# ========================================
print("\n[STEP 1] Creando app Flask para estáticos del frontend...")
front_app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
print(f"[OK] Front app creado. Static folder: {FRONTEND_DIR}")


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
        try:
            return front_app.send_static_file(os.path.join(path, 'index.html'))
        except:
            pass

    return send_from_directory(FRONTEND_DIR, path)


# ========================================
# CARGA DEL BACKEND DE LOGIN
# ========================================
print("\n[STEP 2] Cargando Backend de Login...")

def _load_login_backend():
    """
    Carga dinámicamente el app Flask del backend de Login.
    
    Returns:
        El objeto app de Flask que exporta login_backend.py, o None si falla
        
    Raises:
        Imprime detalles de error pero no levanta excepciones para permitir
        ejecución en modo frontend-only como fallback.
    """
    print(f"[DEBUG] Buscando backend en: {LOGIN_BACKEND_PATH}")
    
    # PASO 1: Verificar que el archivo existe
    if not os.path.exists(LOGIN_BACKEND_PATH):
        print(f"[ERROR] ❌ Archivo no encontrado: {LOGIN_BACKEND_PATH}")
        print(f"[ERROR] Estructura esperada:")
        print(f"        {MODULOS_DIR}/login/logica/login_backend.py")
        
        if os.path.exists(MODULOS_DIR):
            try:
                items = os.listdir(MODULOS_DIR)
                print(f"[DEBUG] Contenido de {MODULOS_DIR}:")
                for item in sorted(items)[:10]:
                    print(f"        - {item}")
            except Exception as e:
                print(f"[ERROR] No se pudo leer {MODULOS_DIR}: {e}")
        else:
            print(f"[ERROR] ❌ MODULOS_DIR no existe: {MODULOS_DIR}")
        
        return None
    
    print(f"[OK] ✅ Archivo encontrado: {LOGIN_BACKEND_PATH}")
    
    # PASO 2: Crear especificación del módulo
    try:
        spec = importlib.util.spec_from_file_location("login_backend", LOGIN_BACKEND_PATH)
        
        if spec is None:
            print(f"[ERROR] ❌ No se pudo crear spec desde {LOGIN_BACKEND_PATH}")
            return None
        
        if spec.loader is None:
            print(f"[ERROR] ❌ spec.loader es None para {LOGIN_BACKEND_PATH}")
            return None
        
        print(f"[OK] ✅ Especificación del módulo creada")
        
    except Exception as e:
        print(f"[ERROR] ❌ Error creando spec: {type(e).__name__}: {e}")
        return None
    
    # PASO 3: Crear módulo
    try:
        module = importlib.util.module_from_spec(spec)
        print(f"[OK] ✅ Módulo creado desde especificación")
    except Exception as e:
        print(f"[ERROR] ❌ Error creando módulo: {type(e).__name__}: {e}")
        return None
    
    # PASO 4: Ejecutar el módulo (aquí ocurren imports del backend)
    try:
        sys.modules['login_backend'] = module
        spec.loader.exec_module(module)
        print(f"[OK] ✅ Módulo ejecutado exitosamente")
    except ModuleNotFoundError as mnf:
        print(f"[ERROR] ❌ Import error en login_backend.py: {mnf}")
        print(f"[ERROR]    Verifica que todas las dependencias estén instaladas")
        return None
    except SyntaxError as se:
        print(f"[ERROR] ❌ Syntax error en login_backend.py: {se}")
        print(f"[ERROR]    Línea {se.lineno}: {se.text}")
        return None
    except Exception as e:
        print(f"[ERROR] ❌ Error ejecutando módulo: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # PASO 5: Buscar objeto 'app' en el módulo
    try:
        backend_app = getattr(module, 'app', None)
        
        if backend_app is None:
            print(f"[ERROR] ❌ El módulo login_backend.py NO exporta 'app'")
            print(f"[ERROR]    Atributos disponibles en login_backend:")
            attrs = [a for a in dir(module) if not a.startswith('_')]
            for attr in attrs[:15]:
                print(f"            - {attr}")
            return None
        
        print(f"[OK] ✅ Objeto 'app' encontrado en login_backend.py")
        print(f"[OK] ✅ Tipo: {type(backend_app)}")
        
        return backend_app
        
    except AttributeError as ae:
        print(f"[ERROR] ❌ Error accediendo atributos del módulo: {ae}")
        return None
    except Exception as e:
        print(f"[ERROR] ❌ Error desconocido: {type(e).__name__}: {e}")
        return None


# Ejecutar carga del backend
backend_app = _load_login_backend()


# ========================================
# CONSTRUCCIÓN DE APP WSGI FINAL
# ========================================
print("\n[STEP 3] Construyendo app WSGI final con DispatcherMiddleware...")

if backend_app is not None:
    print(f"[OK] Backend app cargado. Montando en ruta /api...")
    
    # Montar el backend en /api
    # Las rutas dentro de backend_app (**/auth/login, /auth/register, etc.)
    # se accederán como /api/auth/login, /api/auth/register, etc.
    app = DispatcherMiddleware(front_app, {
        '/api': backend_app
    })
    
    print(f"[OK] ✅ DispatcherMiddleware creado:")
    print(f"    - '/' → front_app (estáticos del frontend)")
    print(f"    - '/api' → backend_app (login backend)")
    print(f"\n[OK] ✅ App WSGI lista para Gunicorn")
    print(f"    Comando: gunicorn run:app --workers 1 --threads 2 --worker-class gthread")
    
else:
    print(f"[WARN] ⚠️  Backend NO se cargó correctamente")
    print(f"[WARN] Operando en modo FRONTEND-ONLY (sin backend)")
    print(f"[WARN] Las rutas /api/* no estarán disponibles")
    app = front_app

# VALIDACIÓN CRÍTICA
if app is None:
    print(f"\n[FATAL] ❌ ERROR CRÍTICO: app es None")
    print(f"[FATAL] No se pudo crear la aplicación WSGI")
    sys.exit(1)

print(f"\n[OK] ✅ Variable 'app' exportada correctamente para Gunicorn")
print("=" * 80 + "\n")


# ========================================
# MODO DESARROLLO (Ejecución local con run_simple)
# ========================================
if __name__ == "__main__":
    print("\n[LOCAL DEV] Iniciando servidor de desarrollo...")
    print(f"[LOCAL DEV] Host:   0.0.0.0")
    print(f"[LOCAL DEV] Puerto: {PORT}")
    print(f"[LOCAL DEV] URL:    http://localhost:{PORT}")
    print(f"[LOCAL DEV] Presiona Ctrl+C para detener")
    print("=" * 80 + "\n")
    
    run_simple(
        "0.0.0.0",
        PORT,
        app,
        use_debugger=True,
        use_reloader=True
    )