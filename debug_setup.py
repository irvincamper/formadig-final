#!/usr/bin/env python3
"""
DEBUG SCRIPT - Verifica que el setup de run.py es correcto
Ejecuta esto en local para revisar los logs completos antes de hacer push a Render
"""

import os
import sys

print("\n" + "=" * 80)
print("🔍 DEBUGGING FORMADIG - Verificación de Setup")
print("=" * 80)

# 1. Verificar estructura de carpetas
print("\n[STEP 1] Verificando estructura de carpetas...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "Formadig", "1_Sistema_DIF_Acatlan")
BACKEND_PATH = os.path.join(FRONTEND_DIR, "modulos", "login", "logica", "login_backend.py")

print(f"BASE_DIR: {BASE_DIR}")
print(f"FRONTEND_DIR: {FRONTEND_DIR}")
print(f"BACKEND_PATH: {BACKEND_PATH}")
print(f"¿FRONTEND_DIR existe? {os.path.exists(FRONTEND_DIR)}")
print(f"¿BACKEND_PATH existe? {os.path.exists(BACKEND_PATH)}")

# 2. Verificar que el backend puede importarse
print("\n[STEP 2] Intentando importar backend...")

import importlib.util

try:
    spec = importlib.util.spec_from_file_location("login_backend", BACKEND_PATH)
    if spec is None:
        print("❌ spec es None")
        sys.exit(1)
    
    if spec.loader is None:
        print("❌ spec.loader es None")
        sys.exit(1)
    
    module = importlib.util.module_from_spec(spec)
    sys.modules['login_backend'] = module
    
    print("Ejecutando spec.loader.exec_module...")
    spec.loader.exec_module(module)
    print("✅ Módulo ejecutado exitosamente")
    
    # 3. Verificar que tiene 'app'
    print("\n[STEP 3] Buscando objeto 'app'...")
    
    backend_app = getattr(module, 'app', None)
    
    if backend_app is None:
        print("❌ No se encontró objeto 'app' en login_backend")
        print(f"Atributos disponibles: {[a for a in dir(module) if not a.startswith('_')]}")
        sys.exit(1)
    
    print(f"✅ app encontrado: {type(backend_app)}")
    
    # 4. Verificar rutas del backend
    print("\n[STEP 4] Rutas del backend...")
    routes = list(backend_app.url_map.iter_rules())
    print(f"Total de rutas: {len(routes)}")
    for route in routes[:10]:
        print(f"  - {route}")
    
    # 5. Verificar CORS
    print("\n[STEP 5] Verificando CORS...")
    if hasattr(module, 'CORS'):
        print("✅ CORS está configurado")
    else:
        print("⚠️  CORS puede no estar configurado")
    
    # 6. Verificar Supabase
    print("\n[STEP 6] Verificando Supabase...")
    supabase_url = os.getenv("SUPABASE_URL", "NO CONFIGURADO")
    supabase_key = os.getenv("SUPABASE_KEY", "NO CONFIGURADO")
    
    print(f"SUPABASE_URL: {'✅ Configurado' if supabase_url != 'NO CONFIGURADO' else '❌ NO CONFIGURADO'}")
    print(f"SUPABASE_KEY: {'✅ Configurado' if supabase_key != 'NO CONFIGURADO' else '❌ NO CONFIGURADO'}")
    
    print("\n" + "=" * 80)
    print("✅ TODO PARECE ESTAR BIEN")
    print("=" * 80)
    print("\nAhora puedes hacer:")
    print("  python run.py       - Para ejecutar en local")
    print("  git push            - Para hacer deploy a Render")
    print("\n" + "=" * 80 + "\n")
    
except ImportError as ie:
    print(f"❌ ImportError: {ie}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
