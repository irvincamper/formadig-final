# 🔀 ÁRBOL DE DECISIÓN - Debugging Sistema de Colonias

**¿Algo no funciona? Sigue este árbol para encontrar la solución.**

---

## 🌳 ÁRBOL PRINCIPAL

```
┌─────────────────────────────────────────────────────┐
│  ¿El dropdown de colonia está VACÍO?                │
│  (UI visible pero sin opciones)                     │
└────────────────────┬────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          NO                   SÍ
          │                     │
          ▼                     ▼
    [ÉXITO ✅]        ┌────────────────────┐
                      │ Ejecuta:            │
                      │ test_backend_solo   │
                      │ .py                 │
                      └────────┬────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
        ✅ TODOS OK      ⚠️ Array vacío   ❌ Error Supabase
              │                │                │
              │                │                │
              ▼                ▼                ▼
        [Frontend        [Ver Sección] [Ver Sección]
         Problem]        "Array vacío" "Supabase"]
```

---

## 📋 SECCIÓN 1: Frontend Problem (cuando Backend OK)

```
Síntoma: Backend devuelve datos ✅ pero dropdown sigue vacío ❌

Diagnóstico:
┌──────────────────────────────────────────┐
│ ¿Qué ves en console (F12)?               │
└────────────┬─────────────┬───────────────┘
             │             │
    [Logs sí]│      [No ves logs]
             │             │
             ▼             ▼
        ┌─────────┐  ┌────────────────┐
        │Log #4   │  │Event listener  │
        │muestra  │  │no dispara      │
        │datos ✅ │  │                │
        └─────────┘  └────────────────┘
             │             │
             ▼             ▼
      Problema en   Revisar:
      JS rendering  - querySelector
      (forEach loop)  - CP no 5 dígitos
      
      SOLUCIÓN:      SOLUCIÓN:
      Verificar:     1. F12 Console:
      - colonias       document.getElementById("cp")
        es array       # No debe ser null
      - Elementos    2. Probar evento manual:
        creados OK      cp.addEventListener(
      - Select         "change",
        reference     () => console.log("cambió")
        es válido     )
```

---

## 📋 SECCIÓN 2: Array Vacío (Backend devuelve [])

```
Síntoma: Console muestra "Colonias recibidas: [] (0 elementos)"

Causas posibles (en orden):
┌────────────────────────────────────────────────────────┐
│ 1️⃣  Row Level Security (RLS) bloqueando              │
│ 2️⃣  No hay datos en tabla para ese CP                │
│ 3️⃣  CP con formato incorrecto en BD                  │
└────┬───────────────┬──────────────┬──────────────────┘
     │               │              │
     ▼               ▼              ▼
  [RLS]        [Sin datos]    [Formato]
     │               │              │
     ▼               ▼              ▼
Supabase      SELECT *        CP debe
Dashboard →   FROM colonias   ser VARCHAR
Auth → Policies acatlan WHERE  o TEXT,
       poder adicionar      codigo_postal='28018' no INT
       SELECT policy        LIMIT 10;
       para 'anon'          (verificar en BD)
       
SOLUCIÓN:          SOLUCIÓN:        SOLUCIÓN:
Crear policy       Insertar test    Revisar
para públic        data:            schema
SELECT            INSERT INTO      de tabla
on tabla           colonias_acatlan
colonias_acatlan   (codigo_postal,
                    nombre)
                   VALUES
                   ('28018', 'Centro')
```

---

## 📋 SECCIÓN 3: Supabase Problem

```
Síntoma: test_backend_colonias_solo.py reporta error

┌─────────────────────────────────────────┐
│ ¿Cuál es el error específico?            │
└────┬────────────────┬────────────────────┘
     │                │
     ▼                ▼
[Can't        [Database
 connect]      error]
     │                │
     ▼                ▼
SUPABASE_URL    Tabla no existe
SUPABASE_KEY    o sin permiso
falta en .env
     
SOLUCIÓN:           SOLUCIÓN:
1. Crear .env      1. Ir a Supabase Dashboard
   en raíz        2. SQL Editor
2. Agregar:       3. Crear tabla:
   SUPABASE_URL
   =https://...      CREATE TABLE colonias_acatlan (
   SUPABASE_KEY        id INT PRIMARY KEY,
   =eyJ...             codigo_postal VARCHAR(5),
3. Reintentar        nombre VARCHAR(100),
   test              creado_en TIMESTAMP DEFAULT NOW()
                    );
                  
                  4. O verificar si existe:
                     SELECT * FROM colonias_acatlan;
```

---

## 🔄 PROTOCOLO: "NO VEO NADA EN CONSOLE"

```
Ingresas CP pero NO ves logs en console (F12)

PASO 1: ¿Abre DevTools correctamente?
   [SÍ] → Paso 2
   [NO] → F12 o Right-click → Inspect → Console tab

PASO 2: ¿Ingresaste CP de 5 dígitos?
   [SÍ] 28018 → Paso 3
   [NO] → Probar con CP que exista en Supabase

PASO 3: ¿Presionaste Enter/Tab después de ingresado CP?
   [SÍ] → Paso 4
   [NO] → Event listener escucha "change" y "blur"

PASO 4: ¿Error en JavaScript?
   console → Busca línea roja ❌
   [HAY ERROR] → Revisar TROUBLESHOOTING → "TypeError"
   [SIN ERROR] → cargarColonias no se ejecutó
                 → Event listener no registrado
                 → Revisar Paso 1-3

SOLUCIÓN NUCLEAR:
En console (F12), pegar:
cargarColonias()  // Llamar función manualmente
document.getElementById("cp").value = "28018"
cargarColonias()  // Llamar de nuevo

Si funciona → Event listener no registrado
Si no funciona → Problema en función cargarColonias()
```

---

## 🧪 PROTOCOLO: "ERROR 404"

```
Console: "Error HTTP 404 al obtener colonias"

┌────────────────────────┐
│ Backend levanta?       │
│ python colonias...py   │
└────┬───────────────────┘
     │
     ├─[SÍ] → ¿Ve "🏘️ Backend Colonias iniciado"?
     │         │
     │         ├─[SÍ] → ¿Abierto puerto 5010?
     │         │        → curl localhost:5010/api/colonias/28018
     │         │        → Debe devolver JSON, no 404
     │         │
     │         └─[NO] → Error en backend startup
     │                 → Ver terminal para error
     │
     └─[NO] → Backend NO está corriendo
              → Solución: python colonias_backend.py
              → O: python Formadig/run.py (levanta todo)
```

---

## 🔐 PROTOCOLO: "CORS ERROR"

```
Console: "Access to XMLHttpRequest...blocked by CORS policy"

┌──────────────────────────────┐
│ ¿Backend tiene CORS(app)?     │
│ Ver colonias_backend.py       │
└────┬─────────────────────────┘
     │
     ├─[SÍ] → Está en línea 15 aprox:
     │        from flask_cors import CORS
     │        CORS(app)
     │        │
     │        └─ Si está → Reinicia backend
     │           Si no está → Agregar estas líneas
     │
     └─[NO] → Solución:
             1. Abrir colonias_backend.py
             2. Después de "app = Flask(__name__)"
             3. Agregar:
                from flask_cors import CORS
                CORS(app)
             4. Guardar y reiniciar backend
```

---

## 📱 CHECKLIST RÁPIDO

Cuando algo no funciona, marca estos en ORDEN:

- [ ] **Terminal 1:** ¿Backend colonias levantó?
  ```
  python Formadig/1_Sistema_DIF_Acatlan/modulos/colonias/logica/colonias_backend.py
  Debe mostrar: 🏘️ Backend Colonias iniciado en puerto 5010
  ```

- [ ] **Navegador:** API endpoint devuelve datos?
  ```
  http://localhost:5010/api/colonias/28018
  Debe mostrar: JSON array, NO error
  ```

- [ ] **DevTools:** Elementos DOM existen?
  ```javascript
  document.getElementById("cp")      // No null
  document.getElementById("colonia")  // No null
  ```

- [ ] **DevTools:** Event listener dispara?
  ```javascript
  document.getElementById("cp").dispatchEvent(
    new Event('change')
  )
  // Deberías ver logs en console
  ```

- [ ] **Console:** ¿Ves logs en orden?
  ```
  1. 🔍 Iniciando búsqueda...
  2. 📡 Petición GET...
  3. 📊 Estado de respuesta...
  4. ✅ Respuesta del backend...
  ```

- [ ] **Dropdown:** ¿Se llena con opciones?
  ```html
  <select id="colonia">
    <option>-- Selecciona una colonia --</option>
    <option>Centro</option>        ← ¿Aparecen estos?
    <option>Reforma</option>
  </select>
  ```

---

## 🎯 DECISIÓN FINAL

Después de todo el debugging:

```
┌─────────────────────────────┐
│ ¿Dropdown se llena? ✅      │
└────┬────────────────────────┘
     │
     ├─[SÍ] → 🎉 ÉXITO
     │        Sistema funcionando
     │        Pasar a validación en BD
     │
     └─[NO] → Seguir documentación
              TROUBLESHOOTING_COLONIAS.md
              con error específico
```

---

## 📞 TABLA RÁPIDA DE SÍNTOMAS

| Síntoma | Línea en este árbol |
|---------|-------------------|
| Dropdown vacío | SECCIÓN 1-2 |
| No ves logs | PROTOCOLO "NO VEO NADA" |
| Error 404 | PROTOCOLO "ERROR 404" |
| CORS error | PROTOCOLO "CORS" |
| TypeError | TROUBLESHOOTING JS section |
| Array vacío | SECCIÓN 2 |
| RLS error | SECCIÓN 3 → Database error |

---

## 🔗 REFERENCIAS

- **Logs esperados:** LOGS_ESPERADOS.md
- **Debugging completo:** GUIA_COLONIAS_DEBUG.md
- **Soluciones:** TROUBLESHOOTING_COLONIAS.md
- **Test rápido:** python test_backend_colonias_solo.py

---

**Para printear:** Imprimir este archivo y marcar camino que seguiste  
**Para consultar:** Guardar link a este archivo en favoritos  
**Última actualización:** Abril 11, 2026
