# Commit: Alineación de Schema Supabase y Limpieza de Credenciales

## 📋 Resumen de Cambios

Este commit implementa:
1. **Eliminación de credenciales hardcodeadas** → Uso exclusivo de variables de entorno (`os.getenv()`)
2. **Adición de `.limit()`** a todas las queries Supabase → Prevención de timeouts en producción
3. **Limpieza de fallbacks innecesarios** en mapeos de datos
4. **Simplificación de queries** a tabla principal sin alternativas


---

## 🔐 SEGURIDAD: Variables de Entorno Requeridas en Render

Antes de hacer deploy a Render, configura estas variables en el dashboard:

```
SUPABASE_URL=https://ctiqbycbkcftwuqgzxjb.supabase.co
SUPABASE_KEY=sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk
GEMINI_API_KEY=AIzaSyD1FhiP8ZdGIpwPdHz3NMFHFWASea1xGUo
```

**¡CRÍTICO!** Sin estas variables, los backends retornarán errores 500.

---

## 📝 Archivos Modificados

### Backend: Credenciales & Queries

1. **Formadig/1_Sistema_DIF_Acatlan/modulos/admin_traslados/logica/admin_traslados_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback
   - ✅ Query: `.limit(1000)` agregado
   - ✅ Mapeo: Campos exactos del schema (sin aliases innecesarios)

2. **Formadig/1_Sistema_DIF_Acatlan/modulos/admin_desayunos_frios/logica/admin_desayunos_frios_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback
   - ✅ Query: `.limit(1000)` agregado
   - ✅ Simplificado: Query único a tabla `desayunos_frios` (removido fallback a `desayunos_fríos`, `desayunos_eaeyd`)

3. **Formadig/1_Sistema_DIF_Acatlan/modulos/admin_desayunos_calientes/logica/admin_desayunos_calientes_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback
   - ✅ Query: `.limit(1000)` agregado

4. **Formadig/1_Sistema_DIF_Acatlan/modulos/admin_espacios_eaeyd/logica/admin_espacios_eaeyd_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback
   - ✅ Query: `.limit(1000)` agregado

5. **Formadig/1_Sistema_DIF_Acatlan/modulos/sms/logica/sms_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback

6. **Formadig/1_Sistema_DIF_Acatlan/modulos/chatbot/logica/chatbot_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback
   - ✅ Queries: `.limit(1000)` agregado a `hospitales` y `chatbot_conocimiento`

7. **Formadig/1_Sistema_DIF_Acatlan/modulos/login/logica/login_backend.py**
   - ✅ Credenciales: `os.getenv()` sin fallback


---

## 🔄 Cambios Técnicos Detallados

### Patrón Anterior (INSEGURO):
```python
SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"
```

### Patrón Nuevo (SEGURO):
```python
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
```

### Queries Antes:
```python
res = supabase.table('traslados').select('*').order('fecha_solicitud', desc=True).execute()
# ❌ No tiene límite → Riesgo de timeout en producción
```

### Queries Después:
```python
res = supabase.table('traslados').select('*').order('fecha_solicitud', desc=True).limit(1000).execute()
# ✅ Con límite → Soporte para producción con volumen
```

### Mapeo Antes (Fallbacks Complejos):
```python
"fecha_viaje": r.get('fecha_viaje'),
"fecha_cita": fecha_display,  # Fallback a r.get('fecha')
"hora_salida": hora_display,  # Fallback a r.get('hora')
"destino": r.get('destino_hospital'),  # Alias
```

### Mapeo Después (Exacto):
```python
"fecha_viaje": r.get('fecha_viaje'),
"hora_cita": r.get('hora_cita'),
"destino_hospital": r.get('destino_hospital'),
# ✅ Uso exacto de nombres del schema
```

---

## ✅ Testing Pre-Deploy

Antes de hacer push:

```bash
# 1. Verificar que NO hay credenciales en los archivos
grep -r "sb_publishable_" Formadig/1_Sistema_DIF_Acatlan/modulos/ --include="*.py"
# Debe devolver 0 resultados

# 2. Verificar que todos los backends tienen os.getenv()
grep -r "os.getenv.*SUPABASE" Formadig/1_Sistema_DIF_Acatlan/modulos/ --include="*.py"
# Debe devolver 7 coincidencias (uno por backend)

# 3. Verificar que todas las queries principales tienen .limit()
grep -r "\.limit(" Formadig/1_Sistema_DIF_Acatlan/modulos/ --include="*.py"
# Debe devolver al menos 10 coincidencias
```

---

## 🚀 Deploy a Render

1. **Hacer commit**: `git add -A && git commit -m "fix: alinear schema Supabase y eliminar credenciales hardcodeadas"`

2. **Configurar Render Dashboard**:
   - Ir a: Settings → Environment Variables
   - Agregar las 3 variables listadas arriba
   - Save & Deploy

3. **Verificar en Producción**:
   - GET http://localhost:PORT/api/traslados → Debe retornar JSON con `traslados: [...]`
   - GET http://localhost:PORT/api/desayunos_frios → Debe retornar JSON con `desayunos: [...]`
   - Si retorna 500 → Falta variable de entorno

---

## 🎯 Impacto Esperado

| Aspecto | Antes | Después |
|---------|-------|---------|
| Seguridad | Credenciales en código ❌ | Variables de entorno ✅ |
| Vulnerabilidad | Risk Alto | Risk Eliminado |
| Performance | Queries ilimitadas ⚠️ | Queries limitadas a 1000 ✅ |
| Timeouts | Posibles en prod ⚠️ | Prevenidos ✅ |
| Fallbacks | Múltiples (confuso) | Ninguno (exacto) |

---

## 📌 Notas Importantes

1. **Desarrollo Local**: Los backends usarán valores de `os.getenv()` que retornarán `None` si no están configurados. Para desarrollo local, crea un archivo `.env` en la raíz:
   ```
   SUPABASE_URL=https://ctiqbycbkcftwuqgzxjb.supabase.co
   SUPABASE_KEY=sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk
   GEMINI_API_KEY=AIzaSyD1FhiP8ZdGIpwPdHz3NMFHFWASea1xGUo
   ```
   
   Luego carga con: `python -m dotenv run python run.py`

2. **Endpoints Verificados**: Todos los 7 backends tienen tipos correctos de retorno (JSON)

3. **Schema Exacto**: Las queries usan campos exactos del schema sin fallbacks adicionales

4. **Próximos Pasos**: 
   - [ ] Configurar `.env.example` para desarrollo
   - [ ] Documentar credenciales en README
   - [ ] Hacer deploy a Render con variables configuradas

---

## 🔗 Referencias

- Render Dashboard: https://dashboard.render.com
- Supabase Project: https://app.supabase.com/project/ctiqbycbkcftwuqgzxjb
- Documentación Render Env Vars: https://render.com/docs/configure-environment-variables
