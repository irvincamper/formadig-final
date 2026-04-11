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
    UI.setupHeader('Gestión de Usuarios');

    const registerForm = document.getElementById('registerForm');
    const messageBox = document.getElementById('formMessage');
    const btnRegister = document.getElementById('btnRegister');

    // 3. Manejar Registro de Usuario
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('regEmail').value;
        const fullName = document.getElementById('regFullName').value;
        const password = document.getElementById('regPassword').value;
        const role = document.getElementById('regRole').value;
        
        btnRegister.disabled = true;
        btnRegister.textContent = 'Procesando...';
        hideMessage();

        try {
            const response = await fetch('http://localhost:5001/api/auth/register', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.token}` 
                },
                body: JSON.stringify({ email, password, role, full_name: fullName })
            });

            const data = await response.json();

            if (response.ok) {
                showMessage(`✅ Usuario "${fullName}" creado exitosamente con el rol: ${role}.`, 'success');
                registerForm.reset();
            } else {
                showMessage(`❌ Error: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Network Error:', error);
            showMessage('❌ No se pudo conectar con el servidor Backend.', 'error');
        } finally {
            btnRegister.disabled = false;
            btnRegister.textContent = 'Registrar Nuevo Usuario';
        }
    });

    // Helpers UI
    function showMessage(msg, type) {
        messageBox.textContent = msg;
        messageBox.className = `message ${type}`;
        messageBox.classList.remove('hidden');
    }

    function hideMessage() {
        messageBox.classList.add('hidden');
    }
});
