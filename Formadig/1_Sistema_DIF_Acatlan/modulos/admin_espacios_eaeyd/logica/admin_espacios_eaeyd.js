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
    
    UI.setupHeader('Gestión de EAEyD');

    const isAdmin = ['directora', 'admin', 'desarrollador'].includes(session.role);
    const isEAEyD = session.role.includes('desayuno') || session.role.includes('eaeyd');
    
    if (!isEAEyD && !isAdmin) {
        console.warn("Acceso restringido: Redirigiendo...");
    }

    const form = document.getElementById('registroForm');
    const inputSearch = document.getElementById('searchInput');
    const tbody = document.getElementById('listaRegistros');
    const btnSubmit = (form) ? form.querySelector('button[type="submit"]') : null;
    const btnRechazar = document.getElementById('btnRechazar');

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
            localidad:           document.getElementById('localidad')?.value,
            tipo_asentamiento:   document.getElementById('tipo_asentamiento')?.value,
            cp:                  document.getElementById('cp')?.value,
            referencias:         document.getElementById('referencias')?.value,
            tutor:               document.getElementById('tutor')?.value,
            clave_elector_tutor: document.getElementById('clave_elector_tutor')?.value,
            telefono:            document.getElementById('telefono')?.value,
            escuela:             document.getElementById('escuela')?.value?.trim(),
            estatus:             'Aceptado'  
        };

        if (!updateData.escuela) {
            UI.notify('Debes asignar un Punto EAEyD', 'error');
            return;
        }

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.textContent = 'Guardando...';
        }

        try {
            const res = await fetch(`/api/espacios_eaeyd/${currentSelectedId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify(updateData)
            });

            const data = await res.json();

            if (!res.ok) {
                // ✅ MOSTRAR MENSAJE EXACTO DEL BACKEND
                const errorMsg = data.error || data.message || 'Error desconocido del servidor';
                console.error('❌ Error del backend:', errorMsg);
                throw new Error(errorMsg);
            }

            UI.notify('¡Dictamen EAEyD guardado correctamente! ✅', 'success');
            
            if (btnSubmit) {
                btnSubmit.textContent = 'Solicitud Aceptada';
            }

            // Recargar datos y refrescar la tabla VISUALMENTE
            cargarDatos(true); 

        } catch (error) {
            // ✅ MOSTRAR MENSAJE COMPLETO DEL ERROR
            console.error('❌ Error en guardarDictamen:', error.message);
            UI.notify(`❌ Error: ${error.message}`, 'error');
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.textContent = 'Reintentar Guardado';
            }
        }
    }

    async function cargarDatos(render = true) {
        try {
            const res = await fetch('/api/espacios_eaeyd', {
                headers: { 'Authorization': `Bearer ${session.token}` }
            });
            const data = await res.json();
            console.log("Datos de la BD (EAEyD):", data);
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

            const nombreCompleto = r.nombres || 'Sin nombre';

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
                        <!-- Columna Fecha/Hora removida -->
                        <!-- Columna Avatar -->
                        <div style="width: 44px; height: 44px; border-radius: 50%; background: #fee2e2; display: flex; align-items:center; justify-content:center; flex-shrink:0;">
                            <span style="font-size: 1.3rem; filter: grayscale(1); opacity: 0.7;">👤</span>
                        </div>

                        <!-- Columna Nombre/CURP -->
                        <div style="display:flex; flex-direction:column;">
                            <span class="live-name" style="font-weight:700; color: #1e293b; font-size: 0.95rem; line-height:1.2;">${nombreCompleto}</span>
                            <span class="live-curp" style="font-size:0.75rem; color: #64748b; font-family: monospace; letter-spacing: 0.5px; margin-top:2px;">${r.curp || 'SIN CURP'}</span>
                        </div>
                    </div>
                </td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${r.eaeyd_nombre || 'No asignada'}</td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${r.tutor_nombre || '--'}</td>
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
                // Ubicación
                safeSet('localidad', r.localidad);
                safeSet('colonia', r.colonia);
                safeSet('tipo_asentamiento', r.tipo_asentamiento);
                safeSet('cp', r.cp);
                safeSet('referencias', r.referencias);
                // Responsable
                safeSet('tutor', r.tutor);
                safeSet('clave_elector_tutor', r.clave_elector_tutor || r.clave_elector);
                safeSet('telefono', r.telefono);
                // Documentos
                renderDocBtn('btnDocCurpCont', r.url_curp || r.url_doc_curp, 'CURP');
                renderDocBtn('btnDocCompDomCont', r.url_comprobante_domicilio, 'DOMICILIO');
                renderDocBtn('btnDocFotoInfanteCont', r.url_foto_infante, 'FOTO');
                
                // Mapeo a las vistas en Pestañas Individuales
                renderDocBtn('btnDocCurpCont2', r.url_curp || r.url_doc_curp, 'CURP');
                renderDocBtn('btnDocSaludCont2', r.url_comprobante_salud || r.url_doc_salud, 'Comprobante Médico');
                renderDocBtn('btnDocIneTutorCont2', r.url_ine_tutor || r.url_doc_ine_tutor, 'INE del Responsable');
                
                // Dictamen
                safeSet('escuela', (r.escuela && r.escuela !== 'No asignada') ? r.escuela : "");
                
                if (btnSubmit) {
                    btnSubmit.disabled = false;
                    btnSubmit.textContent = 'Aceptar Solicitud';
                }
            });
            tbody.appendChild(tr);
        });
    }

    if (form) form.addEventListener('submit', guardarDictamen);
    
    // Event listener para botón Rechazar
    if (btnRechazar) {
        btnRechazar.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!currentSelectedId) {
                UI.notify('Selecciona un registro primero', 'error');
                return;
            }
            
            if (!confirm('¿Estás seguro de que deseas rechazar y denegar permanentemente esta solicitud?')) return;

            if (btnSubmit) btnSubmit.disabled = true;
            btnRechazar.disabled = true;
            btnRechazar.textContent = 'Rechazando...';

            try {
                const res = await fetch(`/api/espacios_eaeyd/${currentSelectedId}`, {
                    method: 'PUT',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${session.token}`
                    },
                    body: JSON.stringify({ estatus: 'Rechazado' })
                });

                const data = await res.json();

                if (res.ok) {
                    UI.notify('✅ Solicitud rechazada correctamente.', 'success');
                    if (btnSubmit) {
                        btnSubmit.disabled = true;
                        btnSubmit.textContent = 'Aceptar Solicitud';
                    }
                    cargarDatos(true);
                } else {
                    UI.notify(`❌ Error al rechazar: ${data.error || 'Operación fallida'}`, 'error');
                }
            } catch (error) {
                console.error('Network Error:', error);
                UI.notify('❌ Error de conexión al servidor', 'error');
            } finally {
                if (btnSubmit) btnSubmit.disabled = false;
                btnRechazar.disabled = false;
                btnRechazar.textContent = 'Rechazar Solicitud';
            }
        });
    }
    
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
            console.log("🔍 ESPACIOS EAEYD - Detectado ID en URL:", folioId);
            try {
                const response = await fetch(`/api/espacios_eaeyd/${folioId}`, {
                    headers: { 'Authorization': `Bearer ${session.token}` }
                });
                if (!response.ok) throw new Error(`Error ${response.status}`);
                
                const data = await response.json();
                console.log("📡 Datos cargados del folio:", data);
                console.log("📝 Llenando formulario con campos:");
                
                // Llenar campos específicos de EAEyD
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

    // --- Lógica de Navegación tipo Carrusel ---
    function updateNavControls() {
        const total = allRecords.length;
        const idx = allRecords.findIndex(r => String(r.id) === String(currentSelectedId));
        const navCont = document.getElementById('navCarousel');
        const counter = document.getElementById('navCounter');
        const btnPrev = document.getElementById('btnPrevRec');
        const btnNext = document.getElementById('btnNextRec');

        if (!navCont || total === 0) {
            if (navCont) navCont.style.display = 'none';
            return;
        }

        if (idx === -1) {
            navCont.style.display = 'none';
            return;
        }

        navCont.style.display = 'flex';
        counter.textContent = `${idx + 1} de ${total}`;

        if (btnPrev) {
            btnPrev.disabled = (idx === 0);
            btnPrev.style.opacity = (idx === 0) ? '0.3' : '1';
        }
        if (btnNext) {
            btnNext.disabled = (idx === total - 1);
            btnNext.style.opacity = (idx === total - 1) ? '0.3' : '1';
        }
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

        // 2. Escuela/Plantel (Punto EAEyD)
        if (cells[1]) cells[1].textContent = document.getElementById('escuela')?.value || 'No asignada';
        
        // 3. Tutor (Responsable)
        if (cells[2]) cells[2].textContent = document.getElementById('tutor')?.value || '--';
        
        // 4. Estatus (Badge)
        const badge = cells[3].querySelector('.status-badge');
        if (badge) {
            const val = (document.getElementById('estatus')?.value || 'ACTIVO').toUpperCase();
            badge.textContent = val;
            badge.style.background = (val === 'ACEPTADO' || val === 'ACTIVO' || val === 'APROBADO') ? '#dcfce7' : '#f1f5f9';
            badge.style.color = (val === 'ACEPTADO' || val === 'ACTIVO' || val === 'APROBADO') ? '#166534' : '#64748b';
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
