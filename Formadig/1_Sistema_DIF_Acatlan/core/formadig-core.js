// Core: Gestión de Autenticación y API para DIF Acatlán (FORMADIG)
const CORE_CONFIG = {
    SUPABASE_URL: "https://ctiqbycbkcftwuqgzxjb.supabase.co",
    SUPABASE_KEY: "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk",
    AUTH_BACKEND: "/api/auth"
};

const Auth = {
    // Validar si el usuario tiene una sesión activa
    checkSession: function() {
        const token = localStorage.getItem('supabase_token');
        const role = localStorage.getItem('user_role');
        
        if (!token || !role) {
            console.warn("Sesión no válida. Redirigiendo a login...");
            this.logout();
            return false;
        }
        return { token, role };
    },

    // Cerrar sesión
    logout: function() {
        localStorage.clear();
        // Ajustar ruta según profundidad del módulo
        const currentPath = window.location.pathname;
        if (currentPath.includes('/modulos/')) {
            window.location.href = '../../login/vistas/login.html';
        } else {
            window.location.href = 'modulos/login/vistas/login.html';
        }
    },

    // Obtener información del usuario actual
    getUser: function() {
        return {
            email: localStorage.getItem('user_email'),
            role: localStorage.getItem('user_role'),
            fullName: localStorage.getItem('user_fullname') || 'Usuario DIF'
        };
    }
};

UI = {
    // Generar el Header común para todos los módulos
    setupHeader: (title) => {
        const user = Auth.getUser();

        const headerEl = document.querySelector('header.header');
        if (headerEl) {
            headerEl.innerHTML = `
                <div class="header__logo">FORMADIG</div>
                <div class="header__user-info">
                    <span class="user-name">${user ? user.fullName : 'Bienvenido'}</span>
                    <button onclick="Auth.logout()" class="btn-logout-small">Cerrar Sesión</button>
                </div>
            `;
        } else {
            document.body.insertAdjacentHTML('afterbegin', `
                <header class="header">
                    <div class="header__logo">FORMADIG</div>
                    <div class="header__user-info">
                        <span class="user-name">${user ? user.fullName : 'Bienvenido'}</span>
                        <button onclick="Auth.logout()" class="btn-logout-small">Cerrar Sesión</button>
                    </div>
                </header>
            `);
        }

        // --- Renderizar Sidebar Dinámico ---
        const currentPath = window.location.pathname;
        if (!currentPath.includes('/login/')) {
            const isModule = currentPath.includes('/modulos/');
            const basePath = isModule ? '../../../' : '';

            const userObj = Auth.getUser();
            const userRole = userObj ? (userObj.role || '') : '';
            const isAdmin = ['directora', 'admin', 'desarrollador'].includes(userRole);
            const isTraslado = userRole.includes('traslado');
            const isDesayuno = userRole.includes('desayuno');

            const sidebarElement = document.getElementById('sidebarMenu');
            if (sidebarElement) {
                let menuHTML = `
                    <div class="sidebar-header">
                        <div class="sidebar-logo-text">Menú Principal</div>
                    </div>
                    <nav class="sidebar-menu">
                        <a href="${basePath}dashboard.html" class="menu-item ${!isModule ? 'active' : ''}">
                            🏠 <span>Panel Central</span>
                        </a>
                `;

                // 1. Área Médica (Traslados)
                if (isAdmin || isTraslado) {
                    menuHTML += `
                        <div class="sidebar-section-label">Área Médica</div>
                        <a href="${basePath}modulos/admin_traslados/vistas/admin_traslados.html"
                           class="menu-item ${currentPath.includes('admin_traslados') ? 'active' : ''}">
                            🚑 <span>Traslados Médicos</span>
                        </a>
                    `;
                }

                // 2. Programas Alimentarios y Desarrollo Integral (Agrupados dinámicamente)
                let alimentosMenu = '';
                
                if (isAdmin || isDesayuno) {
                    alimentosMenu += `
                        <a href="${basePath}modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html"
                           class="menu-item ${currentPath.includes('admin_desayunos_frios') ? 'active' : ''}">
                            🥛 <span>Gestión Fríos</span>
                        </a>
                        <a href="${basePath}modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html"
                           class="menu-item ${currentPath.includes('admin_desayunos_calientes') ? 'active' : ''}">
                            🍲 <span>Gestión Calientes</span>
                        </a>
                        <a href="${basePath}modulos/admin_espacios_eaeyd/vistas/admin_espacios_eaeyd.html"
                           class="menu-item ${currentPath.includes('admin_espacios_eaeyd') ? 'active' : ''}">
                            🏢 <span>Espacios EAEyD</span>
                        </a>
                    `;
                }

                if (alimentosMenu !== '') {
                    menuHTML += `
                        <div class="sidebar-section-label">Programas y Desarrollo</div>
                        ${alimentosMenu}
                    `;
                }

                // 4. Sección Universal de Apoyo (Al final)
                menuHTML += `
                    <div class="sidebar-section-label">Asistencia y Soporte</div>
                `;

                // Restricción: admin_desayunos no tiene SMS
                if (userRole !== 'admin_desayunos') {
                    menuHTML += `
                        <a href="${basePath}modulos/sms/vistas/admin_sms.html"
                           class="menu-item ${currentPath.includes('sms') ? 'active' : ''}">
                            📱 <span>Mensajes SMS</span>
                        </a>
                    `;
                }

                menuHTML += `
                    <a href="${basePath}modulos/chatbot/vistas/chatbot.html"
                       class="menu-item ${currentPath.includes('chatbot') ? 'active' : ''}">
                        🤖 <span>Chatbot Asistente</span>
                    </a>
                `;

                // 5. Configuración y Usuarios (Solo Admin)
                if (isAdmin) {
                    menuHTML += `
                        <div class="sidebar-section-label">Sistema y Seguridad</div>
                        <a href="${basePath}modulos/admin_usuarios/vistas/admin_usuarios.html"
                           class="menu-item ${currentPath.includes('admin_usuarios') ? 'active' : ''}">
                            👤 <span>Gestión Usuarios</span>
                        </a>
                    `;
                }

                menuHTML += `</nav>`;
                sidebarElement.innerHTML = menuHTML;
            }
        }
    },

    // Mostrar mensaje de notificación
    notify: function(msg, type = 'success') {
        const box = document.getElementById('formMessage');
        if (box) {
            box.textContent = msg;
            box.className = `message ${type}`;
            box.classList.remove('hidden');
            setTimeout(() => box.classList.add('hidden'), 5000);
        } else {
            alert(msg);
        }
    }
};

// Exportar si es necesario (para módulos que usen import/export)
// export { Auth, UI, CORE_CONFIG };
