#!/usr/bin/env python3
"""
Diagnóstico rápido del error de login
"""
import os
import sys

print("=" * 80)
print("🔍 DIAGNÓSTICO DE LOGIN - FORMADIG")
print("=" * 80)

# 1. Verificar .env
print("\n[1] Verificando .env file...")
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"✅ .env EXISTE en: {env_path}")
    with open(env_path, 'r') as f:
        content = f.read()
        if 'SUPABASE_URL' in content:
            print("✅ SUPABASE_URL está configurada")
        else:
            print("❌ SUPABASE_URL NO está configurada")
        if 'SUPABASE_KEY' in content:
            print("✅ SUPABASE_KEY está configurada")
        else:
            print("❌ SUPABASE_KEY NO está configurada")
else:
    print(f"❌ .env NO EXISTE en: {env_path}")
    sys.exit(1)

# 2. Verificar python-dotenv
print("\n[2] Verificando python-dotenv...")
try:
    from dotenv import load_dotenv
    print("✅ python-dotenv ESTÁ INSTALADO")
    load_dotenv()
    print("✅ Variables de .env CARGADAS")
except ImportError:
    print("❌ python-dotenv NO ESTÁ INSTALADO")
    print("   Ejecuta: pip install python-dotenv")
    sys.exit(1)

# 3. Verificar Supabase credentials
print("\n[3] Verificando Supabase credentials...")
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if supabase_url:
    print(f"✅ SUPABASE_URL={supabase_url[:30]}...")
else:
    print("❌ SUPABASE_URL NO CARGADA")

if supabase_key:
    print(f"✅ SUPABASE_KEY={supabase_key[:20]}...")
else:
    print("❌ SUPABASE_KEY NO CARGADA")

# 4. Verificar login_backend.py
print("\n[4] Verificando login_backend.py...")
login_backend_path = os.path.join(
    os.path.dirname(__file__),
    'dif_acatlan_system', 'modulos', 'login', 'logica', 'login_backend.py'
)
if os.path.exists(login_backend_path):
    print(f"✅ login_backend.py EXISTE")
else:
    print(f"❌ login_backend.py NO EXISTE en {login_backend_path}")

# 5. Verificar que Flask puede cargar el backend
print("\n[5] Intentando cargar login_backend...")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("login_backend", login_backend_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'app'):
            print("✅ login_backend.app CARGADO EXITOSAMENTE")
            # Intentar verificar ruta
            with open(login_backend_path, 'r') as f:
                content = f.read()
                if '@app.route' in content and '/auth/login' in content:
                    print("✅ Ruta /auth/login DEFINIDA")
        else:
            print("❌ login_backend NO TIENE atributo 'app'")
    else:
        print("❌ No se pudo crear spec para login_backend")
except Exception as e:
    print(f"❌ Error cargando login_backend: {e}")

print("\n" + "=" * 80)
print("RESUMEN:")
print("=" * 80)
if supabase_url and supabase_key:
    print("✅ Sistema PARECE estar configurado correctamente")
    print("\nPróximos pasos:")
    print("1. Ejecuta: python run.py")
    print("2. Abre: http://localhost:10000")
    print("3. Intenta loguear")
else:
    print("❌ Faltan credenciales de Supabase")
    print("\nVerifica el archivo .env")
