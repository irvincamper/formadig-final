# 📊 LOGS ESPERADOS - Sistema de Colonias

Este archivo muestra exactamente QUÉ deberías ver en terminal y console cuando el sistema funciona correctamente.

---

## 🖥️ TERMINAL (Donde levantaste el servidor)

### Al Iniciar `python Formadig/run.py`

```
========================================
Iniciando servidores...
========================================

✅ Servidor web principal en puerto 8000
   http://localhost:8000

🏘️ Backend Colonias iniciado en puerto 5010
   Rutas registradas:
   📍 GET /api/colonias/<cp>  - Buscar colonias por CP
   📍 GET /api/colonias/       - Mostrar todas las colonias

🍽️  Backend Desayunos Calientes corriendo en puerto 5001
   Rutas disponibles:
   📌 GET  /api/desayunos_calientes
   📌 POST /api/desayunos_calientes
   📌 PUT  /api/desayunos_calientes/<id>

❄️  Backend Desayunos Fríos corriendo en puerto 5002
   Rutas disponibles:
   📌 GET  /api/desayunos_frios
   📌 POST /api/desayunos_frios

🚗 Backend Traslados corriendo en puerto 5004
   Rutas disponibles:
   📌 GET  /api/traslados
   📌 POST /api/traslados

========================================
Todos los servidores iniciados correctamente ✅
========================================
```

### Cuando Ingresas CP en Módulo

**Terminal mostrará:**
```
🔍 Consultando colonias para CP: 28018

✅ Se encontraron 2 colonia(s) para CP 28018
   Colonias: ['Centro', 'Reforma']

📤 Enviando respuesta al cliente...
```

### Errores Comunes en Terminal

```
❌ RLS bloqueando lectura:
   Supabase error: {'message': 'row level security violation', ...}
   → Solución: Agregar SELECT policy en tabla colonias_acatlan

❌ Tabla no existe:
   Supabase error: 'relation "colonias_acatlan" does not exist'
   → Solución: Crear tabla en Supabase

❌ Conexión rechazada:
   ConnectionRefusedError: [Errno 111] Connection refused
   → Solución: Verificar SUPABASE_URL y SUPABASE_KEY son correctas
```

---

## 🔍 BROWSER CONSOLE (F12 → Console tab)

### Cuando se carga módulo Desayunos Calientes

```
Module loaded: admin_desayunos_calientes
Inicializando event listeners...
✅ Event listener agregado a campo CP
✅ Event listener agregado a campo Colonia (select)
```

### Cuando Ingresas CP (Ej: 28018)

**Deberías ver estos logs EN ORDEN:**

```
1️⃣  🔍 Iniciando búsqueda de colonias para CP: 28018
    └─ Se dispara cuando ingresas CP y presionas Tab/Enter

2️⃣  📡 Petición GET a: http://localhost:5010/api/colonias/28018
    └─ Muestra URL exacta siendo consultada

3️⃣  📊 Estado de respuesta: 200 OK
    └─ HTTP status - 200 = éxito, 404 = servidor no responde, 500 = error

4️⃣  ✅ Respuesta del backend para colonias: Array(2)
    ├─ {id: 1, nombre: "Centro", codigo_postal: "28018"}
    └─ {id: 2, nombre: "Reforma", codigo_postal: "28018"}
    └─ El array tiene 2 elementos

5️⃣  📋 Colonias extraídas (cantidad: 2): Array(2)
    └─ Confirmación que se extrajo correctamente

6️⃣  ✅ Agregando 2 opciones al selector
    └─ Iniciando loop para crear <option> elements

7️⃣  [1] Centro
    └─ Primera colonia siendo agregada

8️⃣  [2] Reforma
    └─ Segunda colonia siendo agregada

9️⃣  ✅ Todas las opciones agregadas exitosamente
    └─ Fin del proceso
```

### Resultado Visual Esperado

**Antes (sin ingresar CP):**
```
Colonia/Barrio: [-- Selecciona una colonia --]
```

**Después (ingresa 28018):**
```
Colonia/Barrio: [▼ Centro    ◄─ Opción 1
                  Reforma     ◄─ Opción 2
                  Seleccionar...]
```

---

## 🟢 Logs por Módulo

### Desayunos Calientes
```
console.log("🔍 Iniciando búsqueda de colonias para CP: " + codigoPostal);
console.log("📡 Petición GET a: /api/colonias/" + codigoPostal);
console.log("✅ Respuesta del backend para colonias:", data);
console.log("📋 Colonias extraídas (cantidad: " + colonias.length + "):", colonias);
```

### Desayunos Fríos
```
Logs IDÉNTICOS a Calientes
```

### Traslados
```
Logs IDÉNTICOS a Calientes + Campos especiales:

// Cuando se carga un traslado existente:
console.log("🚗 Cargando traslado ID:", id);
console.log("CP detectado:", formData.cp);

// Cuando se guarda:
console.log("📍 Colonia seleccionada:", document.getElementById("colonia").value);
```

---

## 🔴 Logs de Error que INDICAN PROBLEMAS

### Error 1: "Colonias recibidas: []"
```
❌ Colonias recibidas: Array(0) []       ← Array vacío
⚠️  No hay colonias registradas para CP: 28018
```

**Significa:**
- Backend respondió (status 200)
- Pero Supabase devolvió array vacío
- Causas: No hay datos, RLS bloqueando, CP no existe

**Fix:**
```
1. Verifica que CP existe: SELECT * FROM colonias_acatlan WHERE codigo_postal = '28018';
2. Verifica RLS policy en Supabase
3. Intenta CP diferente
```

---

### Error 2: "TypeError: Cannot read property 'nombre' of undefined"
```
❌ TypeError: Cannot read property 'nombre' of undefined
   at admin_desayunos_calientes.js:85:15
   at Array.forEach (<anonymous>)
```

**Significa:**
- Array tiene datos pero formato es incorrecto
- Backend devolvió algo que no es `{id, nombre, codigo_postal}`

**Fix:**
```javascript
// En console para diagnosticar:
fetch("http://localhost:5010/api/colonias/28018")
  .then(r => r.json())
  .then(d => {
    console.log("Estructura actual:", JSON.stringify(d[0], null, 2));
    console.log("¿Tiene 'nombre'?", d[0].nombre !== undefined);
  });
```

---

### Error 3: "404 Not Found"
```
❌ Error HTTP 404 al obtener colonias
   Respuesta: 404 Not Found
```

**Significa:**
- Backend colonias_backend.py NO está corriendo
- O ruta `/api/colonias/<cp>` no existe
- O puerto 5010 no está accesible

**Fix:**
```bash
# En terminal nueva, verifica:
python Formadig/1_Sistema_DIF_Acatlan/modulos/colonias/logica/colonias_backend.py

# Debería mostrar:
# 🏘️ Backend Colonias iniciado en puerto 5010
```

---

### Error 4: "CORS error"
```
Access to XMLHttpRequest at 'http://localhost:5010/api/colonias/28018' 
from origin 'http://localhost:8000' blocked by CORS policy
```

**Significa:**
- Backend existe pero CORS no configurado
- No puede enviar respuesta a frontend en diferente puerto

**Fix:**
```python
# En colonias_backend.py, línea 10 aprox:
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ← Agregar esta línea

# Luego reiniciar backend
```

---

### Error 5: "Select de colonia no encontrado en el DOM"
```
❌ Select de colonia no encontrado en el DOM
```

**Significa:**
- HTML no tiene `<select id="colonia">`
- JavaScript está buscando elemento que no existe

**Fix:**
```bash
# Verificar que HTML tiene el select:
grep 'id="colonia"' dif_acatlan_web_app/src/modules/admin_desayunos_calientes.html

# Si no devuelve nada, actualizar HTML:
# Buscar <input type="text"...description...> donde iba colonia
# Y cambiar por <select id="colonia">
```

---

## 📈 Logs de Éxito Completo

### Escenario: Todo funciona perfectamente

```
=== TERMINAL ===
🏘️ Backend Colonias iniciado en puerto 5010

=== NAVEGADOR ===
1. Abres módulo Desayunos Calientes
   Console: ✅ Event listener agregado a campo CP

2. Ingresas 28018 en campo CP
   Console: 🔍 Iniciando búsqueda de colonias para CP: 28018
   Console: 📡 Petición GET a: /api/colonias/28018
   Console: 📊 Estado de respuesta: 200 OK
   Console: ✅ Respuesta del backend para colonias: Array(2)
   Console: 📋 Colonias extraídas (cantidad: 2): Array(2)
   Console: ✅ Agregando 2 opciones al selector
   Console: [1] Centro
   Console: [2] Reforma
   Console: ✅ Todas las opciones agregadas exitosamente

3. Dropdown de colonia NOW muestra:
   [▼ -- Selecciona una colonia --
      Centro
      Reforma]

4. Haces click y seleccionas "Centro"
   Campo se llena con: Centro ✅

5. Guardas el registro
   Backend recibe: {cp: "28018", colonia: "Centro", ...}
   Registro guardado en Supabase ✅

=== TERMINAL ===
📤 Se guardó desayuno caliente con éxito
   ID generado: a1b2c3d4-e5f6
   Colonia: Centro
   CP: 28018
```

---

## 🧪 Test Rápido - Aquí van los Logs Esperados

### Test 1: Verificar Backend está corriendo
```
$ curl http://localhost:5010/api/colonias/28018

Respuesta esperada:
[
  {"id": 1, "nombre": "Centro", "codigo_postal": "28018"},
  {"id": 2, "nombre": "Reforma", "codigo_postal": "28018"}
]
```

### Test 2: Verificar CORS
```
$ curl -i -X OPTIONS http://localhost:5010/api/colonias/28018

Headers esperados:
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### Test 3: Verificar Supabase
```
En Supabase Dashboard:
SELECT * FROM colonias_acatlan WHERE codigo_postal = '28018' LIMIT 10;

Esperado:
ID  | nombre  | codigo_postal | creado_en
1   | Centro  | 28018         | 2024-04-11...
2   | Reforma | 28018         | 2024-04-11...
```

---

## ✅ Checklist de Verificación

- [ ] Terminal muestra: "🏘️ Backend Colonias iniciado en puerto 5010"
- [ ] Navegador a http://localhost:5010/api/colonias/28018 devuelve JSON array
- [ ] Console (F12) muestra log: "🔍 Iniciando búsqueda de colonias"
- [ ] Console muestra: "✅ Respuesta del backend para colonias: Array(N)"
- [ ] Dropdown se llena con colonias después de ingresar CP
- [ ] Puedes seleccionar una colonia sin error
- [ ] El formulario se envía con colonia seleccionada
- [ ] Supabase registra la colonia en la tabla correspondiente

---

**Última actualización:** Abril 11, 2026
