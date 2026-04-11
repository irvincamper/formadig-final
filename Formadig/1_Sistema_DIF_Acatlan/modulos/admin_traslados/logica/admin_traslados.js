document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificación de sesión y Setup Header
    const session = Auth.checkSession();
    if (!session) return;
    
    // Configurar Header y Menú Inmediatamente
    UI.setupHeader('Módulo Operativo - Traslados');

    // Estado local para búsqueda y filtro
    let allRecords = [];

    // Referencias a DOM
    const form = document.getElementById('registroForm');
    const inputSearch = document.getElementById('searchInput');
    const inputFecha = document.getElementById('cita_fecha');
    const tbody = document.getElementById('listaRegistros');
    const cuposOcupadosEl = document.getElementById('cuposOcupados');
    const cuposDisponiblesTextEl = document.getElementById('cuposDisponiblesText');
    const btnSubmit = form.querySelector('button[type="submit"]');
    const btnRechazar = document.getElementById('btnRechazar');

    const TOTAL_CUPOS = 16;
    let currentSelectedId = null;


    // 2. Cargar datos iniciales
    cargarTraslados();

    // 3. Validación en tiempo real (touched logic)
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', () => input.classList.add('touched'));
    });

    // 4. Lógica de Envío (Guardar Solicitud)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Chequear validez nativa de HTML5
        if (!form.checkValidity()) {
            inputs.forEach(input => input.classList.add('touched')); // Forzar mostrado de errores
            UI.notify('Por favor, completa correctamente todos los campos marcados en rojo.', 'error');
            return;
        }

        if (!currentSelectedId) {
            UI.notify('Selecciona una solicitud pendiente de la tabla primero.', 'error');
            return;
        }

        const updateData = {
            paciente_nombre: document.getElementById('paciente_nombre')?.value,
            paciente_curp:   document.getElementById('paciente_curp')?.value,
            localidad:       document.getElementById('localidad')?.value,
            destino:         document.getElementById('destino')?.value,
            cita_fecha:      document.getElementById('cita_fecha').value,
            cita_hora:       document.getElementById('cita_hora').value,
            telefono:        document.getElementById('telefono')?.value,
            telefono_emergencia: document.getElementById('telefono_emergencia')?.value,
            clave_elector:   document.getElementById('clave_elector')?.value,
            tutor:           document.getElementById('tutor')?.value,
            acomp_curp:      document.getElementById('acomp_curp')?.value,
            acomp_sexo:      document.getElementById('acomp_sexo')?.value,
            lugares_requeridos: parseInt(document.getElementById('lugares_requeridos').value) || 2,
            estatus:         'ACEPTADO'
        };

        // Validar cupos antes de enviar
        const ocupadosFecha = calcularCuposPorFecha(updateData.cita_fecha);
        if (ocupadosFecha + updateData.lugares_requeridos > TOTAL_CUPOS) {
            UI.notify(`❌ No hay suficientes cupos disponibles para el día ${updateData.cita_fecha}.`, 'error');
            return;
        }

        const btnSubmit = form.querySelector('button[type="submit"]');
        const btnRechazar = document.getElementById('btnRechazar');
        if (btnSubmit) btnSubmit.disabled = true;
        if (btnRechazar) btnRechazar.disabled = true;
        if (btnSubmit) btnSubmit.textContent = 'Guardando...';

        try {
            const res = await fetch(`/api/traslados/${currentSelectedId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify(updateData)
            });

            const data = await res.json();

            if (res.ok) {
                UI.notify('¡Traslado guardado correctamente! ✅', 'success');
                btnSubmit.textContent = 'Traslado Actualizado 🚐';
                
                // YA NO LIMPIAMOS currentSelectedId para que el usuario vea el cambio en la tabla resaltada
                // currentSelectedId = null;
                // form.reset(); 
                inputs.forEach(input => input.classList.remove('touched'));
                btnSubmit.disabled = true;
                btnRechazar.disabled = true;
                cargarTraslados(); 
            } else {
                UI.notify(`❌ Error: ${data.message || data.error || 'No se pudo aceptar la solicitud'}`, 'error');
            }
        } catch (error) {
            console.error('Network Error:', error);
            UI.notify('❌ Error de conexión al servidor de Traslados (Puerto 5004)', 'error');
        } finally {
            // El texto se mantiene como 'Traslado Actualizado 🚐' en éxito,
            // pero si falló o es el inicio, debe decir algo sensato.
            if (btnSubmit.textContent === 'Guardando...') {
                 btnSubmit.disabled = false;
                 btnRechazar.disabled = false;
                 btnSubmit.textContent = 'Aceptar Traslado 🚐';
            }
        }
    });

    btnRechazar.addEventListener('click', async () => {
        if (!currentSelectedId) {
            UI.notify('Selecciona una solicitud pendiente de la tabla primero.', 'error');
            return;
        }
        
        if (!confirm('¿Estás seguro de que deseas rechazar y cancelar permanentemente este traslado?')) return;

        btnSubmit.disabled = true;
        btnRechazar.disabled = true;
        btnRechazar.textContent = 'Rechazando...';

        try {
            const res = await fetch(`/api/traslados/${currentSelectedId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify({ estatus: 'RECHAZADO' })
            });

            const data = await res.json();
            if (res.ok) {
                UI.notify(data.message || '❌ Solicitud rechazada correctamente.', 'success');
                // Ya no limpiamos para ver el cambio instantáneo
                // currentSelectedId = null;
                // form.reset();
                btnSubmit.disabled = true;
                btnRechazar.disabled = true;
                cargarTraslados(); 
            } else {
                UI.notify(`❌ Error al rechazar: ${data.error || 'Operación fallida'}`, 'error');
            }
        } catch (error) {
            console.error('Network Error:', error);
            UI.notify('❌ Error de conexión al servidor.', 'error');
        } finally {
            btnSubmit.disabled = false;
            btnRechazar.disabled = false;
            btnRechazar.innerHTML = 'Rechazar ✖';
        }
    });

    // 5. Cargar y renderizar la Tabla (Bitácora)
    async function cargarTraslados() {
        try {
            const res = await fetch('/api/traslados', {
                headers: { 'Authorization': `Bearer ${session.token}` }
            });
            
            if (!res.ok) throw new Error('Falló fetch');
            const data = await res.json();
            
            allRecords = data.traslados || [];
            renderTabla(allRecords);
            actualizarUI_Cupos();

            // Auto-seleccionar el primero si hay registros y ninguno está seleccionado
            if (allRecords.length > 0 && !currentSelectedId) {
                const firstRow = document.querySelector('#listaRegistros tr[data-id]');
                if (firstRow) firstRow.click();
            } else {
                updateNavControls();
            }

        } catch (error) {
            console.error('Error cargando traslados:', error);
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#e53e3e;">
                ⚠️ No se pudieron cargar los registros. El servidor backend podría estar apagado.
            </td></tr>`;
        }
    }

    // 6. Lógica de Cupos (Máx 16)
    inputFecha.addEventListener('change', actualizarUI_Cupos);

    function calcularCuposPorFecha(fecha) {
        if (!fecha) return 0;
        const solicitudesDelDia = allRecords.filter(t => {
            const fechaT = t.fecha_cita || t.fecha || t.fecha_viaje || '';
            // Solo contar las solicitudes que fueron aceptadas/programadas/confirmadas
            const estatusValido = ['ACEPTADO', 'PROGRAMADO', 'COMPLETADO', 'REALIZADO', 'CONFIRMADO'].includes(t.estatus);
            return fechaT === fecha && estatusValido;
        });
        return solicitudesDelDia.reduce((total, t) => total + (t.lugares_requeridos || 2), 0);
    }

    function actualizarUI_Cupos() {
        let fechaSeleccionada = document.getElementById('cita_fecha').value;
        let esHoy = false;
        
        if (!fechaSeleccionada) {
            fechaSeleccionada = new Date().toISOString().split('T')[0];
            esHoy = true;
        }

        const ocupados = calcularCuposPorFecha(fechaSeleccionada);
        const disponibles = TOTAL_CUPOS - ocupados;
        
        cuposOcupadosEl.textContent = ocupados;
        
        if (esHoy) {
            cuposDisponiblesTextEl.textContent = `${disponibles} lugares disp. (HOY: ${fechaSeleccionada})`;
        } else {
            cuposDisponiblesTextEl.textContent = `${disponibles} lugares disponibles (Día: ${fechaSeleccionada})`;
        }

        if (disponibles <= 0) {
            cuposOcupadosEl.style.color = 'var(--color-error)';
            cuposDisponiblesTextEl.style.color = 'var(--color-error)';
            cuposDisponiblesTextEl.textContent = 'AMBULANCIA LLENA EL DÍA SELECCIONADO';
        } else if (disponibles <= 4) {
            cuposOcupadosEl.style.color = 'var(--color-warning)';
            cuposDisponiblesTextEl.style.color = 'var(--color-warning)';
        } else {
            cuposOcupadosEl.style.color = 'var(--color-primary-dark)';
            cuposDisponiblesTextEl.style.color = 'var(--color-success)';
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
                📄 VER ${label}
            </a>`;
        } else {
            cont.innerHTML = '<span style="font-size: 0.8rem; font-weight:600; color:#94a3b8;"><span style="opacity:0.6;">⚠️ No disponible</span></span>';
        }
    }

    function renderTabla(records) {
        if (!records || records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;" class="text-muted">No se encontraron registros.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        records.forEach(t => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-id', t.id);
            tr.classList.add('record-row');
            
            const statusUpper = String(t.estatus || 'PENDIENTE').toUpperCase();
            let badgeStyle = 'background: #f1f5f9; color: #64748b;';
            if (statusUpper === 'ACEPTADO' || statusUpper === 'PROGRAMADO' || statusUpper === 'CONFIRMADO') badgeStyle = 'background: #dcfce7; color: #166534;';
            else if (statusUpper === 'PENDIENTE') badgeStyle = 'background: #fef9c3; color: #854d0e;';
            else if (statusUpper === 'EN PROCESO') badgeStyle = 'background: #dbeafe; color: #1e40af;';
            else if (statusUpper === 'COMPLETADO') badgeStyle = 'background: #dcfce7; color: #166534;';
            else if (statusUpper === 'RECHAZADO' || statusUpper === 'CANCELADO' || statusUpper === 'DENEGADO') badgeStyle = 'background: #fee2e2; color: #b91c1c;';

            if (currentSelectedId === t.id) tr.classList.add('selected-row-v3');

            let confirmacionIcono = '';
            if (statusUpper === 'CONFIRMADO') {
                confirmacionIcono = ' <span title="Confirmado por SMS" style="font-size: 1.2rem; margin-left: 6px; display:inline-block; animation: pop 0.4s ease-out;">✅</span>';
            } else if (statusUpper === 'RECHAZADO') {
                confirmacionIcono = ' <span title="Rechazado por SMS" style="font-size: 1.2rem; margin-left: 6px;">❌</span>';
            }
            // Fecha y hora: usar los campos de la app móvil si están disponibles
            const fechaRaw = t.fecha_cita || t.fecha || t.fecha_viaje || null;
            const horaRaw  = t.hora_salida || t.hora || '--:--';

            const fechaDisplay = fechaRaw
                ? `<span style="font-weight:600; color:var(--color-primary);">${fechaRaw}</span>`
                : '<span style="opacity:0.5; font-size:0.8rem;">Sin fecha</span>';

            const tieneDocsBenef = t.url_doc_beneficiario ? `<a href="${t.url_doc_beneficiario}" target="_blank" title="Ver doc. beneficiario" style="margin-left:6px;">📄</a>` : '';
            const tieneDocsAcomp = t.url_doc_acompanante  ? `<a href="${t.url_doc_acompanante}"  target="_blank" title="Ver doc. acompañante"  style="margin-left:4px;">📄</a>` : '';

            tr.innerHTML = `
                <td style="padding: 1rem 1.25rem;">
                    <div style="display:flex; align-items:center; gap:1.25rem;">
                        <!-- Columna Fecha/Hora -->
                        <div style="display:flex; flex-direction:column; min-width:85px;">
                            <span style="font-weight:700; color:#0d9488; font-size: 0.9rem;">${t.fecha_viaje || t.fecha || "S/F"}</span>
                            <span style="font-size:0.75rem; color:#64748b; font-weight:500;">${(t.hora_cita || t.hora || "--:--").toUpperCase()}</span>
                        </div>
                        
                        <!-- Columna Avatar -->
                        <div style="width: 44px; height: 44px; border-radius: 50%; background: #e2e8f0; display: flex; align-items:center; justify-content:center; flex-shrink:0;">
                            <span style="font-size: 1.3rem; filter: grayscale(1); opacity: 0.7;">👤</span>
                        </div>

                        <!-- Columna Nombre/CURP -->
                        <div style="display:flex; flex-direction:column;">
                            <span class="live-name" style="font-weight:700; color: #1e293b; font-size: 0.95rem; line-height:1.2;">
                                ${t.paciente_nombre || 'Sin nombre'} ${confirmacionIcono}
                            </span>
                            <span class="live-curp" style="font-size:0.75rem; color: #64748b; font-family: monospace; letter-spacing: 0.5px; margin-top:2px;">
                                ${t.paciente_curp || 'SIN CURP'}
                            </span>
                        </div>
                    </div>
                </td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${t.destino_hospital || 'No asignado'}</td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${t.acompanante_nombre || t.tutor || '--'} ${tieneDocsBenef}${tieneDocsAcomp}</td>
                <td style="padding: 1rem 1.25rem; text-align: right;">
                    <span class="status-badge" style="${badgeStyle}">${statusUpper}</span>
                    ${t.kilometraje_salida != null ? `<br><span style="font-size:0.75rem; color:#64748b;">Km: ${t.kilometraje_salida ?? 0}→${t.kilometraje_llegada ?? 0}</span>` : ''}
                </td>
            `;


            tr.addEventListener('click', () => {
                currentSelectedId = t.id;
                document.querySelectorAll('#listaRegistros tr').forEach(row => row.classList.remove('selected-row-v3'));
                tr.classList.add('selected-row-v3');
                
                // Resaltar el título del formulario
                document.getElementById('formTitle')?.classList.add('editing-mode-title');
                
                updateNavControls();
                
                // Rellenar panel izquierdo con datos reales de la DB
                let fullName = (t.paciente_nombre || '').trim();
                if (t.apellidos && !fullName.includes(t.apellidos)) {
                    fullName += ` ${t.apellidos}`;
                }
                document.getElementById('paciente_nombre').value = fullName;
                document.getElementById('apellidos').value = t.apellidos || '';
                document.getElementById('paciente_curp').value = t.paciente_curp || '';
                
                // Nuevos mapeos:
                const edadInput = document.getElementById('paciente_edad');
                if (edadInput) edadInput.value = t.paciente_edad || t.edad || '';
                
                document.getElementById('fecha_nacimiento').value = t.fecha_nacimiento || '';
                document.getElementById('sexo').value = t.sexo || t.paciente_sexo || '';
                document.getElementById('estado_civil').value = t.estado_civil || '';
                
                document.getElementById('localidad').value = t.localidad || t.paciente_domicilio || '';
                document.getElementById('colonia').value = t.colonia || '';
                document.getElementById('cp').value = t.cp || '';
                document.getElementById('referencias').value = t.referencias || '';
                
                
                document.getElementById('destino').value = t.destino_hospital || t.destino || '';
                document.getElementById('tutor').value = t.acompanante_nombre || t.tutor || '';
                
                const entidadAcomp = document.getElementById('acompanante_entidad');
                if (entidadAcomp) entidadAcomp.value = t.acompanante_entidad || t.entidad || '';
                
                document.getElementById('telefono').value = t.telefono || t.telefono_principal || '';
                document.getElementById('clave_elector').value = t.clave_elector || '';
                document.getElementById('telefono_emergencia').value = t.telefono_secundario || t.telefono_emergencia || '';
                
                const zonaHosp = document.getElementById('zona_hospital');
                if (zonaHosp) zonaHosp.value = t.zona_hospital || '--';
                
                // ── Lógica de Documentos (Estandarizada) ──
                // Documentación Digital
                renderDocBtn('btnDocPacienteCont', t.url_doc_beneficiario, 'DOCUMENTO');
                renderDocBtn('btnDocAcompCont', t.url_doc_acompanante, 'DOCUMENTO');
                renderDocBtn('btnDocCompDomCont', t.url_comprobante_domicilio, 'DOMICILIO');
                
                // Automatización: Pre-llenar si vienen vacíos para el bloque de agendamiento
                let fechaVal = t.fecha_viaje || t.fecha || '';
                let horaVal = t.hora_cita || t.hora || '';

                // Mapear estos valores estáticos a la pestaña de vista "Datos de la Cita Médica"
                const fSol = document.getElementById('fecha_solicitada');
                if (fSol) fSol.value = fechaVal || '--';
                const hSol = document.getElementById('hora_solicitada');
                if (hSol) hSol.value = horaVal || '--';

                if (!fechaVal) {
                    const today = new Date().toISOString().split('T')[0];
                    fechaVal = today;
                }
                if (!horaVal) {
                    const now = new Date();
                    now.setHours(now.getHours() + 1); // Sugerir 1 hora después
                    horaVal = now.toTimeString().slice(0, 5);
                }

                document.getElementById('cita_fecha').value = fechaVal;
                document.getElementById('cita_hora').value = horaVal;
                document.getElementById('lugares_requeridos').value = t.lugares_requeridos || 2;
                
                // Actualizar automáticamente los cupos cuando se carga la fecha
                actualizarUI_Cupos();
                
                btnSubmit.disabled = false;
                btnRechazar.disabled = false;
                btnSubmit.textContent = 'Aceptar Traslado 🚐';
                
                const actionBlock = document.getElementById('asignacionBloque');
                actionBlock.style.transform = 'scale(1.02)';
                actionBlock.style.boxShadow = '0 10px 25px rgba(22,101,52,0.15)';
                actionBlock.style.borderColor = '#22c55e';
                setTimeout(() => {
                    actionBlock.style.transform = '';
                    actionBlock.style.boxShadow = '';
                    actionBlock.style.borderColor = '#bbf7d0';
                }, 600);
            });

            tbody.appendChild(tr);
        });
    }

    // --- Lógica de Sincronización en Tiempo Real (Live Sync) ---
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
    document.getElementById('btnNextRec')?.addEventListener('click', () => navigate(1));

    // --- Lógica de Sincronización en Tiempo Real (Versión Ultra-Robusta) ---
    function syncActiveRow() {
        if (!currentSelectedId) return;
        
        // Buscamos la fila en todo el documento
        const row = document.querySelector(`tr[data-id="${currentSelectedId}"]`);
        if (!row) return;

        const cells = row.cells;
        if (!cells || cells.length < 5) return;

        // 1. Beneficiario (Paciente + CURP)
        const nameSpan = cells[0].querySelector('.live-name');
        if (nameSpan) {
            const nom = document.getElementById('paciente_nombre')?.value || '';
            const ape = document.getElementById('apellidos')?.value || '';
            nameSpan.textContent = `${nom} ${ape}`.trim() || 'Sin nombre';
        }
        const curpSpan = cells[0].querySelector('.live-curp');
        if (curpSpan) curpSpan.textContent = document.getElementById('paciente_curp')?.value || 'S/C';

        // 2. Localidad
        if (cells[1]) {
            const span = cells[1].querySelector('span:last-child');
            if (span) span.textContent = document.getElementById('localidad')?.value || '-';
        }
        
        // 3. Destino
        if (cells[2]) {
            const span = cells[2].querySelector('span:last-child');
            if (span) span.textContent = document.getElementById('destino')?.value || '-';
        }

        // 4. Fecha/Hora
        if (cells[3]) {
            const f = document.getElementById('cita_fecha')?.value || '--';
            const h = document.getElementById('cita_hora')?.value || '--';
            cells[3].textContent = `${f} / ${h}`;
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
