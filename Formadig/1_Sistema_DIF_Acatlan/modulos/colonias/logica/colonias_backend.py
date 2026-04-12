"""
Backend para Gestión de Colonias
Módulo: colonias_backend.py
Funcionalidad: Obtener colonias por código postal desde Supabase

⚠️ NOTA: Este archivo exporta un Blueprint para ser registrado en la app maestra unificada.
"""

from flask import Blueprint, request, jsonify
from supabase import create_client
import os

# Inicializar Blueprint
colonias_bp = Blueprint('colonias', __name__, url_prefix='/api/colonias')

# Inicializar Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://ctiqbycbkcftwuqgzxjb.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY', 'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================================
# GET /<cp> - Obtener colonias por código postal
# ============================================================================
@colonias_bp.route('/<cp>', methods=['GET'], strict_slashes=False)
def obtener_colonias_por_cp(cp):
    """
    Endpoint GET para obtener colonias por código postal.
    Consulta la tabla colonias_acatlan en Supabase.
    Devuelve array directo de objetos para mejor consumo en frontend.
    """
    try:
        # Validar que cp no esté vacío
        if not cp or not cp.strip():
            print(f"❌ CP vacío recibido")
            return jsonify({'error': 'Código Postal no puede estar vacío', 'colonias': []}), 400
        
        cp_clean = cp.strip()
        print(f"🔍 Buscando colonias para CP: {cp_clean}")
        
        # Consultar colonias por código postal
        response = supabase.table('colonias_acatlan').select('id, nombre, codigo_postal').eq('codigo_postal', cp_clean).execute()
        
        colonias = response.data if response.data else []
        
        print(f"✅ Se encontraron {len(colonias)} colonia(s) para CP {cp_clean}")
        if colonias:
            print(f"   Colonias: {[c.get('nombre') for c in colonias]}")
        
        # Devolver array limpio para mejor consumo frontend
        return jsonify(colonias), 200
        
    except Exception as e:
        print(f'❌ Error crítico al obtener colonias: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al obtener colonias: {str(e)}'}), 500


# ============================================================================
# GET / - Listar todas las colonias (opcional, para debug)
# ============================================================================
@colonias_bp.route('/', methods=['GET'], strict_slashes=False)
def listar_todas_colonias():
    """
    Endpoint GET para listar TODAS las colonias (sin filtro).
    Útil para debug. En producción, mejor usar el endpoint por CP.
    """
    try:
        # Obtener máximo 100 colonias para evitar sobrecargar
        response = supabase.table('colonias_acatlan').select('*').limit(100).execute()
        
        colonias = response.data if response.data else []
        
        return jsonify({
            'colonias': colonias,
            'total': len(colonias),
            'nota': 'Limitado a 100 registros para mejor rendimiento'
        }), 200
        
    except Exception as e:
        print(f'❌ Error al listar colonias: {str(e)}')
        return jsonify({'error': f'Error al listar colonias: {str(e)}'}), 500


# ============================================================================
# NOTA: El blueprint 'colonias_bp' se registra en la app maestra
# ============================================================================
