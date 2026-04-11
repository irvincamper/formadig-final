# 🐛 GUÍA DE DEPURACIÓN - Sistema de Colonias

## 📋 Cambios Realizados

### Backend (`colonias_backend.py`)
**Cambio:** Formato de respuesta simplificado
```python
# ANTES:
{
  "colonias": [...],
  "total": 10,
  "codigo_postal": "28018"
}

# DESPUÉS:
[
  {"id": 1, "nombre": "Centro", "codigo_postal": "28018"},
  {"id": 2, "nombre": "Reforma", "codigo_postal": "28018"}
]
```

**Ventaja:** Array directo = más fácil de iterar en frontend

**Logging Agregado:**
```
🔍 Buscando colonias para CP: 28018
✅ Se encontraron 2 colonia(s) para CP 28018
   Colonias: ['Centro', 'Reforma']
```

---

### Frontend (Todos los módulos)
**Cambios en `cargarColonias()` function:**

#### 1. Validación mejorada
```javascript
if (!selectColonia) {
    console.error('❌ Select de colonia no encontrado en el DOM');
    return;
}
```

#### 2. Logging detallado de red
```javascript
console.log(`📡 Petición GET a: /api/colonias/${codigoPostal}`);
console.log(`📊 Estado de respuesta: ${response.status} ${response.statusText}`);
```

#### 3. Extracción flexible de datos
```javascript
// Soporta tanto array directo como objeto con propiedad "colonias"
const colonias = Array.isArray(data) ? data : (data.colonias || []);
console.log("✅ Respuesta del backend:", data);
console.log(`📋 Colonias extraídas (${colonias.length}):`, colonias);
```

#### 4. Iteración con logging
```javascript
colonias.forEach((col, idx) => {
    const nombreColonia = col.nombre || col.name || 'Unnamed';
    console.log(`   [${idx + 1}] ${nombreColonia}`);  // ← VER ESTO EN CONSOLA
    // ... crear option ...
});
```

---

## 🔍 CÓMO DEPURAR

### Paso 1: Abrir Browser DevTools
```
F12 → Console
```

### Paso 2: Ir a módulo Desayunos o Traslados
```
http://localhost:8000/modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html
```

### Paso 3: Ingresa un Código Postal válido en el campo "C.P."
Ejemplo: `28018`

### Paso 4: Presiona Tab o Enter para disparar `onChange`

### Paso 5: Mira la consola - Deberías ver logs como:

```
🔍 Iniciando búsqueda de colonias para CP: 28018
📡 Petición GET a: /api/colonias/28018
📊 Estado de respuesta: 200 OK
✅ Respuesta del backend para colonias: (2) [{…}, {…}]
📋 Colonias extraídas (cantidad: 2): (2) [{…}, {…}]
✅ Agregando 2 opciones al selector
   [1] Centro
   [2] Reforma
✅ Todas las opciones agregadas exitosamente
```

---

## ⚠️ POSIBLES PROBLEMAS Y SOLUCIONES

### Problema 1: ERROR 404 en la petición
**En consola ves:**
```
❌ Error HTTP 404 al obtener colonias
```

**Causas posibles:**
- [ ] Backend `colonias_backend.py` no está ejecutándose
- [ ] Puerto 5010 no está disponible/escuchando

**Solución:**
```bash
# Verificar que el backend está corriendo
# En terminal: python Formadig/1_Sistema_DIF_Acatlan/modulos/colonias/logica/colonias_backend.py

# Deberías ver:
# 🏘️ Backend Colonias iniciado en puerto 5010
# 📍 Rutas registradas:
#    /api/colonias/<cp> [GET]
#    /api/colonias/ [GET]
```

---

### Problema 2: Array vacío []
**En consola ves:**
```
✅ Respuesta del backend para colonias: []
📋 Colonias extraídas (cantidad: 0): []
⚠️ No hay colonias registradas para CP 28018
```

**Causas posibles:**
- [ ] No hay datos en tabla `colonias_acatlan` para ese CP
- [ ] Row Level Security (RLS) está bloqueando lectura en Supabase
- [ ] El CP no tiene formato correcto en BD

**Soluciones:**

#### A. Verificar que existen datos en Supabase
```sql
-- En Supabase Dashboard → SQL Editor, ejecuta:
SELECT * FROM colonias_acatlan WHERE codigo_postal LIKE '%28%' LIMIT 10;
```

Si no hay resultados, inserta algunos datos de prueba:
```sql
INSERT INTO colonias_acatlan (codigo_postal, nombre) VALUES
('28018', 'Centro'),
('28018', 'Reforma'),
('28020', 'Santa María');
```

#### B. Verificar RLS en Supabase
```
Supabase Dashboard → Authentication → Policies
Tabla: colonias_acatlan
Busca: SELECT policy
```

Si no hay policy SELECT para rol `anon` o `authenticated`:
```sql
-- Crear policy de lectura para todos
CREATE POLICY "Allow public read" ON colonias_acatlan
  FOR SELECT
  USING (true);
```

---

### Problema 3: Error de CORS
**En consola ves:**
```
❌ Error de red/CORS cargando colonias:
   Access to XMLHttpRequest at 'http://localhost:5010/api/colonias/28018' 
   from origin 'http://localhost:8000' blocked by CORS policy
```

**Solución:**
Backend ya tiene CORS habilitado, pero verifica que esté en servidor_control.py:
```python
# En servidor_control.py, línea 50 aprox:
ports = [5001, 5003, 5004, 5005, 5006, 5007, 5008, 5009, 5010, 8000]
#                                                          ↑ ¿Está 5010?
```

---

### Problema 4: TypeError: col.nombre is undefined
**En consola ves:**
```
TypeError: colonias.forEach is not a function
// O
TypeError: Cannot read property 'nombre' of undefined
```

**Causa:**
Backend no está devolviendo array, sino un objeto

**Solución:**
Verifica que configuraste correctamente el backend. El código corregido ahora devuelve array directo:
```python
return jsonify(colonias), 200
```

---

## ✅ TEST RÁPIDO (Manual al inicio)

### 1. Verifica que backend levantó correctamente
```
Debería estar en puerto 5010
Si ves en terminal:
🏘️ Backend Colonias iniciado en puerto 5010
   /api/colonias/<cp> [GET]
   /api/colonias/ [GET]
→ ✅ BIEN
```

### 2. Prueba la API directamente en navegador
```
Visita: http://localhost:5010/api/colonias/28018
```

Deberías ver un JSON como:
```json
[
  {"id": 1, "nombre": "Centro", "codigo_postal": "28018"},
  {"id": 2, "nombre": "Reforma", "codigo_postal": "28018"}
]
```

Si ves `[]` (empty array): **No hay datos en Supabase**  
Si ves error 404: **Backend no está corriendo**  
Si ves error 500: **Error en backend (ver terminal)**

### 3. Prueba en módulo Desayunos
- Abre console (F12)
- Ingresa CP
- Deberías ver los logs detallados
- Si vienes los logs pero no las opciones: **Problema en DOM**

---

## 📞 PRÓXIMOS PASOS SI SIGUE SIN FUNCIONAR

1. **Comparte screenshots de:**
   - Terminal donde levanta colonias_backend.py
   - Console de DevTools (F12) cuando ingresas CP
   - Response en http://localhost:5010/api/colonias/28018

2. **Verifica:** ¿Los otros backends funcionan? (Traslados, Desayunos)

3. **Si es RLS:**
   - Crea manualmente una policy de lectura
   - O usa key de servicio (con cuidado en producción)

---

## 📊 Resumen de URLs

| Función | URL | Puerto | Método |
|---------|-----|--------|--------|
| Obtener colonias por CP | `/api/colonias/28018` | 5010 | GET |
| Debug - Todas las colonias | `/api/colonias/` | 5010 | GET |

---

**Última actualización:** Abril 11, 2026
