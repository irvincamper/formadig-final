# 🔧 TROUBLESHOOTING - Sistema de Colonias por Módulo

## Estado Actual (Antes de Depuración)

### ✅ Lo que FUNCIONA:
- ✅ Backend colonias_backend.py creado y registrado (puerto 5010)
- ✅ HTML dropdown selectores creados en todos los módulos
- ✅ Event listeners funcionan en campos CP
- ✅ Logging extensivo agregado (console.log + print())

### ❌ Lo que NO funciona:
- ❌ Dropdown de colonias aparece **VACÍO** después de ingresar CP
- ❌ No se sabe si error es en backend o frontend

---

## 📱 Desayunos Calientes

### Archivos modificados:
- 📝 `dif_acatlan_web_app/src/modules/admin_desayunos_calientes.html`
- 📝 `dif_acatlan_web_app/src/modules/admin_desayunos_calientes.js`

### ✅ Verificación rápida:

```javascript
// Abrir Console (F12) y pegar esto:
console.log("📍 Test Desayunos Calientes");
console.log("Select element:", document.getElementById("colonia"));
console.log("CP element:", document.getElementById("cp"));
```

Debería devolver dos elementos del DOM, no `null`.

### 🐛 Si dropdown está vacío:

#### Paso 1: Verificar que evento dispara
```javascript
// En console (F12):
document.getElementById("cp").addEventListener("input", function() {
    console.log("✅ CP input detectado:", this.value);
});

// Luego ingresa un CP - deberías ver el log
```

#### Paso 2: Verificar fetch funciona
```javascript
// En console (F12):
fetch("http://localhost:5010/api/colonias/28018")
    .then(r => r.json())
    .then(d => console.log("Respuesta backend:", d))
    .catch(e => console.error("Error:", e));
```

Si ves `[]` - **No hay datos en Supabase**  
Si ves error - **Backend no responde**  
Si ves array con objetos - **Backend OK, problema en función**

#### Paso 3: Fix manual en console
```javascript
// Limpiar y repoblar select
const selectColonia = document.getElementById("colonia");
selectColonia.innerHTML = '<option>-- Selecciona una colonia --</option>';

// Llamar cargarColonias manualmente
cargarColonias(); // Si está definida en scope global

// O si está dentro del módulo:
window.cargarColonias = cargarColonias; // En el archivo JS, agregar esto
```

### 🔍 Dónde está el código:

**HTML - Select element:**
```html
<!-- Línea aprox. 280 -->
<input type="text" id="cp" placeholder="Ej: 28018" required>
<select id="colonia" required>
    <option value="">-- Selecciona una colonia --</option>
</select>
```

**JavaScript - Evento listener:**
```javascript
// En admin_desayunos_calientes.js, línea aprox. 50
document.getElementById("cp").addEventListener("change", cargarColonias);
document.getElementById("cp").addEventListener("blur", cargarColonias);
```

**JavaScript - Función cargarColonias:**
```javascript
// Línea aprox. 70
async function cargarColonias() {
    const codigoPostal = document.getElementById("cp").value.trim();
    
    if (codigoPostal.length !== 5) {
        console.log("❌ CP debe tener 5 dígitos");
        return;
    }
    
    // ... rest de función
}
```

---

## 🥶 Desayunos Fríos

### Archivos modificados:
- 📝 `dif_acatlan_web_app/src/modules/admin_desayunos_frios.html`
- 📝 `dif_acatlan_web_app/src/modules/admin_desayunos_frios.js`

### Diferencias vs Calientes:
**NINGUNA** - Implementación es idéntica

### ✅ Verificación:

```javascript
// En console (F12):
console.log("📍 Test Desayunos Fríos");
console.log("Select:", document.getElementById("colonia"));

// Prueba el mismo fix que en Calientes
fetch("http://localhost:5010/api/colonias/28018")
    .then(r => r.json())
    .then(d => console.log("Fríos - Backend:", d));
```

### 🐛 Si falla:

Mismos pasos que Desayunos Calientes, ya que código es idéntico.

---

## 🚗 Traslados

### Archivos modificados:
- 📝 `dif_acatlan_web_app/src/modules/admin_traslados.html`
- 📝 `dif_acatlan_web_app/src/modules/admin_traslados.js`

### ⚠️ CAMBIOS ESPECIALES en Traslados:

El módulo Traslados usaba `codigo_postal` en lugar de `cp`, así que se corrigió:

**HTML (antes):**
```html
<input type="text" id="codigo_postal" placeholder="...">
```

**HTML (después):**
```html
<input type="text" id="cp" placeholder="Ej: 28018">
<select id="colonia" required>
    <option>-- Selecciona una colonia --</option>
</select>
```

**JavaScript (antes):**
```javascript
setVal('codigo_postal', response.codigo_postal);
```

**JavaScript (después):**
```javascript
setVal('cp', formData.cp);
colonia: document.getElementById("colonia").value,
```

### ✅ Verificación específica para Traslados:

```javascript
// En console (F12):
console.log("📍 Test Traslados");
console.log("CP field:", document.getElementById("cp")); // ← Debe existir
console.log("Colonia select:", document.getElementById("colonia")); // ← Debe existir

// Verifica que no hay elemento viejo
console.log("¿Aún existe codigo_postal?:", document.getElementById("codigo_postal"));
// ↑ Debe ser null
```

### 🐛 Si falla en Traslados:

#### Causa 1: HTML no se actualizó correctamente
```html
<!-- MALO -->
<input id="codigo_postal"> <!-- ← ID viejo
<!-- BUENO -->
<input id="cp">              <!-- ← ID correcto
```

**Fix:** Buscar `codigo_postal` en HTML y cambiar a `cp`

#### Causa 2: JavaScript aún referencia campo viejo
```javascript
// MALO
document.getElementById("codigo_postal").addEventListener(...)

// BUENO
document.getElementById("cp").addEventListener(...)
```

**Fix:** Buscar `codigo_postal` en JS y cambiar a `cp`

#### Causa 3: setVal() no encuentra el campo
```javascript
// Si ves error: "Cannot read property 'value' of null"

// Verificar que existe en HTML:
document.getElementById("cp") // No debe ser null

// O si setVal() es una función personalizada:
function setVal(fieldId, value) {
    const elem = document.getElementById(fieldId);
    if (!elem) {
        console.error(`❌ Campo ${fieldId} no existe en HTML`);
        return;
    }
    elem.value = value;
}
```

---

## 🚨 Problemas Generales (Todos los módulos)

### Problema: "Cannot read property 'value' of null"

**En la consola ves:**
```
admin_desayunos_calientes.js:75 Uncaught TypeError: 
Cannot read property 'value' of null
```

**Causa:** Elemento HTML no tiene el ID correcto

**Solución:**

1. **Verifica el HTML:**
```bash
# Buscar el archivo HTML
grep -n "id=\"cp\"" dif_acatlan_web_app/src/modules/admin_desayunos_calientes.html
# Deería devolver una línea con <input id="cp"...>

grep -n "id=\"colonia\"" dif_acatlan_web_app/src/modules/admin_desayunos_calientes.html
# Debería devolver una línea con <select id="colonia"...>
```

2. **Si no devuelve nada:**
   - HTML no tiene los IDs correctos
   - Necesitas actualizar manualmente el HTML

3. **Si devuelve algo:**
   - Los IDs están ahí
   - Problema es en JavaScript (cargar Script en orden incorrecto, variable global no definida, etc.)

---

### Problema: "cargarColonias is not defined"

**En la consola ves:**
```
ReferenceError: cargarColonias is not defined
```

**Causa:** Función no está siendo importada o cargada

**Solución:**

```javascript
// En admin_desayunos_calientes.js, verifica que existe:
async function cargarColonias() {
    // ... código de función
}

// Y que esté ANTES de ser referenciada:
document.getElementById("cp").addEventListener("change", cargarColonias);
// ↑ cargarColonias debe haberse definido ANTES de esta línea

// O hazla global:
window.cargarColonias = async function() {
    // ... código
};
```

---

### Problema: CORS error

**En la consola ves:**
```
Access to XMLHttpRequest at 'http://localhost:5010/api/colonias/28018' 
from origin 'http://localhost:8000' blocked by CORS policy
```

**Causa:** Backend no tiene CORS habilitado para puerto 8000

**Solución:** Verificar que en `colonias_backend.py` está:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ← Debe estar aquí
```

Si no está, agregarlo después de crear la app.

---

## 🧪 Checklist de Depuración

Ejecuta esto en orden:

- [ ] **Terminal:** Verifica colonias_backend.py está corriendo en puerto 5010
  ```bash
  # Deberías ver: 🏘️ Backend Colonias iniciado en puerto 5010
  ```

- [ ] **Navegador:** Abre http://localhost:5010/api/colonias/28018
  ```
  Deberías ver JSON array, no error ni página en blanco
  ```

- [ ] **Console (F12):** Verifica elementos del DOM
  ```javascript
  document.getElementById("cp")      // No debe ser null
  document.getElementById("colonia")  // No debe ser null
  ```

- [ ] **Console (F12):** Prueba fetch manual
  ```javascript
  fetch("http://localhost:5010/api/colonias/28018")
    .then(r => r.json())
    .then(d => console.log(d));
  ```

- [ ] **Module:** Ingresa CP de 5 dígitos
  ```
  Mira console para logs: "🔍 CP ingresado:", "📡 Respuesta:", "Colonias recibidas:"
  ```

- [ ] **Select:** ¿Cambió el dropdown? ¿Hay opciones?
  ```javascript
  document.getElementById("colonia").options // Debe tener length > 1
  ```

---

## 📞 Si Nada Funciona

1. **Comparte estos datos:**
   - Salida completa de terminal donde levanta colonias_backend.py
   - Resultado de http://localhost:5010/api/colonias/28018
   - Screenshot de console (F12) cuando ingresas CP
   - Error exacto que ves (si hay)

2. **Intenta desactivar RLS:**
   - Supabase Dashboard → colonias_acatlan → Auth/RLS
   - Verifica que haya política SELECT para rol `anon`

3. **Prueba con otro CP:**
   - Usa un CP que sabes que existe en BD
   - O crea test data con `test_colonias_system.py`

---

**Última actualización:** Abril 11, 2026  
**Responsable:** Sistema de Colonias v2.0
