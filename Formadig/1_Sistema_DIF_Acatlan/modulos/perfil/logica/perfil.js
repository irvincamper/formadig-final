// ========== INICIALIZAR SUPABASE CLIENTE ==========
let supabaseClient = null;

try {
    supabaseClient = supabase.createClient(
        'https://ctiqbycbkcftwuqgzxjb.supabase.co',
        'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk'
    );
} catch (error) {
    console.error('⚠️ Error inicializando Supabase:', error);
}

// ========== FUNCIONES GLOBALES PARA MODALES ==========
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

    // 3. Cargar y Renderizar Perfil
    async function loadProfile() {
        if (!supabaseClient) return;

        try {
            const { data: { user } } = await supabaseClient.auth.getUser();
            if (!user) return;

            const { data, error } = await supabaseClient
                .table('perfiles')
                .select('*')
                .eq('id', user.id)
                .single();

            if (error) throw error;

            if (data) {
                // Actualizar UI de solo lectura
                displayNombre.textContent = data.nombre_completo || 'Usuario';
                displayRol.textContent = (data.rol || 'Miembro').replace('_', ' ');
                valNombre.textContent = data.nombre_completo || '—';
                valTelefono.textContent = data.telefono || 'Sin registrar';
                
                // Generar iniciales para avatar
                const initials = (data.nombre_completo || 'U')
                    .split(' ')
                    .map(n => n[0])
                    .slice(0, 2)
                    .join('');
                userAvatar.textContent = initials;

                // Preparar inputs de edición para cuando se abra el modal
                editNombreInput.value = data.nombre_completo || '';
                editTelefonoInput.value = data.telefono || '';

                // Actualizar localmente por si acaso el header usa estos datos
                localStorage.setItem('user_fullname', data.nombre_completo);
            }
        } catch (err) {
            console.error('Error cargando perfil:', err);
        }
    }

    await loadProfile();

    // 4. Listeners para Modales
    btnOpenEditData.addEventListener('click', () => openModal('modalData'));
    btnOpenEditPass.addEventListener('click', () => openModal('modalPass'));

    // Cierra modales al clickear fuera
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-overlay')) {
            closeModal(e.target.id);
        }
    });

    // 5. Guardar Datos Personales
    document.getElementById('formData').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const nuevoNombre = editNombreInput.value.trim();
        const nuevoTelefono = editTelefonoInput.value.trim();

        if (!nuevoNombre) return UI.notify('El nombre es obligatorio', 'error');

        btnSaveData.disabled = true;
        btnSaveData.textContent = 'Actualizando...';

        try {
            const { data: { user } } = await supabaseClient.auth.getUser();
            const { error } = await supabaseClient
                .table('perfiles')
                .update({
                    nombre_completo: nuevoNombre,
                    telefono: nuevoTelefono
                })
                .eq('id', user.id);

            if (error) throw error;

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

    // 6. Cambiar Contraseña
    document.getElementById('formPass').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const pass = newPassInput.value;
        const confirm = confirmPassInput.value;

        if (pass !== confirm) return UI.notify('Las contraseñas no coinciden', 'error');
        if (pass.length < 6) return UI.notify('La contraseña debe tener al menos 6 caracteres', 'error');

        btnSavePass.disabled = true;
        btnSavePass.textContent = 'Procesando...';

        try {
            const { error } = await supabaseClient.auth.updateUser({
                password: pass
            });

            if (error) throw error;

            UI.notify('Contraseña cambiada exitosamente 🔒');
            newPassInput.value = '';
            confirmPassInput.value = '';
            closeModal('modalPass');
        } catch (err) {
            UI.notify('Error de seguridad: ' + err.message, 'error');
        } finally {
            btnSavePass.disabled = false;
            btnSavePass.textContent = 'Actualizar Contraseña';
        }
    });
});
