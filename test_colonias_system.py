#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test para verificar sistema de colonias
Sin necesidad de levantar todos los servidores
"""

import sys
import os

# Agregar ruta para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from supabase import create_client, Client

def test_supabase_connection():
    """Verifica conexión a Supabase"""
    print("\n" + "="*60)
    print("🔌 TEST 1: Conexión a Supabase")
    print("="*60)
    
    try:
        # Cargar variables
        url = os.getenv("SUPABASE_URL") or input("Ingresa SUPABASE_URL: ").strip()
        key = os.getenv("SUPABASE_KEY") or input("Ingresa SUPABASE_KEY: ").strip()
        
        supabase: Client = create_client(url, key)
        print("✅ Conexión exitosa a Supabase")
        return supabase
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None


def test_colonias_table(supabase):
    """Verifica que tabla colonias_acatlan existe y tiene datos"""
    print("\n" + "="*60)
    print("📊 TEST 2: Tabla colonias_acatlan")
    print("="*60)
    
    try:
        # Verificar que tabla existe
        result = supabase.table("colonias_acatlan").select("*").limit(1).execute()
        print(f"✅ Tabla existe")
        
        # Contar total de registros
        count_result = supabase.table("colonias_acatlan").select("id", count="exact").execute()
        total = count_result.count if hasattr(count_result, 'count') else len(count_result.data)
        print(f"   Total de registros: {total}")
        
        return total > 0
        
    except Exception as e:
        print(f"❌ Error accediendo tabla: {e}")
        return False


def test_colonias_by_cp(supabase, cp="28018"):
    """Prueba query de colonias por código postal"""
    print("\n" + "="*60)
    print(f"🔍 TEST 3: Buscar colonias para CP: {cp}")
    print("="*60)
    
    try:
        colonias = supabase.table("colonias_acatlan")\
            .select("id, nombre, codigo_postal")\
            .eq("codigo_postal", cp.strip())\
            .execute()
        
        if colonias.data:
            print(f"✅ Se encontraron {len(colonias.data)} colonia(s):")
            for i, col in enumerate(colonias.data, 1):
                print(f"   [{i}] {col.get('nombre', 'N/A')} (ID: {col.get('id')})")
            return True
        else:
            print(f"⚠️  No hay colonias para CP: {cp}")
            print("  PRÓXIMO PASO: Verifica que existan datos en Supabase o prueba otro CP")
            return False
            
    except Exception as e:
        print(f"❌ Error en query: {e}")
        return False


def test_different_cps(supabase):
    """Busca CPZ que tienen colonias"""
    print("\n" + "="*60)
    print("📋 TEST 4: Códigos Postales disponibles")
    print("="*60)
    
    try:
        result = supabase.table("colonias_acatlan")\
            .select("codigo_postal")\
            .execute()
        
        if result.data:
            # Obtener CPZ únicos
            unique_cps = set()
            for row in result.data:
                cp = row.get("codigo_postal")
                if cp:
                    unique_cps.add(cp)
            
            print(f"✅ Se encontraron {len(unique_cps)} código(s) postal(es) diferentes:")
            for cp in sorted(unique_cps)[:10]:  # Mostrar solo primeros 10
                print(f"   - {cp}")
            
            if len(unique_cps) > 10:
                print(f"   ... y {len(unique_cps) - 10} más")
            
            return list(unique_cps)
        else:
            print("⚠️  No hay datos en tabla")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def test_rls_policy(supabase):
    """Intenta verificar RLS (limitado sin acceso directo a BD)"""
    print("\n" + "="*60)
    print("🔐 TEST 5: Row Level Security (RLS)")
    print("="*60)
    
    print("⚠️  NOTA: Verificación limitada sin acceso directo a BD")
    print("    Para revisar RLS completo:")
    print("    1. Ve a Supabase Dashboard")
    print("    2. Tabla: colonias_acatlan")
    print("    3. Pestaña: Authentication → Policies")
    print("    4. Verifica que exista SELECT policy para rol 'anon' o 'authenticated'")
    
    # Intenta una query anónima
    try:
        # Si llega aquí, RLS probablemente permite lectura
        result = supabase.table("colonias_acatlan")\
            .select("id")\
            .limit(1)\
            .execute()
        
        if result.data is not None:  # Nota: vacío es diferente de None o error
            print("✅ RLS permite lectura (o está deshabilitado)")
            return True
        else:
            print("⚠️  RLS podría estar bloqueando lecturas")
            return False
            
    except Exception as e:
        if "403" in str(e) or "permission" in str(e).lower():
            print(f"❌ RLS está bloqueando: {e}")
            return False
        else:
            print(f"⚠️  Error en RLS check: {e}")
            return False


def generate_sample_data(supabase):
    """Inserta datos de prueba si tabla está vacía"""
    print("\n" + "="*60)
    print("➕ TEST 6: Generar datos de prueba (OPCIONAL)")
    print("="*60)
    
    try:
        count = supabase.table("colonias_acatlan").select("id", count="exact").execute()
        total = count.count if hasattr(count, 'count') else len(count.data)
        
        if total > 0:
            print(f"✅ Ya hay {total} registros, no se insertarán datos")
            return
        
        print("⚠️  Tabla vacía, insertando datos de prueba...")
        
        sample_data = [
            {"codigo_postal": "28018", "nombre": "Centro"},
            {"codigo_postal": "28018", "nombre": "Reforma"},
            {"codigo_postal": "28020", "nombre": "Santa María"},
            {"codigo_postal": "28020", "nombre": "Guadalupe"},
            {"codigo_postal": "28022", "nombre": "San Francisco"},
        ]
        
        result = supabase.table("colonias_acatlan").insert(sample_data).execute()
        print(f"✅ Se insertaron {len(result.data)} registros de prueba")
        
    except Exception as e:
        print(f"❌ Error al insertar: {e}")


def main():
    """Ejecutar todos los tests"""
    print("\n" + "🧪 "*30)
    print("DIAGNOSTICO DEL SISTEMA DE COLONIAS")
    print("🧪 "*30 + "\n")
    
    # Test 1: Conexión
    supabase = test_supabase_connection()
    if not supabase:
        print("\n❌ No se puede continuar sin conexión a Supabase")
        return
    
    # Test 2: Tabla existe
    table_exists = test_colonias_table(supabase)
    if not table_exists:
        print("\n⚠️  Tabla existe pero está vacía")
    
    # Test 3: Buscar colonias por CP
    test_colonias_by_cp(supabase, "28018")
    
    # Test 4: CPZ disponibles
    available_cps = test_different_cps(supabase)
    
    if available_cps:
        # Test con primer CP disponible
        print(f"\n📌 Probando con CP: {available_cps[0]}")
        test_colonias_by_cp(supabase, available_cps[0])
    
    # Test 5: RLS
    test_rls_policy(supabase)
    
    # Test 6: Datos de prueba
    if input("\n¿Generar datos de prueba? (s/n): ").lower() == 's':
        generate_sample_data(supabase)
    
    # Resumen
    print("\n" + "="*60)
    print("📋 RESUMEN")
    print("="*60)
    print("Si todos los tests pasaron ✅:")
    print("  → Backend debería funcionar correctamente")
    print("  → Si aún no funciona en frontend, revisar JavaScript")
    print("  → Abrir DevTools (F12) y ver logs en consola")
    print("\nSi algún test falló ❌:")
    print("  → Revisar el error específico arriba")
    print("  → Soluciones en GUIA_COLONIAS_DEBUG.md")


if __name__ == "__main__":
    main()
