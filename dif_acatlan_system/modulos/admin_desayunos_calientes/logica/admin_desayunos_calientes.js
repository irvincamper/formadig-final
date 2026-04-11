document.addEventListener('DOMContentLoaded', () => {
    const session = Auth.checkSession();
    if (!session) return;
    
    // Configurar Header y Menú Inmediatamente
    UI.setupHeader('Gestión de Desayunos Calientes');

    const isAdmin = ['directora', 'admin', 'desarrollador'].includes(session.role);
    if (!session.role.includes('desayuno') && !isAdmin) {
        UI.notify('Acceso denegado: Este módulo es exclusivo.', 'error');
        setTimeout(() => window.location.href = '../../../dashboard.html', 1500);
        return;
    }

    // Referencias a DOM
    const form = document.getElementById('registroForm');
    const inputSearch = document.getElementById('searchInput');
    const tbody = document.getElementById('listaRegistros');
    const btnSubmit = form.querySelector('button[type="submit"]');

    // Estado local
    let allRecords = [];
    let currentSelectedId = null;

    // Cargar datos iniciales
    cargarDesayunos();

    // Eventos
    form.addEventListener('submit', guardarDictamen);

    // Hacer global la función de simular carga para el botón onClick de HTML
    window.cargarSolicitudEjemplo = async function() {
        const dummyData = {
            nombre_beneficiario: "Camila Ruiz Aguilar " + Math.floor(Math.random() * 100),
            curp: "RUAC" + Math.floor(Math.random() * 999999) + "MDFRR09",
            tutor: "José Ruiz Martínez",
            escuela: "Pendiente de Asignación",
            estatus: "Pendiente"
        };
        try {
            const res = await fetch('http://localhost:5006/api/desayunos_calientes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.token}` },
                body: JSON.stringify(dummyData)
            });
            
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Error en el servidor');
            }

            UI.notify("Nueva solicitud de Calientes recibida y agregada al Padrón.", "success");
            cargarDesayunos();
        } catch (e) {
            UI.notify("Error al simular carga móvil: " + e.message, "error");
        }
    };

    async function guardarDictamen(e) {
        e.preventDefault();
        
        if (!currentSelectedId) {
            UI.notify('Selecciona un registro PENDIENTE de la tabla primero.', 'error');
            return;
        }

        const updateData = {
            escuela: document.getElementById('escuela').value.trim(),
            estatus: document.getElementById('estatus').value
        };

        if (!updateData.escuela) {
            UI.notify('Debes asignar un Comedor Escolar.', 'error');
            return;
        }

        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Guardando Dictamen...';

        try {
            const res = await fetch(`http://localhost:5006/api/desayunos_calientes/${currentSelectedId}`, {
                method: 'PUT',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify(updateData)
            });

            if (!res.ok) {
                const errorData = await res.json();
                throw new Error(errorData.error || 'Error al actualizar dictamen');
            }

            UI.notify('¡Dictamen registrado exitosamente en el Padrón de Calientes!', 'success');
            
            // Limpiar selección
            currentSelectedId = null;
            form.reset();
            document.getElementById('nombre_beneficiario').value = "";
            document.getElementById('curp').value = "";
            document.getElementById('tutor').value = "";
            document.getElementById('direccion').value = "";
            
            btnSubmit.disabled = true;
            btnSubmit.textContent = 'Guardar Dictamen y Registrar 🍲';

            // Recargar tabla
            cargarDesayunos();

        } catch (error) {
            UI.notify(`❌ ${error.message}`, 'error');
            btnSubmit.disabled = false;
            btnSubmit.textContent = 'Reintentar Guardado';
        }
    }

    async function cargarDesayunos() {
        try {
            const res = await fetch('http://localhost:5006/api/desayunos_calientes', {
                headers: { 'Authorization': `Bearer ${session.token}` }
            });
            
            if (!res.ok) throw new Error('Falló fetch');
            const data = await res.json();
            
            allRecords = data.desayunos || [];
            renderTabla(allRecords);

        } catch (error) {
            console.error('Error cargando desayunos calientes:', error);
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#e53e3e;">
                ⚠️ No se pudieron cargar los registros. El servidor backend podría estar apagado o en otro puerto.
            </td></tr>`;
        }
    }

    function renderTabla(registros) {
        tbody.innerHTML = '';
        if (registros.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b; padding:2rem;">El padrón de Desayunos Calientes está vacío.</td></tr>`;
            return;
        }

        registros.forEach(r => {
            const tr = document.createElement('tr');
            
            let badgeClass = 'status--pendiente';
            if (r.estatus === 'Activo' || r.estatus === 'Aprobado') badgeClass = 'status--activo';

            tr.innerHTML = `
                <td style="font-weight:600; color:var(--color-primary-dark)">${r.nombre_beneficiario}</td>
                <td style="font-family:monospace; color:#475569;">${r.curp}</td>
                <td>${r.escuela || 'No asignada'}</td>
                <td>${r.tutor}</td>
                <td><span class="status-badge ${badgeClass}">${r.estatus || 'Activo'}</span></td>
            `;

            tr.addEventListener('click', () => {
                currentSelectedId = r.id;
                document.getElementById('nombre_beneficiario').value = r.nombre_beneficiario;
                document.getElementById('curp').value = r.curp;
                document.getElementById('tutor').value = r.tutor;
                document.getElementById('direccion').value = "Extraída de App Móvil GPS"; 
                
                if(r.escuela !== 'Pendiente de Asignación') {
                    document.getElementById('escuela').value = r.escuela;
                } else {
                    document.getElementById('escuela').value = "";
                }
                
                btnSubmit.disabled = false;
                const actionBlock = document.getElementById('asignacionBloque');
                actionBlock.style.background = '#fef08a';
                setTimeout(() => actionBlock.style.background = '#fffff0', 800);
            });

            tbody.appendChild(tr);
        });
    }

    // Búsqueda y Filtrado en Tiempo Real
    inputSearch.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase();
        const filtrados = allRecords.filter(r => 
            r.nombre_beneficiario.toLowerCase().includes(query) || 
            r.curp.toLowerCase().includes(query) ||
            r.escuela.toLowerCase().includes(query)
        );
        renderTabla(filtrados);
    });
});
