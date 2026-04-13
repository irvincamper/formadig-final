// Función estándar para formatear fechas (parse local para evitar desfase UTC)
function formatearFecha(fechaString) {
    if (!fechaString) return 'S/F';
    // Si viene en formato YYYY-MM-DD parsear como local (sin UTC shift)
    const matchISO = String(fechaString).match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (matchISO) {
        const [, y, m, d] = matchISO;
        return `${d}/${m}/${y}`;
    }
    // Fallback
    const fecha = new Date(fechaString);
    if (Number.isNaN(fecha.getTime())) return 'Inválida';
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

// ========== INICIALIZAR SUPABASE CLIENTE PARA REALTIME ==========
let supabaseClient = null;
let realtimeChannel = null;

try {
    supabaseClient = supabase.createClient(
        'https://ctiqbycbkcftwuqgzxjb.supabase.co',
        'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk'
    );
    console.log('✅ Cliente Supabase inicializado para Realtime');
} catch (error) {
    console.warn('⚠️ Error inicializando Supabase cliente:', error);
    supabaseClient = null;
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificación de sesión y Setup Header
    const session = Auth.checkSession();
    if (!session) return;
    
    // Configurar Header y Menú Inmediatamente
    UI.setupHeader('Módulo Operativo - Traslados');

    // Estado local para búsqueda y filtro
    let allRecords = [];
    let paginaActual = 1;
    const registrosPorPagina = 10;

    // Referencias a DOM
    const form = document.getElementById('registroForm');
    const tbody = document.getElementById('listaRegistros');
    const cuposOcupadosEl = document.getElementById('cuposOcupados');
    const cuposDisponiblesTextEl = document.getElementById('cuposDisponiblesText');
    const btnSubmit = form.querySelector('button[type="submit"]');
    const btnRechazar = document.getElementById('btnRechazar');
    const searchInput = document.getElementById('searchInput');  // ← BUSCAR

    const TOTAL_CUPOS = 16;
    let currentSelectedId = null;


    // 2. Cargar datos iniciales - Con autollenado por URL param
    async function autollenarPorFolio() {
        const urlParams = new URLSearchParams(window.location.search);
        const folioId = urlParams.get('id');
        
        if (folioId) {
            console.log("🔍 Detectado ID en URL:", folioId);
            try {
                const response = await fetch(`/api/traslados/${folioId}`);
                if (!response.ok) throw new Error(`Error ${response.status}`);
                
                const data = await response.json();
                console.log("📡 Datos cargados del folio:", data);
                console.log("📝 Llenando formulario con campos:");
                
                // Usar la función global setValue para llenar todos los campos
                setValue('paciente_curp', data.paciente_curp);
                setValue('paciente_nombre', data.paciente_nombre);
                setValue('paciente_edad', data.paciente_edad);

                setValue('colonia', data.paciente_colonia || data.colonia);
                setValue('cp', data.paciente_cp || data.cp);
                setValue('paciente_domicilio', data.paciente_domicilio);
                setValue('referencias', data.paciente_referencias || data.referencias);
                setValue('destino_hospital', data.destino_hospital);
                setValue('acompanante_nombre', data.acompanante_nombre);
                setValue('acompanante_clave_elector', data.acompanante_clave_elector);
                setValue('telefono_principal', data.telefono_principal);
                setValue('telefono_secundario', data.telefono_secundario);
                setValue('fecha_viaje', data.fecha_viaje);
                setValue('hora_cita', data.hora_cita);
                setValue('lugares_requeridos', data.lugares_requeridos);
                
                currentSelectedId = data.id;
                console.log("✅ Formulario poblado automáticamente desde URL");
            } catch (error) {
                console.error("❌ Error cargando folio desde URL:", error);
                cargarTraslados();
            }
        } else {
            // Si no hay ID en URL, cargar lista normal
            cargarTraslados();
        }
    }
    
    autollenarPorFolio();

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

    // ========================================================================
    // EVENT LISTENER: BÚSQUEDA (LUPA) - Filtrar lista de traslados
    // ========================================================================
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            
            if (!query) {
                // Si está vacío, mostrar todos
                renderTabla(allRecords);
            } else {
                // Filtrar por paciente_nombre o paciente_curp
                const filtrados = allRecords.filter(t => {
                    const nombre = (t.paciente_nombre || '').toLowerCase();
                    const curp = (t.paciente_curp || '').toLowerCase();
                    return nombre.includes(query) || curp.includes(query);
                });
                renderTabla(filtrados);
            }
        });
    }

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
            paciente_nombre: document.getElementById('paciente_nombre')?.value?.toUpperCase().trim(),
            paciente_curp:   document.getElementById('paciente_curp')?.value?.toUpperCase().trim(),
            paciente_domicilio: document.getElementById('paciente_domicilio')?.value?.toUpperCase().trim(),
            localidad: undefined,
            colonia: document.getElementById('colonia')?.value?.toUpperCase().trim(),
            cp: document.getElementById('cp')?.value,
            referencias: document.getElementById('referencias')?.value?.toUpperCase().trim(),
            destino_hospital: document.getElementById('destino_hospital')?.value?.toUpperCase().trim(),
            fecha_viaje:     document.getElementById('fecha_viaje').value,
            hora_cita:       document.getElementById('hora_cita').value,
            telefono_principal: document.getElementById('telefono_principal')?.value,
            telefono_secundario: document.getElementById('telefono_secundario')?.value,
            acompanante_clave_elector: document.getElementById('acompanante_clave_elector')?.value?.toUpperCase().trim(),
            acompanante_nombre: document.getElementById('acompanante_nombre')?.value?.toUpperCase().trim(),
            lugares_requeridos: parseInt(document.getElementById('lugares_requeridos').value) || 2,
            estatus:         'ACEPTADO'
        };

        // Validar cupos antes de enviar
        const fechaParaValidar = updateData.fecha_viaje;
        const ocupadosFecha = calcularCuposPorFecha(fechaParaValidar);
        if (ocupadosFecha + updateData.lugares_requeridos > TOTAL_CUPOS) {
            UI.notify(`❌ No hay suficientes cupos disponibles para el día ${fechaParaValidar}.`, 'error');
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
            UI.notify('❌ Error de conexión al servidor. Verifica la conexión de red.', 'error');
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
            // Obtener datos del usuario autenticado
            const user = Auth.getUser();
            const userEmail = user?.email || '';
            const userRole = user?.role || '';
            
            const res = await fetch('/api/traslados', {
                headers: {
                    'Authorization': `Bearer ${session.token}`,
                    'X-User-Email': userEmail,
                    'X-User-Role': userRole
                }
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
            
            // ========== INICIAR ESCUCHA REALTIME ==========
            iniciarRealtimeTraslados();

        } catch (error) {
            console.error('Error cargando traslados:', error);
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#e53e3e;">
                ⚠️ No se pudieron cargar los registros. El servidor backend podría estar apagado.
            </td></tr>`;
        }
    }
    
    // ========== FUNCIÓN: REALTIME - Escuchar cambios en la tabla traslados ==========
    async function iniciarRealtimeTraslados() {
        if (!supabaseClient) {
            console.warn('⚠️ Cliente Supabase no disponible, Realtime deshabilitado');
            return;
        }
        
        try {
            // Si hay un canal anterior, limpiarlo
            if (realtimeChannel) {
                await realtimeChannel.unsubscribe();
            }
            
            // Crear nuevo canal escuchando cambios en traslados
            realtimeChannel = supabaseClient.channel('public:traslados', {
                config: { broadcast: { self: true } }
            })
            .on('postgres_changes', 
                { 
                    event: '*',  // Escuchar INSERT, UPDATE, DELETE
                    schema: 'public',
                    table: 'traslados'
                },
                (payload) => {
                    console.log('🔄 Cambio detectado en traslados:', payload);
                    
                    // Re-cargar los traslados del backend
                    cargarTraslados();
                }
            )
            .subscribe((status) => {
                if (status === 'SUBSCRIBED') {
                    console.log('✅ Realtime conectado - Escuchando cambios en traslados');
                } else if (status === 'CLOSED') {
                    console.log('⚠️ Realtime desconectado');
                }
            });
        } catch (error) {
            console.error('❌ Error iniciando Realtime:', error);
        }
    }

    // 6. Lógica de Cupos (Máx 16)
    inputFecha.addEventListener('change', actualizarUI_Cupos);

    function calcularCuposPorFecha(fecha) {
        if (!fecha) return 0;
        const solicitudesDelDia = allRecords.filter(t => {
            // La columna real en la BD es 'fecha'; fecha_viaje es el alias del form
            const fechaT = t.fecha || t.fecha_viaje || '';
            const estatusValido = ['ACEPTADO', 'PROGRAMADO', 'COMPLETADO', 'REALIZADO', 'CONFIRMADO'].includes((t.estatus || '').toUpperCase());
            return fechaT === fecha && estatusValido;
        });
        return solicitudesDelDia.reduce((total, t) => total + (t.lugares_requeridos || 2), 0);
    }

    function actualizarUI_Cupos() {
        let fechaSeleccionada = document.getElementById('fecha_viaje').value;
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
        if (url && url.trim()) {
            cont.innerHTML = `<a href="${url}" target="_blank" rel="noopener noreferrer"
                style="display:inline-flex; align-items:center; gap:0.4rem; padding:0.6rem 1.2rem;
                background: linear-gradient(135deg, #0d9488, #0f766e); color:white;
                border-radius:10px; font-weight:700; font-size:0.8rem;
                box-shadow: 0 4px 10px rgba(13,148,136,0.2);
                text-decoration:none; transition: all 0.2s;"
                onmouseover="this.style.transform='translateY(-2px)'" 
                onmouseout="this.style.transform='translateY(0)'">
                📄 VER ${label || 'DOCUMENTO'}
            </a>`;
        } else {
            cont.innerHTML = '<span style="font-size: 0.8rem; font-weight:600; color:#94a3b8;"><span style="opacity:0.6;">⚠️ No disponible</span></span>';
        }
    }

    function renderTabla(records) {
        // Guardar todos los registros para paginación
        allRecords = records || [];

        if (!allRecords || allRecords.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;" class="text-muted">No se encontraron registros.</td></tr>';
            actualizarControlesPaginacion();
            return;
        }

        // Lógica de Paginación
        const inicio = (paginaActual - 1) * registrosPorPagina;
        const fin = inicio + registrosPorPagina;
        const datosPagina = allRecords.slice(inicio, fin);

        tbody.innerHTML = '';
        datosPagina.forEach(t => {
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
                            <span style="font-weight:700; color:#0d9488; font-size: 0.9rem;">${formatearFecha(t.fecha)}</span>
                            <span style="font-size:0.75rem; color:#64748b; font-weight:500;">${(t.hora || '--:--').substring(0, 5).toUpperCase()}</span>
                        </div>
                        
                        <!-- Columna Avatar -->
                        <div style="width: 44px; height: 44px; border-radius: 50%; background: #e2e8f0; display: flex; align-items:center; justify-content:center; flex-shrink:0;">
                            <span style="font-size: 1.3rem; filter: grayscale(1); opacity: 0.7;">👤</span>
                        </div>
                    </div>
                </td>
                <td style="padding: 1rem 1.25rem;">
                    <div style="display:flex; flex-direction:column;">
                        <span class="live-name" style="font-weight:700; color: #1e293b; font-size: 0.95rem; line-height:1.2;">
                            ${t.paciente_nombre || 'Sin nombre'} ${confirmacionIcono}
                        </span>
                        <span class="live-curp" style="font-size:0.75rem; color: #64748b; font-family: monospace; letter-spacing: 0.5px; margin-top:2px;">
                            ${t.paciente_curp || 'SIN CURP'}
                        </span>
                    </div>
                </td>
                <td style="padding: 1rem 1.25rem; font-size: 0.85rem; color: #475569;">${t.destino_hospital || 'No asignado'}</td>
                <td style="padding: 1rem 1.25rem; text-align: right;">
                    <span class="status-badge" style="${badgeStyle}">${statusUpper}</span>
                    ${t.kilometraje_salida != null ? `<br><span style="font-size:0.75rem; color:#64748b;">Km: ${t.kilometraje_salida ?? 0}→${t.kilometraje_llegada ?? 0}</span>` : ''}
                </td>
            `;

// 👇 CAMBIO 1: Agregamos "async" aquí
                    tr.addEventListener('click', async () => {
                        try {
                            currentSelectedId = t.id;
                            document.querySelectorAll('#listaRegistros tr').forEach(row => row.classList.remove('selected-row-v3'));
                            tr.classList.add('selected-row-v3');
                            
                            // Resaltar el título del formulario
                            document.getElementById('formTitle')?.classList.add('editing-mode-title');
                            
                            updateNavControls();
                            
                            // ════════════════════════════════════════════════════════════════════════
                            // FUNCIÓN HELPER: Llenar valor en input con validación
                            // ════════════════════════════════════════════════════════════════════════
                            const setVal = (id, val) => {
                                const el = document.getElementById(id);
                                if (el) el.value = val || '';
                            };
                            
                            // ════════════════════════════════════════════════════════════════════════
                            // PESTAÑA 1: DATOS (Identidad y Contacto)
                            // ════════════════════════════════════════════════════════════════════════
                            setVal('paciente_curp', t.paciente_curp || '');
                            setVal('paciente_nombre', t.paciente_nombre || '');
                            setVal('paciente_edad', t.paciente_edad || '');
                            setVal('telefono_principal', t.telefono_principal || '');
                            setVal('telefono_secundario', t.telefono_secundario || '');
                            
                           // ════════════════════════════════════════════════════════════════════════
                            // PESTAÑA 2: UBICACIÓN
                            // ════════════════════════════════════════════════════════════════════════
                            setVal('paciente_domicilio', t.paciente_domicilio || '');
                            setVal('cp', t.codigo_postal || '');
                            
                            // 👇 CAMBIO 2: Le decimos que espere a que bajen las colonias antes de seguir
                            if (t.codigo_postal) {
                                await cargarColonias(t.codigo_postal);
                            }
                            
                            // Lógica robusta para seleccionar la colonia sin importar mayúsculas/minúsculas
                            const selectColonia = document.getElementById('colonia');
                            if (selectColonia && t.colonia) {
                                const option = Array.from(selectColonia.options).find(opt => opt.value.toLowerCase() === t.colonia.toLowerCase());
                                if (option) {
                                    selectColonia.value = option.value;
                                } else {
                                    selectColonia.value = '';
                                }
                            } else {
                                setVal('colonia', '');
                            }
                            
                            // Limpiar campos sin elemento visible
                            setVal('referencias', '');
                            
                            // ════════════════════════════════════════════════════════════════════════
                            // 🕵️ CHIVATO: Esto imprimirá en la consola los datos exactos del paciente
                            console.log("👉 Datos que llegan de la BD para este paciente:", t);

                            // ════════════════════════════════════════════════════════════════════════
                            // ════════════════════════════════════════════════════════════════════════
                            // PESTAÑA 3: VIAJE (Detalles médicos y acompañante)
                            // ════════════════════════════════════════════════════════════════════════
                            setVal('destino_hospital', t.destino_hospital || '');
                            
                            // 📅 FECHA (Lee de la columna t.fecha)
                            let fViaje = '';
                            if (t.fecha) { // <-- Corregido al nombre real de tu columna
                                if (t.fecha.includes('/')) {
                                    let p = t.fecha.split('/'); 
                                    fViaje = `${p[2]}-${p[1]}-${p[0]}`; 
                                } else {
                                    fViaje = t.fecha.split('T')[0];
                                }
                            }
                            setVal('fecha_viaje', fViaje); // Asume que el input en tu HTML sigue teniendo id="fecha_viaje"
                            
                            // ⏰ HORA DE IDA (Lee de la columna t.hora)
                            let hCita = '';
                            if (t.hora) { // <-- Corregido al nombre real de tu columna
                                let match = String(t.hora).match(/\d{2}:\d{2}/);
                                if (match) hCita = match[0];
                            }
                            setVal('hora_cita', hCita); // Asume que el input en tu HTML sigue teniendo id="hora_cita"

                            // ⏰ HORA DE REGRESO (NUEVO CAMPO: Lee de t.hora_regreso)
                            let hRegreso = '';
                            if (t.hora_regreso) {
                                let matchReg = String(t.hora_regreso).match(/\d{2}:\d{2}/);
                                if (matchReg) hRegreso = matchReg[0];
                            }
                            setVal('hora_regreso', hRegreso); // ¡OJO! Asegúrate de tener un <input type="time" id="hora_regreso"> en tu HTML

                            // LOS OTROS CAMPOS
                            setVal('acompanante_nombre', t.acompanante_nombre || '');
                            setVal('acompanante_clave_elector', t.acompanante_clave_elector || '');
                            setVal('estatus', t.estatus || '');
                            
                            // Automatización de Cupos
                            if (t.acompanante_nombre && t.acompanante_nombre.trim() !== '') {
                                setVal('lugares_requeridos', 2); // Va con acompañante
                            } else {
                                setVal('lugares_requeridos', 1); // Va solo
                            }


                    // ════════════════════════════════════════════════════════════════════════
                    // PESTAÑA 4: DOCS (Evidencias fotográficas/PDF)
                    // ════════════════════════════════════════════════════════════════════════
                    renderDocBtn('btnDocPacienteCont', t.url_doc_beneficiario || null, 'DOCUMENTO');
                    renderDocBtn('btnDocAcompCont', t.url_doc_acompanante || null, 'DOCUMENTO');
                    renderDocBtn('btnDocCompDomCont', t.url_comprobante_domicilio || null, 'DOMICILIO');
                    
                    // ════════════════════════════════════════════════════════════════════════
                    // AUTOMATIZACIONES
                    // ════════════════════════════════════════════════════════════════════════
                    // Si no hay fecha, asignar fecha de hoy
                    let fechaVal = t.fecha_viaje || '';
                    if (!fechaVal) {
                        const today = new Date().toISOString().split('T')[0];
                        setVal('fecha_viaje', today);
                    }
                    
                    // Si no hay hora, asignar hora + 1
                    let horaVal = t.hora_cita || '';
                    if (!horaVal) {
                        const now = new Date();
                        now.setHours(now.getHours() + 1);
                        horaVal = now.toTimeString().slice(0, 5);
                        setVal('hora_cita', horaVal);
                    }
                    
                    // Actualizar UI de cupos
                    actualizarUI_Cupos();
                    
                    // Habilitar botones de acción
                    btnSubmit.disabled = false;
                    btnRechazar.disabled = false;
                    btnSubmit.textContent = 'Aceptar Traslado 🚐';
                    
                    const actionBlock = document.getElementById('asignacionBloque');
                    if (actionBlock) {
                        actionBlock.style.transform = 'scale(1.02)';
                        actionBlock.style.boxShadow = '0 10px 25px rgba(22,101,52,0.15)';
                        actionBlock.style.borderColor = '#22c55e';
                        setTimeout(() => {
                            actionBlock.style.transform = '';
                            actionBlock.style.boxShadow = '';
                            actionBlock.style.borderColor = '#bbf7d0';
                        }, 600);
                    }
                } catch (error) {
                    console.error('Error al seleccionar traslado:', error);
                }
            });

            tbody.appendChild(tr);
        });

        actualizarControlesPaginacion();
    }

    function actualizarControlesPaginacion() {
        const totalPaginas = Math.ceil(allRecords.length / registrosPorPagina);
        const pagText = document.getElementById('pagActualText');
        const btnPrev = document.getElementById('btnAnterior');
        const btnNext = document.getElementById('btnSiguiente');

        if (pagText) pagText.textContent = `Página ${paginaActual} de ${totalPaginas || 1}`;
        
        if (btnPrev) {
            btnPrev.disabled = (paginaActual === 1);
            btnPrev.style.opacity = btnPrev.disabled ? '0.5' : '1';
        }
        
        if (btnNext) {
            btnNext.disabled = (paginaActual === totalPaginas || totalPaginas === 0);
            btnNext.style.opacity = btnNext.disabled ? '0.5' : '1';
        }
    }

    // Eventos de Paginación
    document.getElementById('btnAnterior')?.addEventListener('click', () => {
        if (paginaActual > 1) {
            paginaActual--;
            renderTabla(allRecords);
        }
    });

    document.getElementById('btnSiguiente')?.addEventListener('click', () => {
        const totalPaginas = Math.ceil(allRecords.length / registrosPorPagina);
        if (paginaActual < totalPaginas) {
            paginaActual++;
            renderTabla(allRecords);
        }
    });

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
        
        // Buscamos la fila en la tabla
        const row = document.querySelector(`#listaRegistros tr[data-id="${currentSelectedId}"]`);
        if (!row) return;

        // Obtener los valores actuales del formulario
        const nom = document.getElementById('paciente_nombre')?.value || 'Sin nombre';
        const curp = document.getElementById('paciente_curp')?.value || 'SIN CURP';
        const destino = document.getElementById('destino_hospital')?.value || 'No asignado';
        const estatus = (document.getElementById('estatus')?.value || 'PENDIENTE').toUpperCase();

        // Actualizar los spans dentro de la fila (si existen)
        const nameSpan = row.querySelector('.live-name');
        if (nameSpan) {
            nameSpan.textContent = nom;
        }
        
        const curpSpan = row.querySelector('.live-curp');
        if (curpSpan) {
            curpSpan.textContent = curp;
        }

        // Actualizar la segunda celda (destino)
        const cells = row.cells;
        if (cells && cells.length > 2) {
            cells[2].textContent = destino;
        }

        // Actualizar el badge de estado
        const statusBadge = row.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.textContent = estatus;
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
