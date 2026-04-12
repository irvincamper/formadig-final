"""
=============================================================================
WRAPPER PARA GUNICORN - FORMADIG v2.1
=============================================================================
Este archivo expone la aplicación unificada para Gunicorn en producción.
Gunicorn busca: gunicorn run:app
Por lo tanto, necesita encontrar "app" en este archivo.
=============================================================================
"""

import os
import sys

# Agregar la ruta del módulo a sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Formadig", "1_Sistema_DIF_Acatlan"))

# Importar y exponer la aplicación unificada desde app_unified.py
from app_unified import app

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Iniciando FORMADIG en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)