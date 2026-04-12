// Función estándar para formatear fechas
function formatearFecha(fechaString) {
    if (!fechaString) return 'S/F';
    const fecha = new Date(fechaString);
    if (isNaN(fecha.getTime())) return 'Inválida';
    const dia = fecha.getDate().toString().padStart(2, '0');
    const mes = (fecha.getMonth() + 1).toString().padStart(2, '0');
    const año = fecha.getFullYear();
    return `${dia}/${mes}/${año}`;
}

// ========== FUNCIÓN GLOBAL: Llenar valores de forma ==========
function setValue(fieldId, fieldValue) {
    const element = document.getElementById(fieldId);
    if (element) {
        element.value = fieldValue || '';
        console.log(`   ✓ ${fieldId} = "${fieldValue}"`);
    } else {
        console.warn(`   ⚠️ Campo no encontrado: ${fieldId}`);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const session = Auth.checkSession();
    if (!session) return;
    
    UI.setupHeader('Gestión de Desayunos Fríos');

    const isAdmin = ['directora', 'admin', 'desarrollador'].includes(session.role);
    const isFrios = session.role.includes('desayuno') || session.role.includes('frios');
    
    if (!isFrios && !isAdmin) {
        console.warn("Acceso restringido: Redirigiendo...");
    }

    const form = document.getElementById('registroForm');
    const inputSearch = document.getElementById('searchInput');
    const tbody = document.getElementById('listaRegistros');
    const btnSubmit = (form) ? form.querySelector('button[type="submit"]') : null;

    let allRecords = [];
    let currentSelectedId = null;

    const safeSet = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.value = val || "";
    };

    async function guardarDictamen(e) {
        if (e) e.preventDefault();
        
        if (!currentSelectedId) {
            UI.notify('Selecciona un registro primero', 'error');
            return;
        }

        const updateData = {
            nombre_beneficiario: document.getElementById('nombre_beneficiario')?.value,
            curp:                document.getElementById('curp')?.value,
            apellidos:           document.getElementById('apellidos')?.value,
            fecha_nacimiento:    document.getElementById('fecha_nacimiento')?.value,
            sexo:                document.getElementById('sexo')?.value,
            estado_civil:        document.getElementById('estado_civil')?.value,
            peso_menor:          document.getElementById('peso_menor')?.value,
            estatura_menor:      document.getElementById('estatura_menor')?.value,
            nivel_estudios:      document.getElementById('nivel_estudios')?.value,
            ingreso_mensual:     document.getElementById('ingreso_mensual')?.value,
            situacion_vulnerabilidad: document.getElementById('situacion_vulnerabilidad')?.checked,
            localidad:           document.getElementById('localidad')?.value,
            colonia:             document.getElementById('colonia')?.value,
            tipo_asentamiento:   document.getElementById('tipo_asentamiento')?.value,
            cp:                  document.getElementById('cp')?.value,
            referencias:         document.getElementById('referencias')?.value,
            tutor:               document.getElementById('tutor')?.value,
            clave_elector_tutor: document.getElementById('clave_elector_tutor')?.value,
            telefono:            document.getElementById('telefono')?.value,
            escuela:             document.getElementById('escuela')?.value?.trim(),
            estatus:             document.getElementById('estatus')?.value
        };

        if (!updateData.escuela) {
            UI.notify('Debes asignar una Escuela', 'error');
            return;
        }

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.textContent = 'Guardando...';
        }

        try {
            const res = await fetch(`/api/desayunos_frios/${currentSelectedId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify(updateData)
            });

            if (!res.ok) throw new Error('Error en el servidor');

            UI.notify('¡Dictamen Fríos guardado correctamente! ✅', 'success');
            
            if (btnSubmit) {
                btnSubmit.textContent = 'Fríos Actualizado 🥛';
            }

            cargarDatos(true); 

        } catch (error) {
            UI.notify(`❌ Error: ${error.message}`, 'error');
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.textContent = 'Reintentar Guardado';
            }
        }
    }

    async function cargarDatos(render = true) {
        try {
            const res = await fetch('/api/desayunos_frios', {
                headers: { 'Authorization': `Bearer ${session.token}` }
            });
            const data = await res.json();
            allRecords = data.desayunos || data.registros || [];
            renderTabla(allRecords);

            // Auto-seleccionar el primero si hay registros y ninguno está seleccionado
            if (allRecords.length > 0 && !currentSelectedId) {
                const firstRow = document.querySelector('#listaRegistros tr[data-id]');
                if (firstRow) firstRow.click();
            } else {
                updateNavControls();
            }
        } catch (error) {
            if (tbody) tbody.innerHTML = '<tr><td colspan="4">Error al conectar</td></tr>';
        }
    }

    function renderDocBtn(containerId, url, label) {
        const cont = document.getElementById(containerId);
        if (!cont) return;
        if (url) {
            cont.innerHTML = `<a href="${url}" target="_blank" rel="noopener noreferrer"
                style="display:inline-flex; align-items:center; justify-content:center; width:100%; gap:0.5rem; padding:1rem;
                background: linear-gradient(135deg, #00766c, #005a52); color:white;
                border-radius:12px; font-weight:700; font-size:0.95rem;
                text-decoration:none; transition: opacity 0.2s; box-shadow: 0 4px 10px rgba(0,118,108,0.2);"
                onmouseover="this.style.opacity='0.85'" onmouseout="this.style.opacity='1'">
                📄 Ver ${label}
            </a>`;
        } else {
            cont.innerHTML = '<span style="font-size: 0.85rem; opacity: 0.5;">No disponible</span>';
        }
    }

    function renderTabla(registros) {
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (registros.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; padding:3rem; opacity:0.6;">No hay registros disponibles.</td></tr>';
            return;
        }

        registros.forEach(r => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-id', r.id);
            tr.classList.add('record-row');

            const statusUpper = String(r.estatus || 'ACTIVO').toUpperCase();
            let badgeStyle = 'background: #f1f5f9; color: #64748b;';
            if (statusUpper === 'APROBADO' || statusUpper === 'ACTIVO') badgeStyle = 'background: #dcfce7; color: #166534;';

            if (currentSelectedId === r.id) tr.classList.add('selected-row-v3');

            const nombreCompleto = `${r.nombre_beneficiario || ''} ${r.apellidos || ''}`.trim() || 'Sin nombre';

            // Formatear Fecha usando función estándar
            const fechaStr = formatearFecha(r.fecha_registro || r.fecha_nacimiento || r.created_at);
            let horaStr = "--:--";
            try {
                if (r.created_at) {
                    const f = new Date(r.created_at);
                    if (!isNaN(f.getTime())) {
                        horaStr = f.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: true }).toUpperCase();
                    }
                }
            } catch (e) {
                console.error("Error al formatear hora:", e);
            }

            tr.innerHTML = `
                <td style="padding: 1rem 1.25rem;">
                    <div style="display:flex; align-items:center; gap:1.25rem;">
                        <!-- Columna Fecha/Hora -->
                        <div style="display:flex; flex-direction:column; min-width:85px; text-align:left;">
                            <span style="font-weight:700; color:#00766c; font-size: 0.9rem;">${fechaStr}</span>
                            <span style="font-size:0.75rem; color:#64748b; font-weight:500;">${horaStr}</span>
                        </div>
                        
                        <!-- Columna Avatar -->
                        <div style="width: 44px; height: 44px; border-radius: 50%; background: #e2e8f0; display: flex; align-items:center; justify-content:center; flex-shrink:0;">
                            <span style="font-size: 1.3rem; filter: grayscale(1); opacity: 0.7;">👤</span>
                        </div>

                        <!-- Columna Nombre/CURP -->
                        <div style="display:flex; flex-direction:column;">
                            <span class="live-name" style="font-weight:700; color: #1e293b; font-size: 0.95rem; line-height:1.2;">${nombreCompleto}</span>
                            <span class="live-curp" style="font-size:0.75rem; color: #64748b; font-family: monospace; letter-spacing: 0.5px; margin-top: 2px;">${r.curp || 'SIN CURP'}</span>
                        </div>
                    </div>
                </td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${r.escuela || 'No asignada'}</td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${r.tutor || '--'}</td>
                <td style="padding: 1rem 1.25rem; text-align: right;"><span class="status-badge" style="${badgeStyle}">${statusUpper}</span></td>
            `;


            tr.addEventListener('click', () => {
                currentSelectedId = r.id;
                document.querySelectorAll('#listaRegistros tr').forEach(row => row.classList.remove('selected-row-v3'));
                tr.classList.add('selected-row-v3');

                // Resaltar el título del formulario
                document.getElementById('formTitle')?.classList.add('editing-mode-title');

                updateNavControls();

                safeSet('nombre_beneficiario', r.nombre_beneficiario);
                safeSet('curp', r.curp);
                safeSet('apellidos', r.apellidos);
                safeSet('fecha_nacimiento', r.fecha_nacimiento);
                safeSet('sexo', r.sexo);
                safeSet('estado_civil', r.estado_civil);
                // Datos de Salud
                safeSet('peso_menor', r.peso_menor || r.peso);
                safeSet('estatura_menor', r.estatura_menor || r.estatura || r.talla);
                // Socioeconómico
                safeSet('nivel_estudios', r.nivel_estudios);
                safeSet('ingreso_mensual', r.ingreso_mensual);
                const vulnCheck = document.getElementById('situacion_vulnerabilidad');
                if (vulnCheck) vulnCheck.checked = !!(r.situacion_vulnerabilidad || r.vulnerabilidad);
                // Ubicación
                safeSet('localidad', r.localidad);
                safeSet('colonia', r.colonia);
                safeSet('tipo_asentamiento', r.tipo_asentamiento);
                safeSet('cp', r.cp);
                safeSet('referencias', r.referencias);
                // Tutor
                safeSet('tutor', r.tutor);
                safeSet('clave_elector_tutor', r.clave_elector_tutor || r.clave_elector);
                safeSet('telefono', r.telefono);
                // Documentos
                renderDocBtn('btnDocCurpCont', r.url_curp || r.url_doc_curp, 'CURP');
                renderDocBtn('btnDocCompDomCont', r.url_comprobante_domicilio, 'DOMICILIO');
                renderDocBtn('btnDocFotoInfanteCont', r.url_foto_infante, 'FOTO');
                
                // Documentos en la nueva vista móvil integrada (Datos de Salud y Tutor)
                renderDocBtn('btnDocCurpCont2', r.url_curp || r.url_doc_curp, 'CURP');
                renderDocBtn('btnDocSaludCont2', r.url_comprobante_salud || r.url_doc_salud, 'Comprobante Salud');
                renderDocBtn('btnDocIneTutorCont2', r.url_ine_tutor || r.url_doc_ine_tutor, 'INE del Tutor');
                // Dictamen
                safeSet('escuela', (r.escuela && r.escuela !== 'No asignada') ? r.escuela : "");
                
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.textContent = 'Guardar Dictamen 🥛';
                }
            });
            tbody.appendChild(tr);
        });
    }

    if (form) form.addEventListener('submit', guardarDictamen);
    
    if (inputSearch) {
        inputSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtrados = allRecords.filter(r => 
                (r.nombre_beneficiario || "").toLowerCase().includes(query) || 
                (r.curp || "").toLowerCase().includes(query)
            );
            renderTabla(filtrados);
        });
    }

    cargarDatos();

    // ========== Función de autollenado por URL param ==========
    async function autollenarPorFolio(session) {
        const urlParams = new URLSearchParams(window.location.search);
        const folioId = urlParams.get('id');
        
        if (folioId) {
            console.log("🔍 DESAYUNOS FRÍOS - Detectado ID en URL:", folioId);
            try {
                const response = await fetch(`/api/desayunos_frios/${folioId}`, {
                    headers: { 'Authorization': `Bearer ${session.token}` }
                });
                if (!response.ok) throw new Error(`Error ${response.status}`);
                
                const data = await response.json();
                console.log("📡 Datos cargados del folio:", data);
                console.log("📝 Llenando formulario con campos:");
                
                // Llenar campos específicos de Desayunos
                setValue('nombre_beneficiario', data.nombre_beneficiario || `${data.nombres} ${data.apellidos}`);
                setValue('nombres', data.nombres);
                setValue('apellidos', data.apellidos);
                setValue('curp', data.curp);
                setValue('fecha_nacimiento', data.fecha_nacimiento);
                setValue('sexo', data.sexo);
                setValue('estado_civil', data.estado_civil);
                setValue('peso_menor', data.peso_menor);
                setValue('estatura_menor', data.estatura_menor);
                setValue('nivel_estudios', data.nivel_estudios);
                setValue('ingreso_mensual', data.ingreso_mensual);
                setValue('situacion_vulnerabilidad', data.situacion_vulnerabilidad);
                setValue('localidad', data.localidad);
                setValue('tipo_asentamiento', data.tipo_asentamiento);
                setValue('cp', data.cp);
                setValue('referencias', data.referencias);
                setValue('tutor', data.tutor);
                setValue('clave_elector_tutor', data.clave_elector_tutor);
                setValue('telefono', data.telefono);
                setValue('escuela', data.escuela);
                setValue('estatus', data.estatus);
                
                currentSelectedId = data.id;
                console.log("✅ Formulario poblado automáticamente desde URL");
            } catch (error) {
                console.error("❌ Error cargando folio desde URL:", error);
                // Continuar cargando lista normal
                cargarDatos();
            }
        }
    }
    
    autollenarPorFolio(session);

    // ========================================================================
    // FUNCIÓN: Obtener colonias por Código Postal
    // ========================================================================
    async function cargarColonias(codigoPostal) {
        const selectColonia = document.getElementById('colonia');
        if (!selectColonia) {
            console.error('❌ Select de colonia no encontrado en el DOM');
            return;
        }
        
        if (!codigoPostal || codigoPostal.length !== 5) {
            console.warn(`⚠️ CP inválido o incompleto: "${codigoPostal}"`);
            selectColonia.innerHTML = '<option value="">-- Selecciona una colonia --</option>';
            return;
        }

        console.log(`🔍 Iniciando búsqueda de colonias para CP: ${codigoPostal}`);

        try {
            const url = `/api/colonias/${codigoPostal}`;
            console.log(`📡 Petición GET a: ${url}`);
            
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });

            console.log(`📊 Estado de respuesta: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                console.warn(`⚠️ Error HTTP ${response.status} al obtener colonias`);
                selectColonia.innerHTML = '<option value="">-- No se encontraron colonias --</option>';
                return;
            }

            const data = await response.json();
            console.log("✅ Respuesta del backend para colonias:", data);

            // El backend ahora devuelve array directamente
            const colonias = Array.isArray(data) ? data : (data.colonias || []);
            console.log(`📋 Colonias extraídas (cantidad: ${colonias.length}):`, colonias);

            // Limpiar dropdown
            selectColonia.innerHTML = '<option value="">-- Selecciona una colonia --</option>';
            
            if (colonias.length === 0) {
                console.warn(`⚠️ No hay colonias registradas para CP ${codigoPostal}`);
                selectColonia.innerHTML += '<option disabled style="color: #999;">No hay colonias para este CP</option>';
            } else {
                console.log(`✅ Agregando ${colonias.length} opciones al selector`);
                colonias.forEach((col, idx) => {
                    const nombreColonia = col.nombre || col.name || 'Unnamed';
                    console.log(`   [${idx + 1}] ${nombreColonia}`);
                    
                    const option = document.createElement('option');
                    option.value = nombreColonia;
                    option.textContent = nombreColonia;
                    selectColonia.appendChild(option);
                });
                console.log('✅ Todas las opciones agregadas exitosamente');
            }
        } catch (error) {
            console.error('❌ Error de red/CORS cargando colonias:', error);
            console.error('   Detalles del error:', error.message);
            selectColonia.innerHTML = '<option value="">-- Error cargando colonias --</option>';
        }
    }

    // ========================================================================
    // EVENT LISTENER: Autocompletar colonias cuando cambia CP
    // ========================================================================
    const cpInput = document.getElementById('cp');
    if (cpInput) {
        cpInput.addEventListener('change', (e) => {
            cargarColonias(e.target.value);
        });
    }

    // --- Lógica de Navegación tipo Carrusel ---
    function updateNavControls() {
        const navCont = document.getElementById('navCarousel');
        const counter = document.getElementById('navCounter');
        const btnPrev = document.getElementById('btnPrevRec');
        const btnNext = document.getElementById('btnNextRec');

        if (!navCont || !allRecords.length) return;

        if (!currentSelectedId) {
            navCont.style.display = 'none';
            return;
        }

        const idx = allRecords.findIndex(r => String(r.id) === String(currentSelectedId));
        if (idx === -1) {
            navCont.style.display = 'none';
            return;
        }

        navCont.style.display = 'flex';
        counter.textContent = `${idx + 1} de ${allRecords.length}`;

        btnPrev.disabled = (idx === 0);
        btnNext.disabled = (idx === allRecords.length - 1);
        
        btnPrev.style.opacity = (idx === 0) ? '0.3' : '1';
        btnNext.style.opacity = (idx === allRecords.length - 1) ? '0.3' : '1';
    }

    function navigate(dir) {
        const idx = allRecords.findIndex(r => String(r.id) === String(currentSelectedId));
        const nextIdx = idx + dir;

        if (nextIdx >= 0 && nextIdx < allRecords.length) {
            const nextId = allRecords[nextIdx].id;
            const row = document.querySelector(`tr[data-id="${nextId}"]`);
            if (row) {
                row.click();
                row.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    // --- Utilidades de Navegación ---
    function updateNavControls() {
        const total = allRecords.length;
        const currentIdx = allRecords.findIndex(r => r.id === currentSelectedId);
        const navText = document.getElementById('navInfo');
        if (navText) {
            if (total === 0) {
                navText.textContent = "0 de 0";
            } else {
                navText.textContent = `${currentIdx + 1} de ${total}`;
            }
        }

        const btnPrev = document.getElementById('btnPrevRec');
        const btnNext = document.getElementById('btnNextRec');
        if (btnPrev) btnPrev.disabled = (currentIdx <= 0);
        if (btnNext) btnNext.disabled = (currentIdx === -1 || currentIdx >= total - 1);
    }

    function navigate(direction) {
        if (allRecords.length === 0) return;
        let currentIdx = allRecords.findIndex(r => r.id === currentSelectedId);
        let nextIdx = currentIdx + direction;

        if (nextIdx >= 0 && nextIdx < allRecords.length) {
            const nextId = allRecords[nextIdx].id;
            const nextRow = document.querySelector(`#listaRegistros tr[data-id="${nextId}"]`);
            if (nextRow) nextRow.click();
        }
    }

    document.getElementById('btnPrevRec')?.addEventListener('click', () => navigate(-1));
    document.getElementById('btnNextRec')?.addEventListener('click', () => navigate(1));

    // --- Lógica de Sincronización en Tiempo Real (Versión Ultra-Robusta) ---
    function syncActiveRow() {
        if (!currentSelectedId) return;
        
        // Buscamos la fila en todo el documento
        const row = document.querySelector(`tr[data-id="${currentSelectedId}"]`);
        if (!row) return;

        const cells = row.cells;
        if (!cells || cells.length < 4) return;

        // 1. Nombre y CURP
        const nameSpan = cells[0].querySelector('.live-name');
        if (nameSpan) {
            const nom = document.getElementById('nombre_beneficiario')?.value || '';
            const ape = document.getElementById('apellidos')?.value || '';
            nameSpan.textContent = `${nom} ${ape}`.trim() || 'Sin nombre';
        }
        const curpSpan = cells[0].querySelector('.live-curp');
        if (curpSpan) curpSpan.textContent = document.getElementById('curp')?.value || 'S/C';

        // 2. Escuela/Plantel
        if (cells[1]) cells[1].textContent = document.getElementById('escuela')?.value || 'No asignada';
        
        // 3. Tutor
        if (cells[2]) cells[2].textContent = document.getElementById('tutor')?.value || '--';
        
        // 4. Estatus (Badge)
        const badge = cells[3].querySelector('.status-badge');
        if (badge) {
            const val = (document.getElementById('estatus')?.value || 'ACTIVO').toUpperCase();
            badge.textContent = val;
            badge.style.background = (val === 'APROBADO' || val === 'ACTIVO') ? '#dcfce7' : '#166534';
            badge.style.color = (val === 'APROBADO' || val === 'ACTIVO') ? '#166534' : '#64748b';
        }
    }

    // Escucha global de inputs
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

});
