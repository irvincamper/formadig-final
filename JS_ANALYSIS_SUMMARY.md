# JavaScript Module Analysis - DIF Acatlán System

## Overview
Analysis of three admin module JavaScript files to identify current implementation patterns and standardization opportunities.

---

## 1. MAIN LOADING FUNCTIONS COMPARISON

| Module | Loading Function | Data Endpoint | Async | Auto-Select First |
|--------|------------------|----------------|-------|-------------------|
| **Admin Desayunos Fríos** | `cargarDatos()` | `/api/desayunos_frios` | Yes | Yes ✓ |
| **Admin Traslados** | `cargarTraslados()` | `/api/traslados` | Yes | Yes ✓ |
| **Admin Espacios EAEyD** | `cargarDatos()` | `/api/espacios_eaeyd` | Yes | Yes ✓ |

**Status**: Mostly consistent; traslados uses different naming (`cargarTraslados` vs generic `cargarDatos`).

---

## 2. PANEL FILLING LOGIC (DATA BINDING)

All three modules use the same pattern:

```javascript
const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val || "";
};
```

**Fields populated on row selection:**

#### Desayunos Fríos & EAEyD (nearly identical)
- **Identity**: nombre_beneficiario, curp, apellidos, fecha_nacimiento, sexo, estado_civil
- **Health**: peso_menor, estatura_menor
- **Socioeconomic**: nivel_estudios, ingreso_mensual, situacion_vulnerabilidad
- **Location**: localidad, colonia, tipo_asentamiento, cp, referencias
- **Guardian**: tutor, clave_elector_tutor, telefono
- **Assignment**: escuela (Desayunos) / escuela (EAEyD)
- **Status**: estatus

#### Traslados (different structure)
- **Identity**: paciente_curp
- **Patient**: paciente_nombre, paciente_edad
- **Location**: paciente_domicilio, colonia, codigo_postal, referencias
- **Transfer**: destino_hospital, acompanante_nombre, acompanante_clave_elector
- **Contact**: telefono_principal, telefono_secundario
- **Status**: estatus

**⚠️ Issue**: Different field names (`paciente_domicilio` vs `localidad`; `codigo_postal` vs `cp`)

---

## 3. LOCATION FIELD HANDLING

| Field | Desayunos Fríos | Traslados | EAEyD |
|-------|-----------------|-----------|-------|
| **localidad** | ✓ Yes | ✗ NO (uses `paciente_domicilio`) | ✓ Yes |
| **colonia** | ✓ Yes | ✓ Yes | ✓ Yes |
| **tipo_asentamiento** | ✓ Yes | ✗ NO | ✓ Yes |
| **cp/codigo_postal** | ✓ `cp` | ✓ `codigo_postal` | ✓ `cp` |
| **referencias** | ✓ Yes | ✓ Yes | ✓ Yes |

**Summary**: 
- ✓ All location fields are being handled and populated
- ⚠️ Field naming is **INCONSISTENT** across modules (traslados uses different structure)
- **Recommendation**: Standardize to: `localidad`, `colonia`, `tipo_asentamiento`, `cp`, `referencias`

---

## 4. DOCUMENT BUTTON RENDERING

All modules use a shared `renderDocBtn()` pattern:

```javascript
function renderDocBtn(containerId, url, label) {
    const cont = document.getElementById(containerId);
    if (!cont) return;
    if (url && url.trim()) {
        cont.innerHTML = `<a href="${url}" target="_blank"...>📄 VER ${label}</a>`;
    } else {
        cont.innerHTML = '<span style="...">⚠️ No disponible</span>';
    }
}
```

### Document Buttons Rendered

#### Desayunos Fríos
- `btnDocCurpCont` → CURP
- `btnDocCompDomCont` → DOMICILIO
- `btnDocFotoInfanteCont` → FOTO
- `btnDocCurpCont2` → CURP (duplicate for tab view)
- `btnDocSaludCont2` → Comprobante Salud
- `btnDocIneTutorCont2` → INE del Tutor

#### Traslados
- `btnDocPacienteCont` → DOCUMENTO (beneficiary)
- `btnDocAcompCont` → DOCUMENTO (companion)
- `btnDocCompDomCont` → DOMICILIO

#### EAEyD
- `btnDocCurpCont` → CURP
- `btnDocCompDomCont` → DOMICILIO
- `btnDocFotoInfanteCont` → FOTO
- `btnDocCurpCont2` → CURP
- `btnDocSaludCont2` → Comprobante Médico
- `btnDocIneTutorCont2` → INE del Responsable

**URLs mapped from:**
- `r.url_curp` / `r.url_doc_curp`
- `r.url_comprobante_domicilio`
- `r.url_comprobante_salud` / `r.url_doc_salud`
- `r.url_ine_tutor` / `r.url_doc_ine_tutor`
- `r.url_foto_infante`

---

## 5. CSS CLASSES USED

### Standard Classes (Consistent Across All)
| Class | Purpose |
|-------|---------|
| `.record-row` | Table row container |
| `.selected-row-v3` | Active/selected row highlighting |
| `.status-badge` | Status indicator styling |
| `.live-name` | Beneficiary name (synced in real-time) |
| `.live-curp` | CURP field (synced in real-time) |
| `.editing-mode-title` | Form title when in edit mode |
| `.touched` | Field validation state (traslados) |
| `.text-muted` | Muted text for empty states |

### Inline Styling Patterns
All modules use **inline styles** for:
- Row containers (table cells)
- Date/time displays
- Avatar containers
- Name and CURP sections
- Status badges
- Document buttons

---

## 6. DOCUMENT BUTTON STYLING

### Gradient Colors (INCONSISTENT)

| Module | Gradient Color | Style |
|--------|----------------|-------|
| **Desayunos Fríos** | `#00766c` → `#005a52` | Teal (darker) |
| **Traslados** | `#0d9488` → `#0f766e` | Teal (lighter) |
| **EAEyD** | `#0d9488` → `#0f766e` | Teal (lighter) |

### Button Sizing & Layout

| Module | Padding | Font Size | Width | Hover Effect |
|--------|---------|-----------|-------|--------------|
| **Desayunos Fríos** | `1rem` | `0.95rem` | `100%` | `opacity: 0.85` |
| **Traslados** | `0.6rem 1.2rem` | `0.8rem` | auto | `transform: translateY(-2px)` |
| **EAEyD** | `0.6rem 1.2rem` | `0.8rem` | auto | `transform: translateY(-2px)` |

**⚠️ Issues**: 
- Different gradient colors (Desayunos vs others)
- Different button sizing (100% vs auto width)
- Different hover effects (opacity vs transform)

---

## 7. EVENT LISTENERS & PATTERNS

### Common Across All Modules

| Event | Handler | Purpose |
|-------|---------|---------|
| `DOMContentLoaded` | Session check, UI setup | Initialize page |
| `.click` on table row | Fill form + sync row | Row selection |
| `input` on search | Filter tabla | Live search |
| `input`/`change` on form | `syncActiveRow()` | Live sync to table |

### Traslados-Specific Events

| Event | Handler | Purpose |
|-------|---------|---------|
| `blur` on inputs | Add `.touched` class | Validation feedback |
| `submit` on form | `guardarDictamen()` | Save/update record |
| `click` on reject btn | `btnRechazar` | Reject transfer |
| `change` on fecha field | `actualizarUI_Cupos()` | Update capacity display |

### Navigation Pattern (Consistent)

```javascript
// All three modules implement carousel-style navigation
function navigate(dir) {
    const idx = allRecords.findIndex(r => String(r.id) === String(currentSelectedId));
    const nextIdx = idx + dir;
    if (nextIdx >= 0 && nextIdx < allRecords.length) {
        const nextId = allRecords[nextIdx].id;
        const row = document.querySelector(`tr[data-id="${nextId}"]`);
        if (row) row.click();
    }
}
// Listeners: #btnPrevRec click → navigate(-1)
// Listeners: #btnNextRec click → navigate(1)
```

### Live Sync Pattern (Consistent)

All modules implement `syncActiveRow()` to update table in real-time:
```javascript
document.addEventListener('input', (e) => {
    if (e.target.closest('#registroForm')) {
        syncActiveRow();
    }
});

document.addEventListener('change', (e) => {
    if (e.target.closest('#registroForm')) {
        syncActiveRow();
    }
});
```

---

## 8. STATUS BADGE STYLING

### Color Scheme

| Status | Background | Color | Applies To |
|--------|-----------|-------|-----------|
| ACTIVO / APROBADO | `#dcfce7` (light green) | `#166534` (dark green) | All modules |
| PENDIENTE | `#fef9c3` (light yellow) | `#854d0e` (dark yellow) | Traslados only |
| EN PROCESO | `#dbeafe` (light blue) | `#1e40af` (dark blue) | Traslados only |
| COMPLETADO | `#dcfce7` (light green) | `#166534` (dark green) | Traslados only |
| RECHAZADO/CANCELADO | `#fee2e2` (light red) | `#b91c1c` (dark red) | Traslados only |
| Default | `#f1f5f9` (light gray) | `#64748b` (dark gray) | All modules |

---

## 9. SAVE/UPDATE PATTERNS

### Desayunos Fríos & EAEyD (Identical)
```javascript
async function guardarDictamen(e) {
    if (e) e.preventDefault();
    if (!currentSelectedId) {
        UI.notify('Selecciona un registro primero', 'error');
        return;
    }
    
    const updateData = { /* 17 fields */ };
    
    const res = await fetch(`/api/desayunos_frios/${currentSelectedId}`, {
        method: 'PUT',
        headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.token}`
        },
        body: JSON.stringify(updateData)
    });
}
```

### Traslados (Different - More Complex)
- Validates with `form.checkValidity()`
- Has separate accept/reject buttons
- Validates cupo capacity before allowing acceptance
- Updates with estatus field (ACEPTADO/RECHAZADO)

---

## 10. STANDARDIZATION NEEDS & RECOMMENDATIONS

### 🔴 HIGH PRIORITY

1. **Document Button Styling** - Consolidate gradient colors
   - Current: `#00766c`/`#005a52` vs `#0d9488`/`#0f766e`
   - Recommendation: Use `#0d9488` → `#0f766e` (teal, modern)

2. **Location Field Naming** - Traslados uses different names
   - Traslados: `paciente_domicilio`, `codigo_postal`
   - Others: `localidad`, `cp`
   - Recommendation: Standardize across all three

3. **Button Sizing & Layout**
   - Desayunos: 100% width, padding 1rem
   - Traslados/EAEyD: auto width, padding 0.6rem 1.2rem
   - Recommendation: Use consistent sizing (possibly fixed width or consistent percentage)

### 🟡 MEDIUM PRIORITY

4. **Hover Effects** - Consolidate animation patterns
   - Desayunos: `opacity` change
   - Traslados/EAEyD: `transform: translateY()`
   - Recommendation: Standardize to transform for consistency

5. **Loading Function Naming**
   - Use consistent pattern: `cargarXXX()` across all modules
   - Currently: `cargarDatos()` vs `cargarTraslados()`

6. **renderDocBtn() function duplication**
   - Copy-pasted across all three files
   - Recommendation: Extract to shared utility module

### 🟢 LOW PRIORITY

7. **Missing "No disponible" text**
   - Desayunos: "No disponible"
   - Traslados: "⚠️ No disponible"
   - EAEyD: "⚠️ Falta"
   - Recommendation: Standardize to single message

8. **Date/Time Formatting**
   - All use `formatearFecha()` function (consistent ✓)
   - Time format: toLocaleTimeString('es-MX', {...})

---

## 11. IMPLEMENTATION PATTERNS MATRIX

| Pattern | Desayunos Fríos | Traslados | EAEyD | Status |
|---------|-----------------|-----------|-------|--------|
| Safe element setting | ✓ safeSet() | ✓ setVal() | ✓ safeSet() | Consistent naming needed |
| Live search filter | ✓ | ✓ | ✓ | ✓ STANDARDIZED |
| Live row sync | ✓ syncActiveRow() | ✓ syncActiveRow() | ✓ syncActiveRow() | ✓ STANDARDIZED |
| Carousel navigation | ✓ navigate() | ✓ navigate() | ✓ navigate() | ✓ STANDARDIZED |
| Document button render | **Different sizes** | **Different sizes** | **Different sizes** | ⚠️ NEEDS SYNC |
| Session validation | ✓ | ✓ | ✓ | ✓ STANDARDIZED |
| Table row selection | ✓ .selected-row-v3 | ✓ .selected-row-v3 | ✓ .selected-row-v3 | ✓ STANDARDIZED |

---

## SUMMARY TABLE: CURRENT VS STANDARDIZED

### Current Implementation Pattern
```
DESAYUNOS FRÍOS          TRASLADOS               EAEYD
├─ Gradient: Dark Teal   ├─ Gradient: Light Teal ├─ Gradient: Light Teal
├─ Width: 100%           ├─ Width: auto          ├─ Width: auto
├─ Padding: 1rem         ├─ Padding: 0.6/1.2rem  ├─ Padding: 0.6/1.2rem
├─ localidad field ✓     ├─ NO localidad field   ├─ localidad field ✓
├─ cargarDatos()         ├─ cargarTraslados()    ├─ cargarDatos()
└─ 6 document buttons    └─ 3 document buttons   └─ 6 document buttons
```

### Recommended Standardized Pattern
```
ALL MODULES
├─ Gradient: Light Teal (#0d9488 → #0f766e)
├─ Width: Consistent (recommend 100% or fixed)
├─ Padding: Standardized (0.6rem 1.2rem)
├─ ALL fields: localidad, colonia, tipo_asentamiento, cp, referencias
├─ ALL functions: cargarXXX() naming
├─ ALL buttons: Extracted to shared utility
├─ ALL hovers: transform: translateY(-2px)
└─ ALL missing docs: "No disponible" message
```

---

## CODE DUPLICATION OPPORTUNITIES

### Candidates for Extraction to Shared Module:

1. **formatearFecha()** - Already consistent, keep as-is
2. **renderDocBtn()** - Copy-pasted in all three → Extract to `utils.js`
3. **syncActiveRow()** - Similar logic, slight variations → Extract with config
4. **navigate()** - Identical logic → Extract to shared utilities
5. **updateNavControls()** - Almost identical → Extract to shared
6. **safeSet/setVal** - Identical utility → Extract as `setFormValue()`

---

## NEXT STEPS FOR STANDARDIZATION

1. ✅ Create shared utility module (`formUtils.js`)
2. ✅ Standardize field names (rename traslados fields)
3. ✅ Unify document button styling
4. ✅ Consolidate button sizing
5. ✅ Extract duplicated functions
6. ✅ Update all three modules to use shared utilities
7. ✅ Test for regressions across all modules
