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
        const isHidden = localStorage.getItem('sidebarHidden') === 'true';

        // Botón de Rescate (solo visible cuando el menú está oculto)
        const headerInner = `
            <div style="display:flex; align-items:center;">
                <button class="btn-sidebar-toggle btn-header-rescue" id="btnHeaderToggle" onclick="UI.toggleSidebar()" title="Mostrar menú lateral">☰</button>
                <div class="header__logo">FORMADIG</div>
            </div>
            <div class="header__user-info">
                <span class="user-name">${user ? user.fullName : 'Bienvenido'}</span>
                <button onclick="Auth.logout()" class="btn-logout-small">Cerrar Sesión</button>
            </div>
        `;

        const headerEl = document.querySelector('header.header');
        if (headerEl) {
            headerEl.innerHTML = headerInner;
        } else {
            document.body.insertAdjacentHTML('afterbegin', `
                <header class="header">${headerInner}</header>
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
                // Determinar si el dropdown debe estar abierto inicialmente
                const operativeModules = [
                    'admin_traslados', 'admin_desayunos_frios', 
                    'admin_desayunos_calientes', 'admin_espacios_eaeyd', 
                    'sms', 'chatbot'
                ];
                const isOperativeActive = operativeModules.some(m => currentPath.includes(m));

                let menuHTML = `
                    <div class="sidebar-header">
                        <button class="btn-sidebar-toggle" onclick="UI.toggleSidebar()" title="Ocultar menú">☰</button>
                        <div class="sidebar-logo-text">Menú Principal</div>
                    </div>
                    <nav class="sidebar-menu">
                        <a href="${basePath}dashboard.html" class="menu-item ${!isModule ? 'active' : ''}">
                            🏠 <span>Panel Central</span>
                        </a>

                        <!-- Botón Dropdown Módulos -->
                        <div class="menu-item dropdown-toggle ${isOperativeActive ? 'is-open' : ''}" 
                             onclick="UI.toggleModules(this)">
                            <div>📦 <span>Módulos</span></div>
                            <span class="dropdown-chevron">▼</span>
                        </div>

                        <div class="sidebar-dropdown-content ${isOperativeActive ? 'is-open' : ''}" id="modulesDropdown">
                `;

                // ... (el resto del menuHTML se mantiene igual)
                if (isAdmin || isTraslado) {
                    menuHTML += `
                        <div class="sidebar-section-label">Área Médica</div>
                        <a href="${basePath}modulos/admin_traslados/vistas/admin_traslados.html"
                           class="menu-item ${currentPath.includes('admin_traslados') ? 'active' : ''}" title="Traslados Médicos">
                            🚑 <span>Traslados Médicos</span>
                        </a>
                    `;
                }
                if (isAdmin || isDesayuno) {
                    menuHTML += `
                        <div class="sidebar-section-label">Programas y Desarrollo</div>
                        <a href="${basePath}modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html"
                           class="menu-item ${currentPath.includes('admin_desayunos_frios') ? 'active' : ''}">🥛 <span>Gestión Fríos</span></a>
                        <a href="${basePath}modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html"
                           class="menu-item ${currentPath.includes('admin_desayunos_calientes') ? 'active' : ''}">🍲 <span>Gestión Calientes</span></a>
                        <a href="${basePath}modulos/admin_espacios_eaeyd/vistas/admin_espacios_eaeyd.html"
                           class="menu-item ${currentPath.includes('admin_espacios_eaeyd') ? 'active' : ''}">🏢 <span>Espacios EAEyD</span></a>
                    `;
                }

                menuHTML += `
                    <div class="sidebar-section-label">Asistencia y Soporte</div>
                    <a href="${basePath}modulos/sms/vistas/admin_sms.html" class="menu-item">📱 <span>SMS</span></a>
                    <a href="${basePath}modulos/chatbot/vistas/chatbot.html" class="menu-item">🤖 <span>Chatbot</span></a>
                `;

                if (isAdmin) {
                    menuHTML += `
                        <div class="sidebar-section-label">Sistema</div>
                        <a href="${basePath}modulos/admin_usuarios/vistas/admin_usuarios.html" class="menu-item">👤 <span>Usuarios</span></a>
                    `;
                }

                menuHTML += `
                        </div>
                    </nav>`;
                
                sidebarElement.innerHTML = menuHTML;

                // Aplicar estado inicial
                if (isHidden) {
                    sidebarElement.classList.add('hidden');
                    document.body.classList.add('sidebar-is-hidden');
                    const workspace = document.querySelector('.workspace');
                    if (workspace) workspace.classList.add('full-width');
                } else {
                    document.body.classList.remove('sidebar-is-hidden');
                }
            }
        }
    },

    // Alternar visibilidad de la barra lateral (Ocultar por completo)
    toggleSidebar: function() {
        const sidebar = document.getElementById('sidebarMenu');
        const workspace = document.querySelector('.workspace');
        if (sidebar) {
            const isNowHidden = sidebar.classList.toggle('hidden');
            
            if (isNowHidden) {
                document.body.classList.add('sidebar-is-hidden');
                if (workspace) workspace.classList.add('full-width');
            } else {
                document.body.classList.remove('sidebar-is-hidden');
                if (workspace) workspace.classList.remove('full-width');
            }
            
            localStorage.setItem('sidebarHidden', isNowHidden);
        }
    },

    // Alternar visibilidad del menú de módulos (Accordion)
    toggleModules: function(button) {
        const content = document.getElementById('modulesDropdown');
        if (content) {
            content.classList.toggle('is-open');
            button.classList.toggle('is-open');
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
