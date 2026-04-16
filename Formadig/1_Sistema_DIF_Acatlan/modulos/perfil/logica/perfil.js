// ========== PERFIL.JS — REFACTORIZADO PARA BACKEND ==========

// ═══════════════════════════════════════════════════════════
// FUNCIONES GLOBALES PARA MODALES
// ═══════════════════════════════════════════════════════════
function openModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verificación de sesión
    const sessionToken = Auth.checkSession();
    if (!sessionToken) return;
    
    UI.setupHeader('Mi Perfil');

    // 2. Referencias DOM (Display)
    const displayNombre = document.getElementById('displayNombre');
    const displayRol = document.getElementById('displayRol');
    const valNombre = document.getElementById('valNombre');
    const valTelefono = document.getElementById('valTelefono');
    const userAvatar = document.getElementById('userAvatar');

    // Referencias DOM (Modales/Forms)
    const editNombreInput = document.getElementById('editNombre');
    const editTelefonoInput = document.getElementById('editTelefono');
    const newPassInput = document.getElementById('newPass');
    const confirmPassInput = document.getElementById('confirmPass');

    // Botones
    const btnOpenEditData = document.getElementById('btnOpenEditData');
    const btnOpenEditPass = document.getElementById('btnOpenEditPass');
    const btnSaveData = document.getElementById('btnSaveData');
    const btnSavePass = document.getElementById('btnSavePass');

    // 3. CARGAR PERFIL DESDE EL BACKEND
    async function loadProfile() {
        try {
            console.log("🔄 Cargando perfil desde backend...");
            const response = await fetch('/api/perfil', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${sessionToken.token}`
                }
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            console.log("✅ Datos de perfil cargados:", data);

            if (data) {
                // Actualizar UI de solo lectura
                displayNombre.textContent = data.nombre_completo || 'Usuario';
                displayRol.textContent = (data.rol || 'Miembro').replace(/_/g, ' ');
                valNombre.textContent = data.nombre_completo || '—';
                valTelefono.textContent = data.telefono || 'Sin registrar';
                
                // Generar iniciales para avatar
                const initials = (data.nombre_completo || 'U')
                    .split(' ')
                    .map(n => n[0])
                    .slice(0, 2)
                    .join('');
                userAvatar.textContent = initials;

                // Preparar inputs de edición
                editNombreInput.value = data.nombre_completo || '';
                editTelefonoInput.value = data.telefono || '';

                // Sincronizar localmente para el header
                localStorage.setItem('user_fullname', data.nombre_completo);
            }
        } catch (err) {
            console.error('❌ Error cargando perfil:', err);
            displayNombre.textContent = "Error al cargar";
            valNombre.textContent = "Revisa tu conexión o sesión";
            UI.notify('No se pudo cargar la información del perfil', 'error');
        }
    }

    await loadProfile();

    // 4. Listeners para Modales
    if (btnOpenEditData) btnOpenEditData.addEventListener('click', () => openModal('modalData'));
    if (btnOpenEditPass) btnOpenEditPass.addEventListener('click', () => openModal('modalPass'));

    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) closeModal(e.target.id);
    });

    // 5. GUARDAR DATOS PERSONALES (Hacia Backend)
    document.getElementById('formData').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nuevoNombre = editNombreInput.value.trim();
        const nuevoTelefono = editTelefonoInput.value.trim();

        if (!nuevoNombre) return UI.notify('El nombre es obligatorio', 'error');

        btnSaveData.disabled = true;
        btnSaveData.textContent = 'Actualizando...';

        try {
            const res = await fetch('/api/perfil', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionToken.token}`
                },
                body: JSON.stringify({
                    nombre_completo: nuevoNombre,
                    telefono: nuevoTelefono
                })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Error desconocido');
            }

            UI.notify('¡Datos actualizados correctamente! ✅');
            await loadProfile();
            closeModal('modalData');
            
            // Refrescar Header para ver el nuevo nombre arriba
            UI.setupHeader('Mi Perfil');
        } catch (err) {
            UI.notify('Error al actualizar: ' + err.message, 'error');
        } finally {
            btnSaveData.disabled = false;
            btnSaveData.textContent = 'Guardar Cambios';
        }
    });

    // 6. CAMBIAR CONTRASEÑA (Hacia Backend)
    document.getElementById('formPass').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const pass = newPassInput.value;
        const confirm = confirmPassInput.value;

        if (pass !== confirm) return UI.notify('Las contraseñas no coinciden', 'error');
        if (pass.length < 6) return UI.notify('Mínimo 6 caracteres', 'error');

        btnSavePass.disabled = true;
        btnSavePass.textContent = 'Procesando...';

        try {
            const res = await fetch('/api/perfil/password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionToken.token}`
                },
                body: JSON.stringify({ password: pass })
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.error || 'Error de seguridad');
            }

            UI.notify('Contraseña cambiada exitosamente 🔒');
            newPassInput.value = '';
            confirmPassInput.value = '';
            closeModal('modalPass');
        } catch (err) {
            UI.notify(err.message, 'error');
        } finally {
            btnSavePass.disabled = false;
            btnSavePass.textContent = 'Actualizar Contraseña';
        }
    });
});
