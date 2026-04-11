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

    const TOTAL_CUPOS = 16;
    let currentSelectedId = null;

    // Hacer global la función de simular carga para el botón de HTML
    window.cargarSolicitudEjemplo = async function() {
        const dummyData = {
            paciente_nombre: "María Sánchez " + Math.floor(Math.random() * 100),
            paciente_curp: "SAMM" + Math.floor(Math.random() * 999999) + "HDFRRM05",
            acompanante_nombre: "Hijo de María",
            destino: "Hospital General Regional",
            cita_fecha: "",
            cita_hora: "",
            lugares_requeridos: 2,
            estatus: "PENDIENTE"
        };
        try {
            // Se usa un workaround de POST porque al simular desde la App Móvil no tienen fecha/hora
            // El backend exige fecha y hora, así que meteré una fecha ficticia muy lejana para que pase validación y luego el Admin la corrija
            dummyData.cita_fecha = "2099-12-31";
            dummyData.cita_hora = "00:00";
            
            await fetch('/api/traslados', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.token}` },
                body: JSON.stringify(dummyData)
            });
            UI.notify("Solicitud de ambulancia recibida y agregada a la lista.", "success");
            cargarTraslados();
        } catch (e) {
            UI.notify("Error al simular carga móvil.", "error");
        }
    };

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
            cita_fecha: document.getElementById('cita_fecha').value,
            cita_hora: document.getElementById('cita_hora').value || '03:00', // Set default to 03:00 AM
            lugares_requeridos: parseInt(document.getElementById('lugares_requeridos').value) || 2,
            estatus: 'PROGRAMADO',
            // Added fields for location and companion
            hora_salida: '03:00', // Fixed departure time (3:00 AM)
            hora_regreso: '15:30', // Fixed return time (3:30 PM)
            acompanante_clave_elector: document.getElementById('acompanante_clave_elector')?.value || ''
        };

        // Validar cupos antes de enviar
        const ocupadosFecha = calcularCuposPorFecha(updateData.cita_fecha);
        if (ocupadosFecha + updateData.lugares_requeridos > TOTAL_CUPOS) {
            UI.notify(`❌ No hay suficientes cupos disponibles para el día ${formData.cita_fecha}.`, 'error');
            return;
        }

        const btnSubmit = form.querySelector('button[type="submit"]');
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Guardando...';

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
                UI.notify('✅ Solicitud agendada correctamente.', 'success');
                currentSelectedId = null;
                form.reset();
                document.getElementById('paciente_nombre').value = "";
                document.getElementById('paciente_curp').value = "";
                document.getElementById('destino').value = "";
                inputs.forEach(input => input.classList.remove('touched'));
                cargarTraslados(); // Refrescar tabla
            } else {
                UI.notify(`❌ Error: ${data.message || 'No se pudo agendar'}`, 'error');
            }
        } catch (error) {
            console.error('Network Error:', error);
            UI.notify('❌ Error de conexión al servidor de Traslados (Puerto 5004)', 'error');
        } finally {
            btnSubmit.disabled = false;
            btnSubmit.textContent = 'Agendar Traslado 🚑';
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
        const solicitudesDelDia = allRecords.filter(t => t.fecha_cita === fecha && t.estatus !== 'CANCELADO');
        return solicitudesDelDia.reduce((total, t) => total + (t.lugares_requeridos || 2), 0);
    }

    function actualizarUI_Cupos() {
        const fechaSeleccionada = inputFecha.value;
        if (!fechaSeleccionada) {
            cuposOcupadosEl.textContent = '-';
            cuposDisponiblesTextEl.textContent = 'Seleccione fecha para ver cupos';
            cuposDisponiblesTextEl.style.color = 'var(--color-text-muted)';
            return;
        }

        const ocupados = calcularCuposPorFecha(fechaSeleccionada);
        const disponibles = TOTAL_CUPOS - ocupados;
        
        cuposOcupadosEl.textContent = ocupados;
        cuposDisponiblesTextEl.textContent = `${disponibles} lugares disponibles (Día: ${fechaSeleccionada})`;

        if (disponibles <= 0) {
            cuposOcupadosEl.style.color = '#e53e3e'; // Rojo
            cuposDisponiblesTextEl.style.color = '#e53e3e';
            cuposDisponiblesTextEl.textContent = 'AMBULANCIA LLENA EL DÍA SELECCIONADO';
        } else if (disponibles <= 4) {
            cuposOcupadosEl.style.color = '#d97706'; // Naranja
            cuposDisponiblesTextEl.style.color = '#d97706';
        } else {
            cuposOcupadosEl.style.color = 'var(--color-primary-dark)';
            cuposDisponiblesTextEl.style.color = '#22543d';
        }
    }

    // 7. Búsqueda y Filtrado en Tiempo Real
    inputSearch.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtrados = allRecords.filter(t => 
            t.paciente_nombre.toLowerCase().includes(query) ||
            (t.paciente_curp && t.paciente_curp.toLowerCase().includes(query)) ||
            (t.destino_hospital && t.destino_hospital.toLowerCase().includes(query))
        );
        renderTabla(filtrados);
    });

    function renderTabla(records) {
        if (!records || records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;" class="text-muted">No se encontraron registros.</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        records.forEach(t => {
            const tr = document.createElement('tr');
            
            // Badge Dinámico del estado
            const statusUpper = (t.estatus || 'Oculto').toUpperCase();
            const badgeClass = statusUpper === 'PROGRAMADO' ? 'status--programado' 
                             : statusUpper === 'EN PROCESO' ? 'status--en-proceso' 
                             : '';

            tr.innerHTML = `
                <td style="font-size:0.9rem;">${t.fecha_cita.includes('2099') ? 'Sin asignar' : t.fecha_cita}</td>
                <td style="font-weight:500; font-size:0.95rem;">${t.paciente_nombre}</td>
                <td class="text-muted" style="font-size:0.9rem;">${t.destino_hospital || t.destino || '-'}</td>
                <td style="font-size:0.9rem;">${(t.hora_salida === '00:00:00' || t.hora_salida === '00:00') ? 'Sin asignar' : t.hora_salida}</td>
                <td><span class="status-badge ${badgeClass}">${statusUpper}</span></td>
            `;

            tr.addEventListener('click', () => {
                currentSelectedId = r.id || t.id; // r está en los otros, t aquí
                document.getElementById('paciente_nombre').value = t.paciente_nombre;
                document.getElementById('paciente_curp').value = t.paciente_curp || '';
                document.getElementById('destino').value = t.destino_hospital || t.destino || '';
                
                // Fill location fields from the record
                document.getElementById('localidad').value = t.localidad || '';
                document.getElementById('colonia').value = t.colonia || '';
                document.getElementById('tipo_asentamiento').value = t.tipo_asentamiento || '';
                document.getElementById('cp').value = t.cp || '';
                document.getElementById('paciente_domicilio').value = t.paciente_domicilio || '';
                document.getElementById('referencias').value = t.referencias || '';
                
                // Fill companion clave elector if available
                document.getElementById('acompanante_clave_elector').value = t.acompanante_clave_elector || '';
                
                if(!t.fecha_cita.includes('2099')) document.getElementById('cita_fecha').value = t.fecha_cita;
                else document.getElementById('cita_fecha').value = "";
                
                if(t.hora_salida !== '00:00' && t.hora_salida !== '00:00:00') document.getElementById('cita_hora').value = t.hora_salida;
                else document.getElementById('cita_hora').value = "";
                
                btnSubmit.disabled = false;
                const actionBlock = document.getElementById('asignacionBloque');
                actionBlock.style.background = '#dcfce3';
                setTimeout(() => actionBlock.style.background = '#f0fdf4', 800);
            });

            tbody.appendChild(tr);
        });
    }

});
