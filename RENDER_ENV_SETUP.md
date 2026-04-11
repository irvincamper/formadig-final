# 🔧 CONFIGURAR VARIABLES DE ENTORNO EN RENDER

## ⚠️ EL PROBLEMA

Tu app falló porque las claves de Supabase están hardcodeadas en el código:

```python
SUPABASE_URL = "https://ctiqbycbkcftwuqgzxjb.supabase.co"
SUPABASE_KEY = "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk"
```

**Render NO tiene acceso a estas claves**, así que la autenticación falla con error 500.

## ✅ LA SOLUCIÓN

### Paso 1: En Render Dashboard

1. Ve a tu servicio en **Render** → **Dashboard**
2. Haz clic en tu app FORMADIG
3. Ve a la sección **Environment** (Entorno)
4. Haz clic en **Add Environment Variable**

### Paso 2: Añade estas 2 variables

```
SUPABASE_URL = https://ctiqbycbkcftwuqgzxjb.supabase.co
SUPABASE_KEY = sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk
```

### Paso 3: Deploy

Después de añadir las variables, Render deployará automáticamente tu app con la nueva configuración.

## 📋 Checklist Render

- [ ] Variable `SUPABASE_URL` configurada
- [ ] Variable `SUPABASE_KEY` configurada
- [ ] El servicio mostró "Deploy Successful"
- [ ] La URL está accesible sin errores 5xx

## 🔍 Verificación

Para confirmar que funciona:

```bash
# Desde tu terminal local:
curl https://tu-app.render.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

Debería retornar un JSON con el resultado de la autenticación (incluso si fallan las credenciales), NO un error 500.

## 🚨 IMPORTANTE: Nunca Hardcodees Secretos

**Nunca** hagas `git push` con claves en el código. Siempre usa variables de entorno:

✅ Correcto:
```python
KEY = os.getenv("MY_KEY", "default_value")
```

❌ Incorrecto:
```python
KEY = "my-secret-key-1234"  # ¡Público en GitHub!
```

## 📝 Archivos Modificados

- `login_backend.py` - Ahora lee `SUPABASE_URL` y `SUPABASE_KEY` desde variables de entorno
- `.env.example` - Referencia de las variables que necesitas configurar
