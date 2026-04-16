// ========== INICIALIZAR SUPABASE CLIENTE ==========
let supabaseClient = null;

try {
    supabaseClient = supabase.createClient(
        'https://ctiqbycbkcftwuqgzxjb.supabase.co',
        'sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk'
    );
    console.log('✅ Cliente Supabase inicializado para Perfil');
} catch (error) {
    console.error('⚠️ Error inicializando Supabase:', error);
}

document.addEventListener('DOMContentLoaded', async () => {
    // 1. Verificación de sesión y UI Setup
    const session = Auth.checkSession();
    if (!session) return;
    
    UI.setupHeader('Mi Perfil');

    // 2. Referencias DOM
    const profileForm = document.getElementById('profileForm');
    const userEmailBadge = document.getElementById('userEmailBadge');
    const inputNombre = document.getElementById('nombre_completo');
    const inputTelefono = document.getElementById('telefono');
    const inputPassword = document.getElementById('password');
    const inputConfirmPassword = document.getElementById('confirm_password');
    const btnSave = document.getElementById('btnSave');
    const messageBox = document.getElementById('formMessage');

    const currentUser = Auth.getUser();
    if (currentUser && currentUser.email) {
        userEmailBadge.textContent = currentUser.email;
    }

    // 3. Cargar Datos del Perfil desde Supabase
    async function cargarDatosPerfil() {
        if (!supabaseClient) return;

        try {
            // Obtener el ID del usuario desde la sesión de Supabase
            const { data: { user }, error: userError } = await supabaseClient.auth.getUser();
            
            if (userError || !user) {
                console.error('Error obteniendo usuario de auth:', userError);
                return;
            }

            const userId = user.id;

            // Consultar tabla perfiles
            const { data, error } = await supabaseClient
                .table('perfiles')
                .select('nombre_completo, telefono')
                .eq('id', userId)
                .single();

            if (error) {
                console.warn('Aviso: No se encontró perfil en tabla perfiles:', error);
                // Fallback a metadata de la sesión local
                inputNombre.value = currentUser.fullName || '';
                return;
            }

            if (data) {
                inputNombre.value = data.nombre_completo || '';
                inputTelefono.value = data.telefono || '';
            }
        } catch (err) {
            console.error('Error cargando perfil:', err);
        }
    }

    await cargarDatosPerfil();

    // 4. Lógica de Guardado
    profileForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Limpiar mensajes
        messageBox.classList.add('hidden');
        messageBox.className = '';

        const nuevoNombre = inputNombre.value.trim();
        const nuevoTelefono = inputTelefono.value.trim();
        const pass = inputPassword.value;
        const confirmPass = inputConfirmPassword.value;

        // Validaciones
        if (!nuevoNombre) {
            mostrarMensaje('El nombre es obligatorio', 'error');
            return;
        }

        if (pass || confirmPass) {
            if (pass !== confirmPass) {
                mostrarMensaje('Las contraseñas no coinciden', 'error');
                return;
            }
            if (pass.length < 6) {
                mostrarMensaje('La contraseña debe tener al menos 6 caracteres', 'error');
                return;
            }
        }

        btnSave.disabled = true;
        btnSave.textContent = 'Guardando cambios...';

        try {
            const { data: { user } } = await supabaseClient.auth.getUser();
            const userId = user.id;

            // A. ACTUALIZAR TABLA PERFILES
            const { error: dbError } = await supabaseClient
                .table('perfiles')
                .update({
                    nombre_completo: nuevoNombre,
                    telefono: nuevoTelefono
                })
                .eq('id', userId);

            if (dbError) throw dbError;

            // B. ACTUALIZAR CONTRASEÑA EN AUTH (Si se ingresó)
            if (pass) {
                const { error: authError } = await supabaseClient.auth.updateUser({
                    password: pass
                });
                if (authError) throw authError;
            }

            // Actualizar localStorage para que el header se vea bien sin recargar
            localStorage.setItem('user_fullname', nuevoNombre);
            
            // Actualizar Header UI
            UI.setupHeader('Mi Perfil');

            mostrarMensaje('¡Perfil actualizado con éxito! ✅', 'success');
            inputPassword.value = '';
            inputConfirmPassword.value = '';

        } catch (error) {
            console.error('Error al guardar:', error);
            mostrarMensaje('Error al actualizar el perfil: ' + (error.message || error), 'error');
        } finally {
            btnSave.disabled = false;
            btnSave.textContent = '💾 Guardar Cambios';
        }
    });

    function mostrarMensaje(msg, type) {
        messageBox.textContent = msg;
        messageBox.className = `message ${type}`;
        messageBox.classList.remove('hidden');
        
        // Efecto scroll suave hacia el mensaje si es necesario
        messageBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});
