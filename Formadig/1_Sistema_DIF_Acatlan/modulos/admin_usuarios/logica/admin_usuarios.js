// ============================================================================
// FUNCIONES GLOBALES: Manejo del Modal
// ============================================================================

function toggleShowPassword(event) {
    event.preventDefault();
    
    const passwordInput = document.getElementById('password');
    const eyeOpenIcon = document.getElementById('eyeOpenIcon');
    const eyeClosedIcon = document.getElementById('eyeClosedIcon');
    
    if (!passwordInput) return;
    
    // Toggle entre password y text
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeOpenIcon.style.display = 'none';
        eyeClosedIcon.style.display = 'block';
    } else {
        passwordInput.type = 'password';
        eyeOpenIcon.style.display = 'block';
        eyeClosedIcon.style.display = 'none';
    }
    
    // Mantener el enfoque en el input
    passwordInput.focus();
}

function abrirModal() {
    const modal = document.getElementById('modalAgregarUsuario');
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Evitar scroll cuando el modal está abierto
    }
}

function cerrarModal(event) {
    // Si se hace clic en el overlay o en el botón X, cerrar
    if (event && event.target.id !== 'modalAgregarUsuario') {
        return;
    }
    
    const modal = document.getElementById('modalAgregarUsuario');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restaurar scroll
        
        // Limpiar los campos del formulario
        limpiarFormulario();
        
        // Limpiar mensajes
        const formMessage = document.getElementById('formMessage');
        if (formMessage) {
            formMessage.classList.add('hidden');
        }
    }
}

function limpiarFormulario() {
    const formulario = document.getElementById('agregar-usuario-form');
    if (formulario) {
        formulario.reset();
    }
    
    // Limpiar estilos de error
    limpiarEstilosError();
    
    // Limpiar valores específicos
    const campos = ['nombre_usuario', 'nombre_completo', 'email', 'password', 'rol', 'telefono', 'curp'];
    campos.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) {
            campo.value = '';
        }
    });
}

/**
 * Limpia todos los bordes rojos y mensajes de error del formulario
 */
function limpiarEstilosError() {
    const inputs = document.querySelectorAll('#agregar-usuario-form .form-control');
    const errorTexts = document.querySelectorAll('#agregar-usuario-form .error-text');
    
    inputs.forEach(input => {
        input.classList.remove('input-error');
    });
    
    errorTexts.forEach(text => {
        text.remove();
    });
}

/**
 * Muestra errores específicos en los campos del formulario
 * @param {Object} errors - Objeto con pares {campoId: mensaje}
 */
function mostrarErroresFormulario(errors) {
    if (!errors) return;
    
    Object.keys(errors).forEach(fieldId => {
        const campo = document.getElementById(fieldId);
        if (campo) {
            // Aplicar borde rojo
            campo.classList.add('input-error');
            
            // Insertar mensaje de error justo debajo
            const errorMsg = document.createElement('span');
            errorMsg.className = 'error-text';
            errorMsg.textContent = errors[fieldId];
            
            // Determinar punto de inserción: si es el password o similar con contenedor, insertar después del contenedor
            const container = campo.closest('div[style*="position: relative"]') || campo;
            
            // Evitar duplicados
            const parent = container.parentElement;
            const existingError = parent.querySelector('.error-text');
            if (existingError) existingError.remove();
            
            container.insertAdjacentElement('afterend', errorMsg);
        }
    });
}



document.addEventListener('DOMContentLoaded', () => {
    // 1. Verificar sesión y roles (Solo admin/directora/desarrollador)
    const session = Auth.checkSession();
    if (!session) return;

    const user = Auth.getUser();
    const isAdmin = ['admin', 'directora', 'desarrollador'].includes(user.role);

    if (!isAdmin) {
        alert('No tienes permisos para acceder a este módulo.');
        window.location.href = '../../../dashboard.html';
        return;
    }

    // 2. Inicializar Interfaz
    UI.setupHeader('Gestión de Usuarios - Administradores');

    // 3. Referencias DOM
    const usuariosList = document.getElementById('usuarios-tbody');
    const formulario = document.getElementById('agregar-usuario-form');
    const btnAgregar = document.getElementById('btnAgregar');
    const btnAñadirUsuario = document.getElementById('btnAñadirUsuario');
    const modalAgregarUsuario = document.getElementById('modalAgregarUsuario');
    const usuariosMessage = document.getElementById('usuariosMessage');
    const formMessage = document.getElementById('formMessage');

    // Constantes de seguridad
    const ALLOWED_ROLES = ['admin', 'admin_desayunos', 'admin_traslados'];
    const ROLE_LABELS = {
        'admin': 'Administrador General',
        'admin_desayunos': 'Admin Desayunos',
        'admin_traslados': 'Admin Traslados'
    };

    // ========================================================================
    // FUNCIÓN: Cargar Usuarios
    // ========================================================================
    async function cargarUsuarios() {
        try {
            const response = await fetch('/api/admin_usuarios', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }

            const data = await response.json();
            let usuarios = data.usuarios || [];

            // VALIDACIÓN CRÍTICA DE FRONTEND: Verificar que CADA usuario tenga rol permitido
            usuarios = usuarios.filter(u => {
                const tieneRolValido = ALLOWED_ROLES.includes(u.rol);
                if (!tieneRolValido) {
                    console.warn(`Filtrando usuario ${u.nombre_usuario}: rol "${u.rol}" no permitido`);
                }
                return tieneRolValido;
            });

            // Renderizar tabla
            renderizarUsuarios(usuarios);
            limpiarMensajeCarga();

        } catch (error) {
            console.error('Error al cargar usuarios:', error);
            usuariosList.innerHTML = `
                <tr><td colspan="6" class="empty-message">
                    ❌ Error al cargar administradores: ${error.message}
                </td></tr>
            `;
            mostrarMensaje(usuariosMessage, 'Error al cargar usuario', 'error');
        }
    }

    // ========================================================================
    // FUNCIÓN: Renderizar Usuarios en Tabla
    // ========================================================================
    function renderizarUsuarios(usuarios) {
        if (!usuarios || usuarios.length === 0) {
            usuariosList.innerHTML = `
                <tr><td colspan="6" class="empty-message">
                    No hay administradores registrados aún.
                </td></tr>
            `;
            return;
        }

        usuariosList.innerHTML = usuarios.map(u => `
            <tr>
                <td><strong>${escaparHTML(u.nombre_usuario)}</strong></td>
                <td>${escaparHTML(u.nombre_completo)} ${escaparHTML(u.apellidos || '')}</td>
                <td>
                    <span style="background: #dbeafe; color: #1e40af; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.85rem;">
                        ${ROLE_LABELS[u.rol] || u.rol}
                    </span>
                </td>
                <td>${escaparHTML(u.telefono || '—')}</td>
                <td>${formatearFecha(u.fecha_creacion)}</td>
                <td>
                    <button 
                        class="btn-delete" 
                        data-id="${u.id}" 
                        onclick="eliminarUsuario('${u.id}')">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    }

    // ========================================================================
    // FUNCIÓN: Alertar cuando se carga (remover después de cargar)
    // ========================================================================
    function limpiarMensajeCarga() {
        // Si no hay error, no mostrar nada
    }

    // ========================================================================
    // FUNCIÓN: Agregar Usuario
    // ========================================================================
    formulario.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // 1. Limpiar errores previos
        limpiarEstilosError();

        const nombre_usuario = document.getElementById('nombre_usuario').value.trim();
        const nombre_completo = document.getElementById('nombre_completo').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const rol = document.getElementById('rol').value;
        const telefono = document.getElementById('telefono').value.trim();
        const curp = document.getElementById('curp').value.trim();

        // (La validación robusta ahora la hace principalmente el Backend)
        
        btnAgregar.disabled = true;
        btnAgregar.textContent = 'Procesando...';

        try {
            const response = await fetch('/api/admin_usuarios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                },
                body: JSON.stringify({
                    nombre_usuario,
                    nombre_completo,
                    email,
                    password,
                    rol,
                    telefono,
                    curp
                })
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                mostrarMensaje(formMessage, 
                    `✅ Administrador "${nombre_completo}" creado exitosamente.`, 'success');
                formulario.reset();
                // Cerrar modal después de 1.5 segundos
                setTimeout(() => {
                    cerrarModal();
                    cargarUsuarios();
                }, 1500);
            } else {
                // Manejo de errores estructurados del backend
                if (result.errors) {
                    mostrarErroresFormulario(result.errors);
                    mostrarMensaje(formMessage, '❌ Revisa los campos marcados en rojo', 'error');
                } else {
                    const errorDelBackend = result.message || result.error || 'Error desconocido al crear usuario';
                    mostrarMensaje(formMessage, `❌ ${errorDelBackend}`, 'error');
                }
            }
        } catch (error) {
            console.error('Network error:', error);
            mostrarMensaje(formMessage, 
                '❌ No se pudo conectar con el servidor Backend.', 'error');
        } finally {
            btnAgregar.disabled = false;
            btnAgregar.textContent = '✓ Guardar';
        }
    });

    // Agregar listeners para limpiar error al escribir
    const formInputs = formulario.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('input-error');
            const errorMsg = this.parentElement.querySelector('.error-text');
            if (errorMsg) {
                errorMsg.remove();
            }
        });
    });


    // ========================================================================
    // EVENT LISTENER: Botón "Añadir Usuario" - Abre Modal
    // ========================================================================
    if (btnAñadirUsuario) {
        btnAñadirUsuario.addEventListener('click', (e) => {
            e.preventDefault();
            abrirModal();
        });
    }

    // ========================================================================
    // EVENT LISTENER: Cerrar Modal al hacer clic en el overlay
    // ========================================================================
    if (modalAgregarUsuario) {
        modalAgregarUsuario.addEventListener('click', cerrarModal);
    }

    // ========================================================================
    // FUNCIÓN: Eliminar Usuario (Global)
    // ========================================================================
    window.eliminarUsuario = async function(id) {
        if (!confirm('¿Estás seguro de que deseas eliminar este administrador? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/admin_usuarios/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                mostrarMensaje(usuariosMessage, '✅ Administrador eliminado exitosamente.', 'success');
                // Recargar tabla después de 1 segundo
                setTimeout(cargarUsuarios, 1000);
            } else {
                mostrarMensaje(usuariosMessage, `❌ Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Network error:', error);
            mostrarMensaje(usuariosMessage, 
                '❌ No se pudo conectar con el servidor Backend.', 'error');
        }
    };

    // ========================================================================
    // FUNCIÓN AUXILIAR: Formatear Fecha
    // ========================================================================
    function formatearFecha(fechaString) {
        if (!fechaString) return '—';
        try {
            const fecha = new Date(fechaString);
            const dia = String(fecha.getDate()).padStart(2, '0');
            const mes = String(fecha.getMonth() + 1).padStart(2, '0');
            const año = fecha.getFullYear();
            const horas = String(fecha.getHours()).padStart(2, '0');
            const minutos = String(fecha.getMinutes()).padStart(2, '0');
            return `${dia}/${mes}/${año} ${horas}:${minutos}`;
        } catch {
            return fechaString;
        }
    }

    // ========================================================================
    // FUNCIÓN AUXILIAR: Escapar HTML (Prevenir XSS)
    // ========================================================================
    function escaparHTML(texto) {
        if (!texto) return '';
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    // ========================================================================
    // FUNCIÓN AUXILIAR: Mostrar Mensajes
    // ========================================================================
    function mostrarMensaje(elemento, mensaje, tipo) {
        elemento.textContent = mensaje;
        elemento.className = `message ${tipo}`;
        elemento.classList.remove('hidden');
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            elemento.classList.add('hidden');
        }, 5000);
    }

    // ========================================================================
    // INICIALIZAR: Cargar usuarios al abrir la página
    // ========================================================================
    cargarUsuarios();
});

