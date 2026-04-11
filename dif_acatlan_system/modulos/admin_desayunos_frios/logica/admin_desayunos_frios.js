document.addEventListener('DOMContentLoaded', () => {
    const session = Auth.checkSession();
    if (!session) return;
    
    // Configurar Header y Menú Inmediatamente
    UI.setupHeader('Gestión de Desayunos Fríos');

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
            nombre_beneficiario: "Mateo García López " + Math.floor(Math.random() * 100),
            curp: "GALM" + Math.floor(Math.random() * 999999) + "HDFRRM05",
            tutor: "Ana López Hernández",
            escuela: "Pendiente de Asignación",
            estatus: "Pendiente"
        };
        try {
            const res = await fetch('/api/desayunos_frios', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${session.token}` },
                body: JSON.stringify(dummyData)
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Error en el servidor');
            }

            UI.notify("Nueva solicitud recibida desde la App Móvil y agregada al Padrón.", "success");
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

        // Recolectar datos del dictamen
        const updateData = {
            escuela: document.getElementById('escuela').value.trim(),
            estatus: document.getElementById('estatus').value
        };

        if (!updateData.escuela) {
            UI.notify('Debes asignar una Escuela / Punto de Entrega.', 'error');
            return;
        }

        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Guardando Dictamen...';

        try {
            const res = await fetch(`/api/desayunos_frios/${currentSelectedId}`, {
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

            UI.notify('¡Dictamen registrado exitosamente y reflejado en el Padrón!', 'success');
            
            // Limpiar selección
            currentSelectedId = null;
            form.reset();
            document.getElementById('nombre_beneficiario').value = "";
            document.getElementById('curp').value = "";
            document.getElementById('tutor').value = "";
            document.getElementById('direccion').value = "";
            
            btnSubmit.disabled = true;
            btnSubmit.textContent = 'Guardar Dictamen y Registrar 🥛';

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
            const res = await fetch('/api/desayunos_frios', {
                headers: { 'Authorization': `Bearer ${session.token}` }
            });
            
            if (!res.ok) throw new Error('Falló fetch');
            const data = await res.json();
            
            allRecords = data.desayunos || [];
            renderTabla(allRecords);

        } catch (error) {
            console.error('Error cargando desayunos:', error);
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#e53e3e;">
                ⚠️ No se pudieron cargar los registros. El servidor backend podría estar apagado o en otro puerto.
            </td></tr>`;
        }
    }

    function renderTabla(registros) {
        tbody.innerHTML = '';
        if (registros.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b; padding:2rem;">El padrón de Desayunos Fríos está vacío.</td></tr>`;
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

            // Click evento para editar/aprobar
            tr.addEventListener('click', () => {
                // Solo cargar si está pendiente o quieres permitir re-edición
                currentSelectedId = r.id;
                
                // Rellenar panel izquierdo
                document.getElementById('nombre_beneficiario').value = r.nombre_beneficiario;
                document.getElementById('curp').value = r.curp;
                document.getElementById('tutor').value = r.tutor;
                document.getElementById('direccion').value = "Extraída de App Móvil GPS"; // Simulado
                
                if(r.escuela !== 'Pendiente de Asignación') {
                    document.getElementById('escuela').value = r.escuela;
                } else {
                    document.getElementById('escuela').value = "";
                }
                
                // Habilitar botón y animación
                btnSubmit.disabled = false;
                const actionBlock = document.getElementById('asignacionBloque');
                actionBlock.style.background = '#bee3f8';
                setTimeout(() => actionBlock.style.background = '#ebf8ff', 800);
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
