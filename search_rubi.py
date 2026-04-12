#!/usr/bin/env python3
"""Buscar usuario 'Rubí Hernández López' en traslados y perfiles"""

from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=== BÚSQUEDA DE 'RUBÍ HERNÁNDEZ LÓPEZ' ===\n")
    
    # 1. Buscar en traslados por nombre de paciente
    print("1️⃣ Buscando en tabla TRASLADOS por paciente_nombre...")
    res = supabase.table('traslados').select('*').ilike('paciente_nombre', '%Rubí%').execute()
    
    if res.data:
        print(f"✅ Encontrado {len(res.data)} registro(s) de traslados:\n")
        for t in res.data:
            print(f"  ID: {t['id']}")
            print(f"  Paciente: {t.get('paciente_nombre')}")
            print(f"  CURP: {t.get('paciente_curp')}")
            print(f"  Destino: {t.get('destino_hospital')}")
            print(f"  Fecha: {t.get('fecha_solicitud')}")
            print(f"  Estatus: {t.get('estatus')}")
            print()
    else:
        print("❌ No encontrado en traslados\n")
    
    # 2. Buscar en perfiles
    print("2️⃣ Buscando en tabla PERFILES por nombre...")
    res2 = supabase.table('perfiles').select('*').ilike('nombre_completo', '%Rubí%').execute()
    
    if res2.data:
        print(f"✅ Encontrado {len(res2.data)} perfil(es):\n")
        for p in res2.data:
            print(f"  ID: {p['id']}")
            print(f"  Nombre: {p.get('nombre_completo')}")
            print(f"  Email: {p.get('nombre_usuario')}")
            print(f"  Rol: {p.get('rol')}")
            print(f"  Teléfono: {p.get('telefono')}")
            print()
            
            # Si tiene rol de usuario_traslados, verificar sus traslados
            if 'traslado' in str(p.get('rol', '')).lower():
                print(f"  🔍 Buscando traslados registrados por este usuario...")
                t_res = supabase.table('traslados').select('*').eq('registrado_por', p['id']).execute()
                if t_res.data:
                    print(f"     → Total traslados: {len(t_res.data)}")
                else:
                    print(f"     → Sin traslados registrados")
    else:
        print("❌ No encontrado en perfiles\n")
    
    print("\n3️⃣ Listado de todos los usuarios disponibles:")
    res3 = supabase.table('perfiles').select('id, nombre_completo, nombre_usuario, rol').execute()
    for p in res3.data:
        print(f"  - {p['nombre_completo']} ({p['nombre_usuario']}) [Rol: {p['rol']}]")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
