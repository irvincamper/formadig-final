#!/usr/bin/env python3
"""Verificar tabla de traslados y usuarios registrados"""

from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ctiqbycbkcftwuqgzxjb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Obtener traslados
    res = supabase.table('traslados').select(
        'id, paciente_nombre, paciente_curp, destino_hospital, fecha_solicitud, estatus, registrado_por'
    ).order('fecha_solicitud', desc=True).limit(5).execute()
    
    print("=== TRASLADOS EN LA BASE DE DATOS ===")
    print(f"Total registros: {len(res.data)}")
    print()
    
    for t in res.data:
        print(f"ID: {t['id']}")
        print(f"  Paciente: {t.get('paciente_nombre', 'N/A')}")
        print(f"  CURP: {t.get('paciente_curp', 'N/A')}")
        print(f"  Destino: {t.get('destino_hospital', 'N/A')}")
        print(f"  Fecha Solicitud: {t.get('fecha_solicitud', 'N/A')}")
        print(f"  Estatus: {t.get('estatus', 'N/A')}")
        print(f"  Registrado Por (UUID): {t.get('registrado_por', 'NULL')}")
        
        # Si tiene registrado_por, buscar el perfil
        if t.get('registrado_por'):
            try:
                perfil_res = supabase.table('perfiles').select(
                    'nombre_usuario, nombre_completo, rol'
                ).eq('id', t['registrado_por']).execute()
                
                if perfil_res.data:
                    perfil = perfil_res.data[0]
                    print(f"  👤 Usuario: {perfil.get('nombre_completo', perfil.get('nombre_usuario'))}")
                    print(f"  📧 Email: {perfil.get('nombre_usuario')}")
                    print(f"  🎯 Rol: {perfil.get('rol')}")
            except Exception as e:
                print(f"  ⚠️ Error buscando perfil: {e}")
        print()
        
except Exception as e:
    print(f"❌ Error: {e}")
