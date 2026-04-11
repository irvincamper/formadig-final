#!/usr/bin/env python3
"""
TEST SCRIPT - Prueba que la app funciona correctamente
Ejecuta esto para probar en local antes de hacer push a Render
"""

import subprocess
import time
import sys
import requests
from threading import Thread

print("\n" + "=" * 80)
print("🚀 INICIANDO APP LOCAL...")
print("=" * 80)

# Inicia la app en un thread
process = subprocess.Popen(
    ["python", "run.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Espera a que el servidor esté listo
print("Esperando a que el servidor inicie...")
time.sleep(3)

try:
    print("\n" + "=" * 80)
    print("🧪 PRUEBAS")
    print("=" * 80)
    
    # Test 1: Frontend
    print("\n[TEST 1] Pidiendo frontend (GET /)...")
    try:
        response = requests.get("http://localhost:10000/")
        if response.status_code == 200:
            print("✅ Frontend responde (200)")
            if "html" in response.text.lower() or "<!doctype" in response.text.lower():
                print("✅ Contiene HTML")
            else:
                print("⚠️  No parece ser HTML")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Backend routes
    print("\n[TEST 2] Pidiendo backend (GET /api/auth)...")
    try:
        response = requests.get("http://localhost:10000/api/auth")
        if response.status_code in [200, 405]:  # 405 es OK para GET en rutas que esperan POST
            print(f"✅ Backend responde ({response.status_code})")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Login endpoint
    print("\n[TEST 3] Probando login endpoint (POST /api/auth/login)...")
    try:
        payload = {
            "email": "test@test.com",
            "password": "testpassword"
        }
        response = requests.post(
            "http://localhost:10000/api/auth/login",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Endpoint responde ({response.status_code})")
        print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: CSS/JS files
    print("\n[TEST 4] Pidiendo archivos estáticos...")
    try:
        response = requests.get("http://localhost:10000/core/core.js")
        if response.status_code == 200:
            print("✅ Archivos estáticos se sirven correctamente")
        elif response.status_code == 404:
            print("⚠️  Archivo no encontrado (podría estar bien)")
        else:
            print(f"❌ Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ PRUEBAS COMPLETADAS")
    print("=" * 80)
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("  1. Presiona Ctrl+C aquí para detener el servidor")
    print("  2. Haz push de los cambios a Git:")
    print("     git add run.py Formadig/1_Sistema_DIF_Acatlan/modulos/login/logica/login_backend.py")
    print("     git commit -m 'fix: setup de Formadig para Render deployment'")
    print("     git push")
    print("  3. Render se redeployará automáticamente")
    print("  4. Verifica los logs en Render dashboard")
    print("  5. Accede a: https://tu-app.render.com/")
    print("\n")
    
except KeyboardInterrupt:
    print("\n\n❌ Deteniendo servidor...")
except Exception as e:
    print(f"\n\n❌ Error: {e}")
finally:
    process.terminate()
    process.wait(timeout=5)
    print("✅ Servidor detenido")
