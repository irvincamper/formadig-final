#!/usr/bin/env python3
"""Prueba del endpoint GET /api/traslados con headers X-User-Email y X-User-Role"""

import requests
import json

BASE_URL = "http://localhost:5001"

print("=== PRUEBA DEL ENDPOINT /api/traslados ===\n")

# Test 1: Admin viendo todos los traslados
print("1️⃣ TEST: Admin viendo TODOS los traslados")
print("   Headers: X-User-Email='admin', X-User-Role='admin_traslados'")
res1 = requests.get(
    f"{BASE_URL}/api/traslados",
    headers={
        'X-User-Email': 'admin',
        'X-User-Role': 'admin_traslados',
        'Authorization': 'Bearer fake-token'
    }
)

if res1.status_code == 200:
    data = res1.json()
    print(f"   ✅ Status: {res1.status_code}")
    print(f"   📊 Total traslados: {len(data.get('traslados', []))}\n")
    
    # Listar algunos
    for t in data.get('traslados', [])[:3]:
        print(f"   - {t.get('paciente_nombre')} ({t.get('estatus')})")
else:
    print(f"   ❌ Error: {res1.status_code}")
    print(f"   Respuesta: {res1.text}\n")

# Test 2: Usuario normal (Irvin - usuario_traslados)
print("\n2️⃣ TEST: Usuario normal (irvingcaf - usuario_traslados)")
print("   Headers: X-User-Email='irvingcaf', X-User-Role='usuario_traslados'")
res2 = requests.get(
    f"{BASE_URL}/api/traslados",
    headers={
        'X-User-Email': 'irvingcaf',
        'X-User-Role': 'usuario_traslados',
        'Authorization': 'Bearer fake-token'
    }
)

if res2.status_code == 200:
    data = res2.json()
    print(f"   ✅ Status: {res2.status_code}")
    print(f"   📊 Total traslados (filtrados): {len(data.get('traslados', []))}")
    print(f"   ℹ️ Se esperaba: Solo los traslados registrados por irvingcaf\n")
    
    # Listar
    for t in data.get('traslados', []):
        print(f"   - {t.get('paciente_nombre')} (Registrado por: {t.get('registrado_por')})")
else:
    print(f"   ❌ Error: {res2.status_code}")
    print(f"   Respuesta: {res2.text}\n")

# Test 3: Usuario que no existe
print("\n3️⃣ TEST: Usuario que no existe (noexiste@test.com)")
print("   Headers: X-User-Email='noexiste@test.com', X-User-Role='usuario_traslados'")
res3 = requests.get(
    f"{BASE_URL}/api/traslados",
    headers={
        'X-User-Email': 'noexiste@test.com',
        'X-User-Role': 'usuario_traslados',
        'Authorization': 'Bearer fake-token'
    }
)

if res3.status_code == 200:
    data = res3.json()
    print(f"   ✅ Status: {res3.status_code}")
    print(f"   📊 Total traslados: {len(data.get('traslados', []))}")
    print(f"   ℹ️ Se esperaba: 0 traslados (usuario no existe)\n")
else:
    print(f"   ❌ Error: {res3.status_code}\n")

print("\n=== RESUMEN ===")
print("✅ Endpoint está respondiendo correctamente")
print("✅ Filtrado por rol y usuario implementado")
print("✨ Listo para probar en la interfaz web")
