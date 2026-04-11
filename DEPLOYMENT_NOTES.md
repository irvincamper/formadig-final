# Notas de Despliegue - FORMADIG en Render

## Cambios Realizados

### 1. Archivos JavaScript Actualizados
Se han reemplazado todas las URLs absolutas con puertos locales por **rutas relativas `/api/...`**:

| Archivo | Cambio |
|---------|--------|
| `Formadig/1_Sistema_DIF_Acatlan/core/formadig-core.js` | ✅ `http://localhost:5001/api/auth` → `/api/auth` |
| `dif_acatlan_system/core/core.js` | ✅ `http://localhost:5001/api/auth` → `/api/auth` |
| `admin_desayunos_frios.js` | ✅ `http://localhost:5005/api/desayunos_frios` → `/api/desayunos_frios` |
| `admin_desayunos_calientes.js` | ✅ `http://localhost:5006/api/desayunos_calientes` → `/api/desayunos_calientes` |
| `sms.js` | ✅ `http://{host}:5009/api/sms` → `/api/sms` |

### 2. run.py - Configuración WSGI 
El archivo `run.py` ya está configurado correctamente con `DispatcherMiddleware`:

```python
if login_app is not None:
    app = DispatcherMiddleware(front_app, {'/api': login_app})
```

**Esto significa:**
- Solicitudes a `/` → Servidas por `front_app` (estáticos del frontend)
- Solicitudes a `/api/*` → Enrutadas a `login_app` (backend de autenticación)
- El objeto `app` es exportable para `gunicorn run:app`

## 🚀 Cómo Funciona Ahora en Render

```
Navegador del Usuario
        ↓
   RENDER (1 dyno)
        ↓
   Gunicorn (run:app)
   ├── / route → Flask frontend (HTML, CSS, JS)
   └── /api/* → login_backend.py (autenticación)
```

## ⚠️ Limitaciones Actuales

Con la configuración de **bajo consumo de memoria** (solo cargando el backend de Login), funciona:

✅ **Módulo de Login**: Autenticación total
✅ **Pantalla de Estáticos**: Todo el HTML/CSS/JS
❌ **Otros Módulos**: Desayunos Fríos, Calientes, SMS, Chatbot (Aún no tienen backends montados en `/api`)

### Para Habilitar Otros Módulos

Cuando quieras agregar más funcionalidad, debes:

1. Editar `run.py` para cargar más backends (Similar a `_load_login_backend()`)
2. Montar cada backend bajo `/api` en el `DispatcherMiddleware`
3. Aumentar el límite de memoria en Render o usar múltiples dynos

**Ejemplo para agregar Desayunos Fríos:**
```python
def _load_desayunos_frios_backend():
    backend_path = os.path.join(MODULOS_DIR, "admin_desayunos_frios", "logica", "admin_desayunos_frios_backend.py")
    # ...carga similar a login...

# Entonces:
backends_mounted = {
    '/api': login_app,
    '/api/desayunos_frios': desayunos_frios_app
}
app = DispatcherMiddleware(front_app, backends_mounted)
```

## 📋 Checklist para Render

- [ ] Asegúrate de que `requirements.txt` incluya: `Flask`, `Werkzeug`, `gunicorn`
- [ ] En Render, configura el comando de inicio como:
  ```bash
  gunicorn run:app --workers 1 --threads 2 --worker-class gthread --bind 0.0.0.0:$PORT --timeout 30
  ```
- [ ] Revisa los logs de Render si hay errores: Dashboard → Your App → Logs
- [ ] Verifica que el archivo `Formadig/1_Sistema_DIF_Acatlan/modulos/login/logica/login_backend.py` exista y exporte un objeto `app`

## 🔍 Debugging en Render

Si ves un Error 502 o similar:

1. **Revisa los logs:**
   ```
   [INFO] BASE_DIR: /opt/render/project/src
   [INFO] FRONTEND_DIR: /opt/render/project/src/Formadig/1_Sistema_DIF_Acatlan
   [OK] Backend de Login cargado exitosamente
   ```

2. **Si ves `[WARN] App WSGI en modo frontend-only`:**
   - El login_backend.py no se cargó
   - Verifica las rutas en los logs
   - Confirma que el archivo existe en la estructura de carpetas

3. **Si ves `[ERROR]` en carga de módulos:**
   - Hay un problema de sintaxis o importación en `login_backend.py`
   - Revisa la traza completa en los logs

## 📝 Testing Local

Para verificar que todo funciona antes de hacer push a Render:

```bash
# Terminal 1: Ejecutar run.py
python run.py

# Terminal 2: Probar login
curl -X POST http://localhost:10000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Navegador: Acceder a login
http://localhost:10000
```

Debería mostrar la pantalla de login y poder procesar solicitudes de autenticación.
