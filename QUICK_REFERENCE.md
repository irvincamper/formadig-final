# 🚀 Quick Reference: run.py

## ⚡ Cambios Rápidos

### Deshabilitar SMS (para ahorrar RAM)
En `run.py` línea ~30:
```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
    # "sms": ("sms/logica/sms_backend.py", "/api/sms"),  # ← COMENTADO
}
```
Reinicia: `python run.py`

---

### Solo Login + Traslados (Máximo ahorro)
```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    # "desayunos_frios": (...),
    # "sms": (...),
}
```

---

### Agregar Desayunos Calientes
```python
BACKENDS_CONFIG = {
    "login": ("login/logica/login_backend.py", "/api/auth"),
    "traslados": ("admin_traslados/logica/admin_traslados_backend.py", "/api/traslados"),
    "desayunos_frios": ("admin_desayunos_frios/logica/admin_desayunos_frios_backend.py", "/api/desayunos_frios"),
    "desayunos_calientes": ("admin_desayunos_calientes/logica/admin_desayunos_calientes_backend.py", "/api/desayunos_calientes"),  # ← NUEVO
    "sms": ("sms/logica/sms_backend.py", "/api/sms"),
}
```

---

## 📡 Rutas de API

| Ruta | Backend | Estado |
|------|---------|--------|
| `/api/auth` | Login | ✅ |
| `/api/traslados` | Traslados | ✅ |
| `/api/desayunos_frios` | Desayunos Fríos | ✅ |
| `/api/sms` | SMS | ✅ |
| `/api/desayunos_calientes` | Desayunos Calientes | ⏸️ Comentado |

---

## 🔧 Flujo de Carga

```
run.py
├── 1. Frontend app (estáticos)
├── 2. Cargar backends con importlib (paralelo)
│   ├── login → /api/auth
│   ├── traslados → /api/traslados
│   ├── desayunos_frios → /api/desayunos_frios
│   └── sms → /api/sms
└── 3. Montar todo en DispatcherMiddleware
    └── app (WSGI lista)
```

---

## 💾 Archivo: `BACKENDS_CONFIG`

**Ubicación:** `run.py` línea ~24

**Sintaxis:**
```python
"nombre_modulo": ("ruta/relativa/backend.py", "/api/ruta"),
```

**Formato:**
- Clave: nombre único (usado para logging)
- Valor:
  - Posición 0: ruta relativa desde `modulos/`
  - Posición 1: ruta del Dispatcher (dónde montará la app)

---

## ✅ Validación

### Ver todos los backends cargados
```bash
python run.py | grep "Módulos activos" -A 5
```

### Probar un endpoint
```bash
curl -s http://localhost:10000/api/auth | python -m json.tool
```

---

## 🎓 Referencia de Archivos

| Archivo | Propósito |
|---------|-----------|
| `run.py` | Punto de entrada + Dispatcher |
| `RUN_CONFIGURATION.md` | Guía completa |
| `QUICK_REFERENCE.md` | Este archivo |

---

**Última actualización:** 11/04/2026
