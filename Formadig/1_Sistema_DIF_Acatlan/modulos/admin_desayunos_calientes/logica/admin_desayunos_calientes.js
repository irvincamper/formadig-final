document.addEventListener('DOMContentLoaded', () => {
    const session = Auth.checkSession();
    if (!session) return;
    
    UI.setupHeader('Gestión de Desayunos Calientes');

    // Permisos flexibles para evitar que "regrese" al Dashboard por error
    const isAdmin = ['directora', 'admin', 'desarrollador'].includes(session.role);
    const isDesayunos = session.role.includes('desayuno') || session.role.includes('calientes');
    
    if (!isDesayunos && !isAdmin) {
        console.warn("Acceso restringido: Redirigiendo...");
        // Solo redirigir si realmente no tiene nada que ver con el módulo
        // setTimeout(() => window.location.href = '../../../dashboard.html', 1500); 
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
            UI.notify('Debes asignar un Comedor Escolar', 'error');
            return;
        }

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.textContent = 'Guardando...';
        }

        try {
            const res = await fetch(`/api/desayunos_calientes/${currentSelectedId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify(updateData)
            });

            if (!res.ok) throw new Error('Error en el servidor');

            UI.notify('¡Dictamen guardado correctamente! ✅', 'success');
            
            // YA NO HACEMOS RESET NI LIMPIEZA AGRESIVA
            // Mantenemos los datos visibles para confirmar
            
            if (btnSubmit) {
                btnSubmit.textContent = 'Dictamen Actualizado 🍲';
                // El botón se queda deshabilitado para evitar doble clic
            }

            // Recargar datos y refrescar la tabla VISUALMENTE
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
            const res = await fetch('/api/desayunos_calientes', {
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
                style="display:inline-flex; align-items:center; gap:0.4rem; padding:0.6rem 1.2rem;
                background: linear-gradient(135deg, #0d9488, #0f766e); color:white;
                border-radius:10px; font-weight:700; font-size:0.8rem;
                box-shadow: 0 4px 10px rgba(13,148,136,0.2);
                text-decoration:none; transition: all 0.2s;"
                onmouseover="this.style.transform='translateY(-2px)'" 
                onmouseout="this.style.transform='translateY(0)'">
                📄 VER DOCUMENTO
            </a>`;
        } else {
            cont.innerHTML = '<span style="font-size: 0.8rem; font-weight:600; color:#94a3b8;"><span style="opacity:0.6;">⚠️ Falta</span></span>';
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

            // Formatear Fecha (Efecto ultra-seguro contra nulos)
            let fechaStr = "--/--/--";
            let horaStr = "--:--";
            try {
                if (r.created_at) {
                    const f = new Date(r.created_at);
                    if (!isNaN(f.getTime())) {
                        fechaStr = f.toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' });
                        horaStr = f.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: true }).toUpperCase();
                    }
                }
            } catch (e) {
                console.error("Error al formatear fecha:", e);
            }

            tr.innerHTML = `
                <td style="padding: 1rem 1.25rem;">
                    <div style="display:flex; align-items:center; gap:1.25rem;">
                        <!-- Columna Fecha/Hora (Estilo Captura) -->
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
                renderDocBtn('btnDocSaludCont', r.url_comprobante_salud || r.url_doc_salud, 'Comprobante Salud');
                renderDocBtn('btnDocIneTutorCont', r.url_ine_tutor || r.url_doc_ine_tutor, 'INE del Tutor');
                renderDocBtn('btnDocFotoInfanteCont', r.url_foto_infante, 'FOTO');
                renderDocBtn('btnDocCompDomCont', r.url_comprobante_domicilio, 'DOMICILIO');
                
                // Mapeo a las vistas en Pestañas Individuales
                renderDocBtn('btnDocCurpCont2', r.url_curp || r.url_doc_curp, 'CURP');
                renderDocBtn('btnDocSaludCont2', r.url_comprobante_salud || r.url_doc_salud, 'Comprobante Salud');
                renderDocBtn('btnDocIneTutorCont2', r.url_ine_tutor || r.url_doc_ine_tutor, 'INE del Tutor');
                
                // Dictamen
                safeSet('escuela', (r.escuela && r.escuela !== 'No asignada') ? r.escuela : "");
                
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.textContent = 'Guardar Dictamen 🍲';
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

    document.getElementById('btnPrevRec')?.addEventListener('click', () => navigate(-1));
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
        
        // Buscamos la fila en todo el documento para máxima seguridad
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
            badge.style.background = (val === 'APROBADO' || val === 'ACTIVO') ? '#dcfce7' : '#f1f5f9';
            badge.style.color = (val === 'APROBADO' || val === 'ACTIVO') ? '#166534' : '#64748b';
        }
    }

    // Escucha global de inputs para asegurar que funcione siempre
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
