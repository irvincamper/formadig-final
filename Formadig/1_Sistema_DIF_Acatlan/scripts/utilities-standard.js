/**
 * UTILITIES ESTÁNDAR - Sistema DIF Acatlán
 * Funciones compartidas para unificación de ubicación, documentos y UI
 * Uso: Importar en todos los módulos de administración
 */

// ============================================================================
// 1. FORMATEO DE DATOS
// ============================================================================

function formatearFecha(fechaString) {
    if (!fechaString) return 'S/F';
    const fecha = new Date(fechaString);
    if (isNaN(fecha.getTime())) return 'Inválida';
    const dia = fecha.getDate().toString().padStart(2, '0');
    const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
    const año = fecha.getFullYear();
    return `${dia}/${mes}/${año}`;
}

function escaparHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================================================
// 2. SETTER SEGURO PARA INPUTS
// ============================================================================

function safeSet(id, value) {
    const el = document.getElementById(id);
    if (el) el.value = value || '';
    return el;
}

function safeSetText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text || '';
    return el;
}

// ============================================================================
// 3. LLENADO UNIFICADO DE UBICACIÓN
// ============================================================================

/**
 * Llena los campos de ubicación con datos estandarizados
 * @param {Object} record - Objeto con datos del registro
 * @param {Object} fieldMapping - Mapping personalizado si aplica
 */
function llenarUbicacion(record, fieldMapping = {}) {
    const defaults = {
        'localidad': 'localidad',
        'colonia': 'colonia',
        'tipo_asentamiento': 'tipo_asentamiento',
        'codigo_postal': 'codigo_postal',
        'referencias': 'referencias',
        // Campos alternativos (para compatibilidad)
        'cp': 'cp',
    };

    const mapping = { ...defaults, ...fieldMapping };

    // Usar IDs estándar para ubicación
    const locationIds = {
        'localidad': document.getElementById('localidad'),
        'colonia': document.getElementById('colonia'),
        'tipo_asentamiento': document.getElementById('tipo_asentamiento'),
        'codigo_postal': document.getElementById('codigo_postal'),
        'referencias': document.getElementById('referencias'),
    };

    // Llenar campos exactos
    if (locationIds.localidad) 
        locationIds.localidad.value = record.localidad || '';
    
    if (locationIds.colonia) 
        locationIds.colonia.value = record.colonia || '';
    
    if (locationIds.tipo_asentamiento) 
        locationIds.tipo_asentamiento.value = record.tipo_asentamiento || '';
    
    if (locationIds.codigo_postal) 
        locationIds.codigo_postal.value = record.codigo_postal || record.cp || '';
    
    if (locationIds.referencias) 
        locationIds.referencias.value = record.referencias || '';
}

// ============================================================================
// 4. GESTIÓN INTELIGENTE DE DOCUMENTOS
// ============================================================================

/**
 * Crea un botón inteligente para documentos
 * Si existe URL → activo (verde)
 * Si no existe → deshabilitado (gris)
 */
function renderDocumentoBtn(containerId, url, label = 'VER DOCUMENTO', icon = '📄') {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (url && url.trim() && url !== 'null' && url !== 'undefined') {
        container.innerHTML = `
            <a href="${url}" target="_blank" rel="noopener noreferrer"
               style="display:inline-flex; align-items:center; gap:0.4rem; padding:0.6rem 1.2rem;
                      background: linear-gradient(135deg, #10b981, #059669); color:white;
                      border-radius:8px; font-weight:700; font-size:0.8rem;
                      box-shadow: 0 2px 8px rgba(16,185,129,0.3);
                      text-decoration:none; transition: all 0.2s;
                      cursor:pointer; border:none;"
               onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(16,185,129,0.5)'"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(16,185,129,0.3)'">
                ${icon} ${label}
            </a>`;
    } else {
        container.innerHTML = `
            <span style="display:inline-flex; align-items:center; gap:0.4rem; padding:0.6rem 1.2rem;
                         background:#e2e8f0; color:#94a3b8; border-radius:8px; 
                         font-weight:600; font-size:0.8rem; cursor:not-allowed;">
                ⚠️ No disponible
            </span>`;
    }
}

// ============================================================================
// 5. HORARIOS PREDETERMINADOS PARA TRASLADOS
// ============================================================================

function establecerHorariosTraslados() {
    const salida = document.getElementById('hora_salida');
    const regreso = document.getElementById('hora_regreso');

    if (salida) salida.value = '03:00';
    if (regreso) regreso.value = '15:30';
}

// ============================================================================
// 6. RENDERIZADO ESTÁNDAR DE TABLA CON ESTILOS MEJORADOS
// ============================================================================

/**
 * Aplica estilos estándar a una fila de tabla
 */
function estilizarFilaTabla(tr, isSelected = false) {
    if (isSelected) {
        tr.style.backgroundColor = '#e0f2fe';
        tr.style.borderLeft = '4px solid #0284c7';
    } else {
        tr.style.transition = 'background-color 0.2s ease';
    }

    tr.addEventListener('mouseenter', () => {
        if (!isSelected) {
            tr.style.backgroundColor = '#f1f5f9';
        }
    });

    tr.addEventListener('mouseleave', () => {
        if (!isSelected) {
            tr.style.backgroundColor = '';
        }
    });
}

// ============================================================================
// 7. CONFIGURACIÓN DE PANEL IZQUIERDO (Spacing Mejorado)
// ============================================================================

function mejorarEspacioPanelIzquierdo() {
    const inputs = document.querySelectorAll('#registroForm input, #registroForm select, #registroForm textarea');
    
    inputs.forEach(input => {
        // Aumentar padding
        input.style.padding = '0.75rem 1rem';
        input.style.marginBottom = '1.5rem';
        
        // Bordes redondeados
        input.style.borderRadius = '0.5rem';
        
        // Focus mejorado
        input.addEventListener('focus', () => {
            input.style.boxShadow = '0 0 0 3px rgba(13, 148, 136, 0.1)';
        });
        
        input.addEventListener('blur', () => {
            input.style.boxShadow = '';
        });
    });

    // Mejorar labels
    const labels = document.querySelectorAll('#registroForm label');
    labels.forEach(label => {
        label.style.marginBottom = '0.5rem';
        label.style.fontWeight = '600';
        label.style.fontSize = '0.9rem';
        label.style.color = '#1e293b';
    });
}

// ============================================================================
// 8. LLENADO UNIFICADO DE DOCUMENTOS (MULTIPLE)
// ============================================================================

/**
 * Llena múltiples documentos a la vez
 */
function llenarDocumentos(record) {
    // Desayunos - Documentos del beneficiario
    renderDocumentoBtn('btnDocCurp', record.url_curp, 'CURP');
    renderDocumentoBtn('btnDocSalud', record.url_comprobante_salud, 'SALUD');
    renderDocumentoBtn('btnDocIne', record.url_ine_tutor, 'INE');
    renderDocumentoBtn('btnDocDomicilio', record.url_comprobante_domicilio, 'DOMICILIO');
    renderDocumentoBtn('btnDocFoto', record.url_foto_infante, 'FOTO');

    // Traslados - Documentos específicos
    renderDocumentoBtn('btnDocBenef', record.url_doc_beneficiario, 'PACIENTE');
    renderDocumentoBtn('btnDocAcomp', record.url_doc_acompanante, 'ACOMPAÑANTE');
    renderDocumentoBtn('btnDocCompDom', record.url_comprobante_domicilio, 'DOMICILIO');
}

// ============================================================================
// 9. VALIDACIÓN DE CAMPO CLAVEELECTOR
// ============================================================================

function llenarClaveElector(record) {
    // Para traslados: acompanante_clave_elector
    const claveAcomp = document.getElementById('acompanante_clave_elector');
    if (claveAcomp) {
        claveAcomp.value = record.acompanante_clave_elector || '';
    }

    // Para desayunos: clave_elector_tutor
    const claveTutor = document.getElementById('clave_elector_tutor');
    if (claveTutor) {
        claveTutor.value = record.clave_elector_tutor || '';
    }
}

// ============================================================================
// 10. EXPORTAR PARA USO EN MÓDULOS
// ============================================================================

window.AppUtilities = {
    formatearFecha,
    escaparHTML,
    safeSet,
    safeSetText,
    llenarUbicacion,
    renderDocumentoBtn,
    establecerHorariosTraslados,
    estilizarFilaTabla,
    mejorarEspacioPanelIzquierdo,
    llenarDocumentos,
    llenarClaveElector
};
