"""
=============================================================================
WRAPPER PARA GUNICORN - FORMADIG v2.1
=============================================================================
Este archivo expone la aplicación unificada para Gunicorn en producción.
Gunicorn busca: gunicorn run:app
Por lo tanto, necesita encontrar "app" en este archivo.

Nota: app_unified.py está en la raíz, así que la importación es directa.
=============================================================================
"""

import os

# Importar y exponer la aplicación unificada desde app_unified.py (raíz)
from app_unified import app

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    print(f"\n🚀 Iniciando FORMADIG en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)