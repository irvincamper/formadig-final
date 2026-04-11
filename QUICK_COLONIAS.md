# ⚡ QUICK START - Sistema de Colonias

**¿Qué?** Autocompleción de colonias en 3 módulos  
**¿Dónde?** Desayunos Calientes, Desayunos Fríos, Traslados  
**¿Cuándo usar?** Cuando usuario ingresa CP de 5 dígitos  
**¿Qué hace?** Backend busca colonias → Dropdown se llena  

---

## 🚀 EMPEZAR EN 2 MINUTOS

### Opción A: Test Rápido
```bash
python test_backend_colonias_solo.py
```
✅ Verifica que backend/Supabase funciona  
❌ Identifica qué está fallando

### Opción B: Test en Vivo
```bash
# Terminal 1
python Formadig/1_Sistema_DIF_Acatlan/modulos/colonias/logica/colonias_backend.py

# Terminal 2
cd Formadig && python run.py

# Navegador
http://localhost:8000/.../admin_desayunos_calientes.html
```

Luego: Abre F12 → Console → Ingresa CP 28018 → Observa logs

---

## 📊 ESTADO

| Componente | Estado |
|-----------|--------|
| Backend API | ✅ Listo |
| HTML (3 módulos) | ✅ Listo |
| JavaScript (3 módulos) | ✅ Listo |
| Logging | ✅ Agregado |
| **Data Binding** | 🟡 **Debuggeando** |

**Problema:** Dropdown UI existe pero está VACÍO → datos no llegan

---

## 🔍 DEBUGGING PASO A PASO

### Paso 1: ¿Backend devuelve datos?
```bash
curl http://localhost:5010/api/colonias/28018
```
- Si ves `[{...}, {...}]` → ✅ Backend OK
- Si ves `[]` → ❌ No hay datos en Supabase
- Si ves error 404 → ❌ Backend no corre

### Paso 2: ¿Frontend recibe datos?
```javascript
// En console (F12)
fetch("http://localhost:5010/api/colonias/28018")
  .then(r => r.json())
  .then(d => console.log("Datos:", d))
```

### Paso 3: ¿Event listener dispara?
```javascript
// En console
document.getElementById("cp").addEventListener("input", () => {
  console.log("✅ CP cambió");
});
// Luego cambia el valor en input
```

### Paso 4: ¿Select element existe?
```javascript
console.log(document.getElementById("colonia")); // No debe ser null
```

---

## 📖 DOCUMENTACIÓN

| Archivo | Qué es | Cuándo leer |
|---------|--------|-----------|
| `LOGS_ESPERADOS.md` | Qué ver en terminal/console | Antes de empezar |
| `GUIA_COLONIAS_DEBUG.md` | Cómo debuggear | Estás viendo problema |
| `TROUBLESHOOTING_COLONIAS.md` | Soluciones específicas | Algo no funciona |
| `README_COLONIAS_SISTEMA.md` | Documento maestro | Necesitas contexto |

---

## ⚠️ PROBLEMAS COMUNES

### Dropdown Vacío
```
✅ UI aparece
❌ Sin opciones
→ Probablemente RLS en Supabase bloqueando lectura
→ O: No hay datos para ese CP en BD
```

### Error 404
```
❌ "Error HTTP 404"
→ Backend no está corriendo en puerto 5010
→ Solución: python colonias_backend.py
```

### Logs No Aparecen
```
❌ Ingresas CP, no ves logs
→ Event listener no dispara
→ JavaScript error
→ Revisa: console.error, debugger
```

### CORS Error
```
❌ "Access-Control-Allow-Origin"
→ Backend necesita CORS
→ Verificar: CORS(app) en colonias_backend.py
```

---

## 🧪 VALIDACIÓN RÁPIDA

✅ **Pasó todos estos?** → Sistema funciona

- [ ] Backend levanta: `🏘️ Backend Colonias iniciado en puerto 5010`
- [ ] Endpoint responde: `curl localhost:5010/api/colonias/28018` devuelve JSON
- [ ] Frontend carga: Abre http://localhost:8000/.../admin_desayunos_calientes.html
- [ ] Logs aparecen: En console F12 ves "🔍 Iniciando búsqueda"
- [ ] Datos llegan: Console muestra "✅ Respuesta del backend"
- [ ] Dropdown se llena: Puedes seleccionar colonias

---

## 🔧 COMANDO MAESTRO PARA DEBUGGEAR

**Ejecuta esto primero:**
```bash
python test_backend_colonias_solo.py
```

Este script:
1. ✅ Verifica conexión Supabase
2. ✅ Confirma tabla existe
3. ✅ Prueba query por CP
4. ✅ Simula respuesta backend
5. ✅ Sugiere soluciones si falla

**Si TODO ✅** → Problema está en Frontend JavaScript  
**Si algo ❌** → Revisar error específico arriba

---

## 📱 URLs Útiles

| Descripción | URL |
|-------------|-----|
| Módulo Desayunos Calientes | http://localhost:8000/modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html |
| Módulo Desayunos Fríos | http://localhost:8000/modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html |
| Módulo Traslados | http://localhost:8000/modulos/admin_traslados/vistas/admin_traslados.html |
| API Backend Colonias | http://localhost:5010/api/colonias/28018 |
| API Backend (todas) | http://localhost:5010/api/colonias/ |

---

## 🎯 OBJETIVO

```
Usuario ingresa CP → Sistema busca → Dropdown se llena → Usuario selecciona colonia → Se guarda
✅
```

### Estado Actual
```
Usuario ingresa CP ✅
    ↓
Sistema busca ✅
    ↓
Dropdown aparece ✅
    ↓
Dropdown se llena ❌ ← AQUÍ ESTAMOS
    ↓
Usuario selecciona
    ↓
Se guarda
```

---

## 📞 PRÓXIMO PASO

**AHORA:**
```bash
# Abre terminal en raíz de proyecto
python test_backend_colonias_solo.py
# Lee resultados

# Si ✅ todos → Backend OK, debuggea frontend
# Si ❌ alguno → Revisar TROUBLESHOOTING_COLONIAS.md
```

---

**Documentación:** `/memories/repo/colonias_system_status.md`  
**Última actualización:** Abril 11, 2026  
**Tiempo estimado para completar:** 1-2 horas
