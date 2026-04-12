#!/usr/bin/env python3
"""
Script de depuración: Verificar estado de Desayunos Calientes en Supabase
Este script verifica:
1. Qué tablas existen en Supabase
2. Cuántos registros hay en cada tabla
3. Qué errores retorna la API
"""

import os
import sys

# Agregar Formadig al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Formadig'))

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ FALTA: pip install supabase")
    sys.exit(1)

# Conexión a Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")
client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 70)
print("DEBUG: Desayunos Calientes - Verificación de Tablas y Datos")
print("=" * 70)

# ============================================================================
# 1. Verificar tabla 'desayunos_calientes'
# ============================================================================
print("\n[1] Verificando tabla 'desayunos_calientes'...")
try:
    res = client.table('desayunos_calientes').select('*').limit(1).execute()
    count_res = client.table('desayunos_calientes').select('id', count='exact').execute()
    total = count_res.count if hasattr(count_res, 'count') else len(res.data)
    print(f"    ✅ Tabla EXISTS - Total de registros: {total}")
    if res.data:
        print(f"    📋 Ejemplo de registro: {res.data[0]}")
except Exception as e:
    print(f"    ❌ Tabla NO ENCONTRADA o ERROR: {e}")

# ============================================================================
# 2. Verificar tabla 'desayunos_eaeyd' (alternativa)
# ============================================================================
print("\n[2] Verificando tabla 'desayunos_eaeyd'...")
try:
    res = client.table('desayunos_eaeyd').select('*').limit(1).execute()
    total = len(res.data) if res.data else 0
    print(f"    ✅ Tabla EXISTS - Primeros registros: {total}")
    
    # Contar cuántos tienen tipo_apoyo == 'Calientes'
    res_calientes = client.table('desayunos_eaeyd').select('*').eq('tipo_apoyo', 'Calientes').limit(10).execute()
    total_calientes = len(res_calientes.data) if res_calientes.data else 0
    print(f"    📊 Registros con tipo_apoyo='Calientes': {total_calientes}")
    
    if res.data:
        print(f"    📋 Ejemplo de registro: {res.data[0]}")
except Exception as e:
    print(f"    ❌ Tabla NO ENCONTRADA o ERROR: {e}")

# ============================================================================
# 3. Verificar tabla 'desayunos_frios' (referencia - funciona)
# ============================================================================
print("\n[3] Verificando tabla 'desayunos_frios' (REFERENCIA - funciona)...")
try:
    res = client.table('desayunos_frios').select('*').limit(1).execute()
    count_res = client.table('desayunos_frios').select('id', count='exact').execute()
    total = count_res.count if hasattr(count_res, 'count') else len(res.data)
    print(f"    ✅ Tabla EXISTS - Total de registros: {total}")
    if res.data:
        print(f"    📋 Ejemplo de registro keys: {list(res.data[0].keys())}")
except Exception as e:
    print(f"    ❌ Tabla NO ENCONTRADA o ERROR: {e}")

# ============================================================================
# 4. Lista todas las tablas disponibles
# ============================================================================
print("\n[4] Intentando listar todas las tablas disponibles...")
try:
    # Nota: Supabase REST API no tiene endpoint directo para listar tablas
    # Pero podemos intentar acceder a information_schema si hay RLS deshabilitado
    tablas_conocidas = [
        'desayunos_calientes',
        'desayunos_frios',
        'desayunos_eaeyd',
        'desayunos',
        'solicitudes_desayunos',
        'beneficiarios_desayunos'
    ]
    
    tablas_disponibles = []
    for tabla in tablas_conocidas:
        try:
            res = client.table(tabla).select('*').limit(1).execute()
            tablas_disponibles.append(tabla)
            print(f"    ✅ {tabla}")
        except:
            pass
    
    if not tablas_disponibles:
        print("    ⚠️  No se encontraron tablas conocidas")
    else:
        print(f"\n    📊 Total de tablas encontradas: {len(tablas_disponibles)}")
        
except Exception as e:
    print(f"    ❌ Error: {e}")

# ============================================================================
# 5. Verificar API endpoint
# ============================================================================
print("\n[5] Verificando API endpoint /api/desayunos_calientes...")
try:
    import requests
    import time
    
    # Intentar contra servidor local (si está corriendo)
    urls = [
        'http://localhost:5000/api/desayunos_calientes',
        'http://localhost:8000/api/desayunos_calientes',
        'http://127.0.0.1:5000/api/desayunos_calientes',
    ]
    
    for url in urls:
        try:
            print(f"    🔍 Intentando {url}...")
            resp = requests.get(url, timeout=3)
            print(f"    ✅ Respuesta HTTP {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"    📊 Registros en respuesta: {len(data.get('desayunos', []))}")
            else:
                print(f"    ⚠️  Error: {resp.text[:200]}")
            break
        except requests.exceptions.ConnectionError:
            print(f"    ❌ No se puede conectar a {url}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
except ImportError:
    print("    ⏭️  (Skip - no requests library)")

print("\n" + "=" * 70)
print("✅ Debug completado. Revisa los errores arriba.")
print("=" * 70)
