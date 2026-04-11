# 🧪 GUÍA DE TESTING - ESTANDARIZACIÓN UI/UX

**Objetivo:** Verificar que todos los cambios funcionan correctamente

---

## 🚀 SETUP PARA TESTING

### Paso 1: Acceder al Sistema
```
URL Local: http://localhost:5000 (o tu puerto)
URL Producción: https://tuistemadif.com
```

### Paso 2: Login
- Email: (cuenta admin)
- Password: (credenciales admin)

### Paso 3: Navegar a módulos administrativos

---

## ✅ TEMA 1: CAMPOS DE UBICACIÓN

### Test 1.1: Traslados - Ubicación Completa
```
📍 Pasos:
1. Ir a: Dashboard → Traslados
2. En tabla, buscar un registro con datos
3. Hacer clic en la fila
4. Ir a Tab "📍 Ubicación"

✅ Verificar que existan estos campos (EN ESTE ORDEN):
   ☐ Localidad (NUEVO - debe estar arriba)
   ☐ Colonia / Barrio (debe estar al lado)
   ☐ Tipo de Asentamiento (NUEVO - debe estar abajo)
   ☐ C.P. (debe estar al lado)
   ☐ Domicilio Completo (debe estar abajo)
   ☐ Referencias de Ubicación (textarea al final)

✅ Verificar que se llenan con datos del registro:
   ☐ localidad tiene valor
   ☐ colonia tiene valor
   ☐ tipo_asentamiento tiene valor
   ☐ codigo_postal tiene valor
   ☐ referencias tiene valor

Expected: 6 campos visibles, todos con datos ✅
If fail: Verificar admin_traslados.html tiene los ID correctos
```

### Test 1.2: Desayunos Fríos - Ubicación Completa
```
📍 Pasos:
1. Ir a: Dashboard → Desayunos Fríos
2. En tabla, buscar un registro
3. Hacer clic en la fila
4. Ir a Tab "📍 Ubicación"

✅ Verificar 6 campos: localidad, colonia, tipo_asentamiento, codigo_postal, referencias
✅ Todos deben estar pre-llenados

Expected: Idéntico a Traslados ✅
```

### Test 1.3: Desayunos Calientes - Ubicación Completa
```
📍 Pasos: (Idéntico a Desayunos Fríos)

Expected: Idéntico a Desayunos Fríos ✅
```

### Test 1.4: Espacios EAEYD - Ubicación Completa
```
📍 Pasos: (Idéntico a Desayunos)

Expected: Idéntico a Desayunos ✅
```

---

## ✅ TEMA 2: DOCUMENTOS INTELIGENTES

### Test 2.1: Documento CON URL (debe ser VERDE)
```
📄 Pasos:
1. En cualquier módulo, ir a Tab "🗂️ Docs" o "📄 Documentos"
2. Buscar un registro que TENGA URL_CURP (o similar)
3. Observar el botón de documento

✅ Verificar que muestre:
   ☐ Botón VERDE con gradiente (#10b981 → #059669)
   ☐ Texto "📄 VER CURP" (o documento corresponda)
   ☐ Botón es CLICKABLE (cursor: pointer)
   ☐ Al pasar mouse: sube un poco (translateY(-2px))
   ☐ Muestra sombra: box-shadow: 0 4px 12px rgba(16,185,129,0.5)
   ☐ Click abre en nueva tab (target="_blank")

Expected: Botón verde, clickable, abre documento ✅
If fail: Verificar renderDocumentoBtn() en utilities-standard.js
```

### Test 2.2: Documento SIN URL (debe ser GRIS)
```
📄 Pasos:
1. En mismo módulo, buscar registro que NO TENGA URL_CURP
2. Observar el botón de documento

✅ Verificar que muestre:
   ☐ Botón GRIS (#e2e8f0)
   ☐ Texto "⚠️ No disponible"
   ☐ Botón NO es CLICKABLE (cursor: not-allowed implícito)
   ☐ Al pasar mouse: NO hace nada
   ☐ NO abre nada si "clickeas"

Expected: Botón gris, no funciona, dice "No disponible" ✅
If fail: Verificar que URL es realmente vacío/null/undefined
```

### Test 2.3: Múltiples Documentos (alguns con URL, otros sin)
```
📄 Pasos:
1. Ir a Tab de documentos
2. Observar 3-5 botones de diferentes documentos

✅ Verificar patrón:
   ☐ Al menos uno VERDE (tiene URL)
   ☐ Al menos uno GRIS (no tiene URL)
   ☐ La ratio de verde/gris depende del registro

Expected: Mezcla de verde y gris según disponibilidad ✅
If fail: Revisar datos del registro en base de datos
```

---

## ✅ TEMA 3: HOVER EFFECTS EN TABLAS

### Test 3.1: Pasar mouse en tabla
```
🖱️ Pasos:
1. Ir a cualquier módulo (Traslados, Desayunos, etc)
2. Observar tabla con registros
3. Pasar mouse sobre diferentes filas

✅ Verificar que al pasar mouse:
   ☐ Fondo cambia a #f9fafb (gris MUY CLARO)
   ☐ Transición es suave (0.2s ease)
   ☐ Aparece sombra interna: inset 0 0 0 1px #e2e8f0
   ☐ Al quitar mouse, vuelve a normal

Expected: Hover effect suave y elegante ✅
If fail: Verificar CSS dashboard.css tiene .table tbody tr:hover
```

### Test 3.2: Click en fila (seleccionar)
```
🖱️ Pasos:
1. En tabla, hacer clic en una fila
2. Observar cambio visual

✅ Verificar que la fila seleccionada:
   ☐ Fondo cambia a #e0f2fe (azul MUY CLARO)
   ☐ Barra AZUL aparece a la izquierda (4px sólido #0284c7)
   ☐ Queda "resaltada"
   ☐ Panel derecho se llena con los datos

Expected: Fila azul con barra lateral ✅
If fail: Verificar .selected-row-v3 class en tra.js
```

---

## ✅ TEMA 4: FORM CONTROLS - FOCUS STATE

### Test 4.1: Click en input
```
⌨️ Pasos:
1. En panel derecho, hacer clic en un input
2. Observar cambios visuales

✅ Verificar:
   ☐ Borde cambia a VERDE (#00766c)
   ☐ Fondo cambia a #fafbfc (azulado muy claro)
   ☐ Aparece "aura" alrededor: 0 0 0 3px rgba(0,118,108,0.1)
   ☐ Transición es suave (0.2s)

Expected: Input con borde verde y aura ✅
If fail: Verificar CSS .form-control:focus en dashboard.css
```

### Test 4.2: Hover en input (sin click)
```
⌨️ Pasos:
1. Pasar mouse sobre input SIN hacer click
2. Observar cambio

✅ Verificar:
   ☐ Borde cambia a #cbd5e1 (más oscuro)
   ☐ Fondo cambia a #f8fafc
   ☐ NO aparece aura (eso es solo para focus)

Expected: Input con borde gris oscuro ✅
If fail: Verificar CSS .form-control:hover:not(:focus)
```

### Test 4.3: Spacing en panel
```
⌨️ Pasos:
1. Observar panel lateral con formulario
2. Medir distancia entre inputs

✅ Verificar:
   ☐ Cada grupo tiene margin-bottom: 1.5rem
   ☐ Hay espacio "respirable" entre campos
   ☐ NO están "pegados"
   ☐ Labels están encima del input con margin-bottom: 0.5rem

Expected: Panel con buen espaciado ✅
If fail: Verificar CSS .form-group y .form-label
```

---

## ✅ TEMA 5: UTILITIES COMPARTIDAS

### Test 5.1: Función formatearFecha()
```
📅 Pasos:
1. Abrir consola del navegador (F12)
2. Ejecutar: AppUtilities.formatearFecha('2024-01-15')

✅ Verificar:
   ☐ Devuelve: "15/01/2024" (DD/MM/YYYY)
   ☐ Si es null/undefined: devuelve "S/F"
   ☐ Si es inválido: devuelve "Inválida"

Expected: Formato DD/MM/YYYY correcto ✅
If fail: Verificar utilities-standard.js formatearFecha()
```

### Test 5.2: Función safeSet()
```
⚙️ Pasos:
1. Abrir consola (F12)
2. Ejecutar: AppUtilities.safeSet('localidad', 'Acatlán')
3. Verificar que el input cambió

✅ Verificar:
   ☐ Input con id='localidad' recibe el valor 'Acatlán'
   ☐ No hay error en consola
   ☐ Si el elemento NO existe, tampoco hay error

Expected: Valor asignado sin errores ✅
If fail: Verificar utilities-standard.js safeSet()
```

### Test 5.3: Función llenarUbicacion()
```
📍 Pasos:
1. Abrir consola (F12)
2. Ejecutar:
   ```javascript
   const record = {
       localidad: 'Acatlán',
       colonia: 'Centro',
       tipo_asentamiento: 'Pueblo',
       codigo_postal: '54000',
       referencias: 'Frente iglesia'
   };
   AppUtilities.llenarUbicacion(record);
   ```

✅ Verificar:
   ☐ Todos los inputs de ubicación se llenan
   ☐ No hay errores en consola

Expected: Panel se llena automáticamente ✅
If fail: Verificar utilities-standard.js llenarUbicacion()
```

---

## ✅ TEMA 6: CSS IMPROVEMENTS

### Test 6.1: Status Badges
```
🏷️ Pasos:
1. En tabla, observar columna "Estado" o "Status"
2. Notar los diferentes estados: ACEPTADO, PENDIENTE, RECHAZADO, etc

✅ Verificar colores:
   ☐ ACEPTADO = verde (#d1fae5 fondo, #065f46 texto)
   ☐ PENDIENTE = amarillo (#fef08a fondo, #78350f texto)
   ☐ EN PROCESO = azul (#bfdbfe fondo, #1e3a8a texto)
   ☐ RECHAZADO = rojo (#fecaca fondo, #991b1b texto)
   ☐ Cada una tiene sombra sutil: box-shadow

Expected: Badges multicolores con buena legibilidad ✅
If fail: Verificar CSS .status-badge en dashboard.css
```

### Test 6.2: Panel Sticky
```
📌 Pasos:
1. En módulo admin, observar panel derecho
2. Scrollear la página hacia abajo

✅ Verificar:
   ☐ Panel se "pega" en la pantalla (no se va)
   ☐ Permanece visible mientras scrolleas
   ☐ El scrollbar interno del panel funciona si es muy largo
   ☐ Max-height se respeta

Expected: Panel "sticky" que acompaña scroll ✅
If fail: Verificar CSS .sticky-panel position: sticky
```

---

## 🔍 TEMA 7: VERIFICACIÓN TRANSVERSAL

### Test 7.1: Consistencia entre módulos
```
🔄 Pasos:
1. Abrir Traslados
2. Verificar: ubicación, documentos, hover, inputs
3. Ir a Desayunos Fríos
4. Verificar: MISMO comportamiento
5. Ir a Desayunos Calientes
6. Verificar: MISMO comportamiento
7. Ir a Espacios EAEYD
8. Verificar: MISMO comportamiento

✅ Todos deben ser IDÉNTICOS:
   ☐ Campos de ubicación (6 campos)
   ☐ Documentos inteligentes (verde/gris)
   ☐ Hover effects en tabla
   ☐ Focus state en inputs
   ☐ Spacing y padding
   ☐ Colores y estilos

Expected: Experiencia idéntica en todos ✅
If fail: Identificar cuál módulo es diferente y verificar importaciones
```

---

## 🐛 TROUBLESHOOTING GUIDE

| Problema | Causa Probable | Solución |
|----------|-----------------|----------|
| No aparecen campos de ubicación | HTML no tiene IDs correctos | Verificar admin_traslados.html línea 330+ |
| Documentos no cambian color | CSS no carga | Verificar dashboard.css está importado |
| Utilities no encontradas | Script no importado | Verificar `<script src="utilities-standard.js">` antes del módulo JS |
| Hover effects no funcionan | CSS outdated | Limpiar caché (Ctrl+Shift+Del) o hard refresh (Ctrl+F5) |
| Inputs no crecen con focus | CSS conflict | Verificar no hay override de estilos más específicos |
| Tabla no tiene borde azul | selected-row-v3 no aplicada | Verificar módulo JS que agregue la class |
| Documentos siempre gris | URL sin procesar | Verificar record tiene url_curp, url_ine, etc. |

---

## ✨ CHECKLIST FINAL

Marcar cuando se verifica cada test:

```
⚪ Test 1.1: Traslados - Ubicación Completa
⚪ Test 1.2: Desayunos Fríos - Ubicación Completa
⚪ Test 1.3: Desayunos Calientes - Ubicación Completa
⚪ Test 1.4: Espacios EAEYD - Ubicación Completa

⚪ Test 2.1: Documento CON URL (verde)
⚪ Test 2.2: Documento SIN URL (gris)
⚪ Test 2.3: Múltiples Documentos (mezcla)

⚪ Test 3.1: Pasar mouse en tabla
⚪ Test 3.2: Click en fila (seleccionar)

⚪ Test 4.1: Click en input (focus)
⚪ Test 4.2: Hover en input
⚪ Test 4.3: Spacing en panel

⚪ Test 5.1: formatearFecha()
⚪ Test 5.2: safeSet()
⚪ Test 5.3: llenarUbicacion()

⚪ Test 6.1: Status Badges
⚪ Test 6.2: Panel Sticky

⚪ Test 7.1: Consistencia entre módulos

Total: 18 tests
```

Si TODOS están ✅, el sistema está 100% listo.

---

## 📞 REPORTE DE ISSUES

Si encuentras algo que NO funciona:

1. **Documenta el problema:**
   - Qué módulo
   - Qué test fallaron
   - Qué esperabas ver
   - Qué viste realmente

2. **Proporciona contexto:**
   - Información del navegador (Chrome, Firefox, etc.)
   - Versión del navegador
   - URL exacta

3. **Envía reporte:**
   - Incluye screenshot si es posible
   - Errores de consola (F12 → Console)

---

**STATUS:** 🟢 ESTÁ LISTO PARA TESTING

Sigue los pasos y reporta cualquier issue encontrada.
