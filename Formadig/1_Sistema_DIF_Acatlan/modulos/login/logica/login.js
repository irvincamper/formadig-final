document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const messageBox = document.getElementById('formMessage');

    const btnLogin = document.getElementById('btnLogin');
    const passwordInput = document.getElementById('loginPassword');
    const togglePasswordBtn = document.getElementById('togglePassword');

    // Mapeo de roles a carpetas (mantener UX original, adaptar rutas a la estructura real)
    const roleToFolder = {
        'admin_traslados': 'admin_traslados',
        'usuario_traslados': 'admin_traslados',
        'admin_desayunos': 'admin_desayunos_frios',
        'usuario_desayunos': 'admin_desayunos_frios'
    };

    /* window.toggleView eliminada: El registro ahora es un módulo interno para el Director */

    // --- LÓGICA DE MOSTRAR CONTRASEÑA ---
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Alternar entre iconos SVG (Eye / Eye-off)
            if (type === 'password') {
                togglePasswordBtn.innerHTML = `
                    <svg id="eyeIcon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                    </svg>`;
            } else {
                togglePasswordBtn.innerHTML = `
                    <svg id="eyeIcon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye-off">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                        <line x1="1" y1="1" x2="23" y2="23"></line>
                    </svg>`;
            }
        });
    }

    // --- ACCIÓN DE INICIO DE SESIÓN ---
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        btnLogin.disabled = true;
        btnLogin.textContent = 'Autenticando...';

        try {
            const response = await fetch('/api/auth/login', {
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
            showMessage('❌ No se pudo conectar con el servidor Backend. Verifica la conexión.', 'error');
            btnLogin.disabled = false;
            btnLogin.textContent = 'Ingresar al Sistema';
        }
    });


    // Helper message UI
    function showMessage(msg, type) {
        messageBox.textContent = msg;
        messageBox.className = `message ${type}`;
    }
});
