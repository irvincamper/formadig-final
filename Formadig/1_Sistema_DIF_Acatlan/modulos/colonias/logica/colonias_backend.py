"""
Backend para Gestión de Colonias
Módulo: colonias_backend.py
Funcionalidad: Obtener colonias por código postal desde Supabase
"""

from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os

# Crear aplicación Flask
app = Flask(__name__)
CORS(app)

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
    """
    try:
        # Validar que cp no esté vacío
        if not cp or not cp.strip():
            return jsonify({'error': 'Código Postal no puede estar vacío'}), 400
        
        # Consultar colonias por código postal
        response = supabase.table('colonias_acatlan').select('id, nombre, codigo_postal').eq('codigo_postal', cp.strip()).execute()
        
        colonias = response.data if response.data else []
        
        # Si no hay resultados, retornar lista vacía (no es error)
        return jsonify({
            'colonias': colonias,
            'total': len(colonias),
            'codigo_postal': cp.strip()
        }), 200
        
    except Exception as e:
        print(f'❌ Error al obtener colonias: {str(e)}')
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
# Registro del Blueprint en la app
# ============================================================================
app.register_blueprint(colonias_bp)

# ============================================================================
# Ejecutar servidor Flask
# ============================================================================
if __name__ == '__main__':
    print("\n🏘️ Backend Colonias iniciado en puerto 5010")
    print(f"📍 Rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    app.run(host='0.0.0.0', port=5010, debug=False, use_reloader=False)
