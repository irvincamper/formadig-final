#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test individual de backend colonias sin levantar todos los servidores
Útil para diagnosticar problemas sin ruido de otros backends
"""

import os
import sys
import json
from pathlib import Path

# Agregar paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

print("\n" + "="*70)
print("🧪 TEST INDIVIDUAL - Backend Colonias")
print("="*70 + "\n")

# ============================================
# STEP 1: Verificar que archivo existe
# ============================================
print("📁 PASO 1: Verificar archivo backend")
print("-" * 70)

backend_path = Path(__file__).parent / "Formadig" / "1_Sistema_DIF_Acatlan" / "modulos" / "colonias" / "logica" / "colonias_backend.py"

if not backend_path.exists():
    print(f"❌ No se encontró: {backend_path}")
    print("\nBuscando alternativa...")
    
    # Buscar recursivamente
    for path in Path(__file__).parent.rglob("colonias_backend.py"):
        print(f"   ℹ️  Encontrado en: {path}")
        backend_path = path
        break

if backend_path.exists():
    print(f"✅ Archivo encontrado: {backend_path}")
else:
    print("❌ No se puede encontrar colonias_backend.py")
    print("   Asegúrate de que está en Formadig/1_Sistema_DIF_Acatlan/modulos/colonias/logica/")
    sys.exit(1)

# ============================================
# STEP 2: Verificar imports
# ============================================
print("\n📦 PASO 2: Verificar dependencies")
print("-" * 70)

required_packages = {
    'flask': 'Flask',
    'flask_cors': 'CORS',
    'supabase': 'Supabase',
    'dotenv': 'Environment variables',
}

missing = []
for package, name in required_packages.items():
    try:
        __import__(package)
        print(f"✅ {name} disponible")
    except ImportError:
        print(f"❌ {name} NO disponible (falta: pip install {package})")
        missing.append(package)

if missing:
    print(f"\n⚠️  Falta instalar: {' '.join(missing)}")
    print(f"   Ejecuta: pip install {' '.join(missing)}")
    sys.exit(1)

# ============================================
# STEP 3: Cargar variables de entorno
# ============================================
print("\n🔑 PASO 3: Cargar variables de entorno")
print("-" * 70)

from dotenv import load_dotenv

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url:
    print("❌ SUPABASE_URL no configurado")
    print("   Agregar a .env: SUPABASE_URL=https://...")
    sys.exit(1)

if not supabase_key:
    print("❌ SUPABASE_KEY no configurado")
    print("   Agregar a .env: SUPABASE_KEY=...")
    sys.exit(1)

print(f"✅ SUPABASE_URL: {supabase_url[:30]}...")
print(f"✅ SUPABASE_KEY: {supabase_key[:20]}...")

# ============================================
# STEP 4: Conectar a Supabase
# ============================================
print("\n🌐 PASO 4: Conectar a Supabase")
print("-" * 70)

from supabase import create_client

try:
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Conexión a Supabase exitosa")
except Exception as e:
    print(f"❌ Error conectando: {e}")
    sys.exit(1)

# ============================================
# STEP 5: Verificar tabla colonias_acatlan
# ============================================
print("\n📊 PASO 5: Verificar tabla colonias_acatlan")
print("-" * 70)

try:
    result = supabase.table("colonias_acatlan").select("*").limit(1).execute()
    print("✅ Tabla colonias_acatlan existe")
    
    # Contar registros
    count_result = supabase.table("colonias_acatlan").select("id", count="exact").execute()
    total = count_result.count if hasattr(count_result, 'count') else 0
    print(f"   Total de registros: {total}")
    
    if total == 0:
        print("   ⚠️  Tabla vacía - inserta datos de prueba")
    
except Exception as e:
    print(f"❌ Error accediendo tabla: {e}")
    if "does not exist" in str(e):
        print("   → Tabla no existe. Créala en Supabase Dashboard")
    sys.exit(1)

# ============================================
# STEP 6: Probar query de colonias
# ============================================
print("\n🔍 PASO 6: Probar query de colonias")
print("-" * 70)

test_cps = ["28018", "28020", "28022"]

for cp in test_cps:
    try:
        colonias = supabase.table("colonias_acatlan")\
            .select("id, nombre, codigo_postal")\
            .eq("codigo_postal", cp)\
            .execute()
        
        if colonias.data:
            print(f"✅ CP {cp}: {len(colonias.data)} colonia(s) encontradas")
            for col in colonias.data[:2]:  # Mostrar máximo 2
                print(f"   - {col.get('nombre')}")
        else:
            print(f"⚠️  CP {cp}: No hay datos para este CP")
            
    except Exception as e:
        print(f"❌ CP {cp}: Error - {e}")

# ============================================
# STEP 7: Simular respuesta del backend
# ============================================
print("\n📤 PASO 7: Simular respuesta del backend")
print("-" * 70)

cp_test = "28018"
print(f"Simulando: GET /api/colonias/{cp_test}")
print()

try:
    colonias = supabase.table("colonias_acatlan")\
        .select("id, nombre, codigo_postal")\
        .eq("codigo_postal", cp_test.strip())\
        .execute()
    
    print("Respuesta (formato JSON):")
    print(json.dumps(colonias.data, indent=2, ensure_ascii=False))
    
    if colonias.data:
        print(f"\n✅ El frontend recibiría un array con {len(colonias.data)} colonias")
        print("   El JavaScript iteraría y crearía <option> elements")
    else:
        print(f"\n⚠️  Array vacío - dropdown aparecería sin opciones")
        
except Exception as e:
    print(f"❌ Error: {e}")

# ============================================
# STEP 8: Probar conversión de datos
# ============================================
print("\n🔄 PASO 8: Validar formato para frontend")
print("-" * 70)

colonias = supabase.table("colonias_acatlan")\
    .select("id, nombre, codigo_postal")\
    .eq("codigo_postal", "28018")\
    .execute()

test_data = colonias.data if colonias.data else [
    {"id": 1, "nombre": "Centro", "codigo_postal": "28018"},
    {"id": 2, "nombre": "Reforma", "codigo_postal": "28018"}
]

print("Simulando procesamiento en JavaScript:")
print()

for i, col in enumerate(test_data, 1):
    nombre = col.get('nombre', col.get('name', 'Unnamed'))
    print(f"   [{i}] Crear: <option value=\"{nombre}\">{nombre}</option>")

print(f"\n✅ Se crearían {len(test_data)} opciones en el dropdown")

# ============================================
# STEP 9: Status API
# ============================================
print("\n🚀 PASO 9: Resumen de API")
print("-" * 70)

print("""
La siguiente URL debería funcionar cuando levantes el backend:

GET http://localhost:5010/api/colonias/28018
Respuesta esperada: [{"id": 1, "nombre": "Centro", ...}, ...]

GET http://localhost:5010/api/colonias/
Respuesta esperada: todas las colonias en BD

Así probarlo:
  $ curl http://localhost:5010/api/colonias/28018
  $ python Formadig/1_Sistema_DIF_Acatlan/modulos/colonias/logica/colonias_backend.py
""")

# ============================================
# STEP 10: Instrucciones finales
# ============================================
print("\n✅ RESUMEN")
print("-" * 70)

print("""
Si llegaste aquí sin errores ❌:
  ✅ Supabase conecta correctamente
  ✅ Tabla colonias_acatlan existe
  ✅ Los datos sobre disponibles para consultar
  ✅ Backend debería funcionar sin problemas

Próximos pasos:

1. Levanta el servidor completo:
   $ python Formadig/run.py

2. Abre navegador:
   http://localhost:8000/modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html

3. Abre DevTools (F12):
   Console tab

4. Ingresa un CP como "28018" en el campo:
   Deberías ver logs en console

5. Si dropdown se llena → ✅ ÉXITO
   Si dropdown vacío → Revisar GUIA_COLONIAS_DEBUG.md

Si hay error en algún paso arriba → Revisa TROUBLESHOOTING_COLONIAS.md
""")

print("\n" + "="*70)
print("Test completado ✅")
print("="*70 + "\n")
