# 📋 Configuración del Sistema run.py

## 🎯 Visión General

El nuevo `run.py` implementa un **DispatcherMiddleware único** que:

- ✅ Carga todos los backends de forma eficiente con `importlib`
- ✅ Evita `subprocess.Popen` (mejor rendimiento y menos memoria)
- ✅ Monta cada backend en una ruta `/api/*` específica
- ✅ Permite activar/desactivar módulos fácilmente
- ✅ Proporciona logging detallado de cada carga

## 📊 Estado Actual (Verificado)

**Módulos Cargados:** 4 de 4 ✅

```
- '/'                  → Frontend (estático)
- '/api/auth'          → Backend de Login
- '/api/traslados'     → Backend de Traslados
- '/api/desayunos_frios' → Backend de Desayunos Fríos
- '/api/sms'           → Backend de SMS
```

## 🔧 Cómo Activar/Desactivar Módulos

### Paso 1: Edita la sección `BACKENDS_CONFIG` en `run.py`

Busca esta sección (alrededor de la línea 24):

```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
    "sms": ("sms/logica/sms_backend.py", "/api/sms"),
}
```

### Paso 2: Comentar Módulo (para ahorrar memoria)

Para **desactivar** un módulo, agrega `#` al inicio de la línea:

```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    # "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),  # ← DESACTIVADO
    # "sms": ("sms/logica/sms_backend.py", "/api/sms"),  # ← DESACTIVADO
}
```

**Resultado:** Solo se cargarán Login y Traslados, ahorrando ~30-50MB de memoria.

### Paso 3: Descomentar Módulo

Para **reactivar**, simplemente quita el `#`:

```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),  # ← REACTIVADO
    "sms": ("sms/logica/sms_backend.py", "/api/sms"),
}
```

---

## ➕ Cómo Agregar un Nuevo Módulo

### Requisitos del Backend

El archivo backend debe:
1. Importar Flask: `from flask import Flask`
2. Crear instancia: `app = Flask(__name__)`
3. Usar CORS si es necesario: `from flask_cors import CORS`
4. **NO ejecutar** `app.run()` (el DispatcherMiddleware se encarga)

### Ejemplo: Agregar `admin_desayunos_calientes`

1. **Localiza el archivo backend:**
   ```
   Formadig/1_Sistema_DIF_Acatlan/modulos/admin_desayunos_calientes/logica/admin_desayunos_calientes_backend.py
   ```

2. **Agrega una línea en `BACKENDS_CONFIG`:**
   ```python
   BACKENDS_CONFIG = {
       "login": ("login/logica/login_backend.py", "/api/auth"),
       "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
       "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
       "desayunos_calientes": ("admin_desayunos_calientes/logica/admin_desayunos_calientes_backend.py", "/api/desayunos_calientes"),  # ← NUEVO
       "sms": ("sms/logica/sms_backend.py", "/api/sms"),
   }
   ```

3. **Prueba:**
   ```bash
   python run.py
   ```

   Deberías ver:
   ```
   [→] Cargando: desayunos_calientes
       [OK] ✅ Backend cargado exitosamente
   ```

---

## 🧠 Optimización de Memoria

### Escenario 1: Rendimiento Máximo (Solo Login)
```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
}
```
**Memoria:** ~80-100MB

### Escenario 2: Desarrollo Rápido (Login + Traslados)
```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
}
```
**Memoria:** ~120-150MB

### Escenario 3: Producción Completa (Todos)
```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
    "sms": ("sms/logica/sms_backend.py", "/api/sms"),
}
```
**Memoria:** ~250-300MB

---

## ✅ Verificación

### Local (Desarrollo)
```bash
python run.py
```

Debería ver:
```
[SUMMARY] Backends cargados: 4/4
  Módulos activos:
    ✅ login
    ✅ traslados
    ✅ desayunos_frios
    ✅ sms
```

### Con Gunicorn (Producción)
```bash
gunicorn --workers 4 --timeout 120 run:app
```

### Probar Rutas
```bash
# Login
curl http://localhost:10000/api/auth

# Traslados
curl http://localhost:10000/api/traslados

# Desayunos
curl http://localhost:10000/api/desayunos_frios

# SMS
curl http://localhost:10000/api/sms
```

---

## 🚨 Troubleshooting

### Error: `[ERROR] ❌ Archivo no existe`

**Causa:** La ruta en `BACKENDS_CONFIG` es incorrecta o el archivo no existe.

**Solución:**
```bash
# Verifica la ruta exacta
ls -la "Formadig/1_Sistema_DIF_Acatlan/modulos/admin_traslados/logica/admin_traslados_backend.py"
```

### Error: `[ERROR] ❌ No se encontró objeto 'app'`

**Causa:** El archivo backend no tiene `app = Flask(__name__)`

**Solución:**
```python
# En el backend, debe tener:
from flask import Flask
app = Flask(__name__)  # ← OBLIGATORIO
```

### El servidor usa mucho RAM

**Causa:** Todos los módulos están cargados

**Solución:** Comenta los módulos que no necesites en `BACKENDS_CONFIG`

---

## 📚 Estructura de `run.py`

### 1. `BACKENDS_CONFIG` (tu control)
Define qué módulos cargar y en qué ruta

### 2. `cargar_backend()` (automático)
Importa el módulo usando `importlib` y retorna el objeto `app`

### 3. `DispatcherMiddleware` (automático)
Monta todos los `app` cargados en sus rutas

### 4. WSGI `app` (para Gunicorn/producción)
Está liston para usar con servidores WSGI

---

## 🔍 Cómo Funciona Internamente

```python
# run.py hace exactamente esto:

1. frontend_app = create_flask_app()  # App para archivos estáticos

2. for each backend in BACKENDS_CONFIG:
    backend_app = cargar_backend(nombre, ruta)  # Usa importlib
    dispatcher_dict[ruta] = backend_app

3. app = DispatcherMiddleware(frontend_app, dispatcher_dict)
   # Resultado:
   # - /            → frontend_app (HTML/CSS/JS)
   # - /api/auth    → backend_app (login)
   # - /api/traslados → backend_app (traslados)
   # - ... etc
```

**NO usa subprocess.Popen**, todop está en el mismo proceso Python.

---

## 📞 Preguntas Frecuentes

**P: ¿Puedo cambiar las rutas de los backends?**
A: Sí, la segunda columna en `BACKENDS_CONFIG` es la ruta del Dispatcher.

**P: ¿Qué pasa si un backend no carga?**
A: El sistema reporta el error, pero continúa cargando los demás. No crashea.

**P: ¿Necesito reiniciar para cambiar módulos?**
A: Sí, debes comentar/descomentar y reiniciar el servidor.

**P: ¿Por qué no usa `subprocess.Popen`?**
A: Porque importlib es más eficiente en memoria y CPU, y evita procesos zombie.

---

**Última actualización:** 11/04/2026
**Estado:** ✅ PRODUCCIÓN
