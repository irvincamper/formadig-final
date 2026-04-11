document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const messageBox = document.getElementById('formMessage');

    const btnLogin = document.getElementById('btnLogin');
    const btnRegister = document.getElementById('btnRegister');

    // Mapeo de roles a carpetas (mantener UX original, adaptar rutas a la estructura real)
    const roleToFolder = {
        'admin_traslados': 'admin_traslados',
        'usuario_traslados': 'admin_traslados',
        'admin_desayunos': 'admin_desayunos_frios',
        'usuario_desayunos': 'admin_desayunos_frios'
    };

    // Mover entre formularios
    window.toggleView = function() {
        document.getElementById('loginBox').classList.toggle('hidden');
        document.getElementById('registerBox').classList.toggle('hidden');
        messageBox.className = 'message hidden'; // Clear errors
    };

    // --- ACCIÓN DE INICIO DE SESIÓN ---
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        btnLogin.disabled = true;
        btnLogin.textContent = 'Autenticando...';

        try {
            const response = await fetch('http://localhost:5001/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage(`✅ Bienvenid@. Accediendo al sistema...`, 'success');
                
                // Guardar la sesión completa en LocalStorage
                localStorage.setItem('supabase_token', data.session.access_token);
                localStorage.setItem('user_role', data.role);
                localStorage.setItem('user_email', email);
                // Nombre completo (viene del perfil si está disponible)
                if (data.nombre_completo) {
                    localStorage.setItem('user_fullname', data.nombre_completo);
                }

                // Todos los roles van al Dashboard central que muestra los módulos correspondientes
                setTimeout(() => {
                    if (data.role) {
                        window.location.href = '../../../dashboard.html';
                    } else {
                        showMessage('⚠️ Usuario autorizado pero sin rol asignado. Contacta al administrador.', 'error');
                        btnLogin.disabled = false;
                        btnLogin.textContent = 'Ingresar al Sistema';
                    }
                }, 1200);

            } else {
                showMessage(`❌ Error: ${data.error}`, 'error');
                btnLogin.disabled = false;
                btnLogin.textContent = 'Ingresar al Sistema';
            }
        } catch (error) {
            console.error('Network Error:', error);
            showMessage('❌ No se pudo conectar con el servidor Backend (Puerto 5001 apagado).', 'error');
            btnLogin.disabled = false;
            btnLogin.textContent = 'Ingresar al Sistema';
        }
    });

    // --- ACCIÓN DE CREAR USUARIO ---
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('regEmail').value;
        const fullName = document.getElementById('regFullName')?.value || '';
        const password = document.getElementById('regPassword').value;
        const role = document.getElementById('regRole').value;
        
        btnRegister.disabled = true;
        btnRegister.textContent = 'Creando en Supabase...';

        try {
            const response = await fetch('http://localhost:5001/api/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, role, full_name: fullName })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage(`✅ Usuario creado exitosamente con rol: ${role}. Ahora inicia sesión.`, 'success');
                registerForm.reset();
                setTimeout(() => toggleView(), 2000); // Volver al inicio de sesión
            } else {
                showMessage(`❌ Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Network Error:', error);
            showMessage('❌ No se pudo conectar con el servidor Backend.', 'error');
        } finally {
            btnRegister.disabled = false;
            btnRegister.textContent = 'Registrar y Asignar Rol';
        }
    });

    // Helper message UI
    function showMessage(msg, type) {
        messageBox.textContent = msg;
        messageBox.className = `message ${type}`;
    }
});
