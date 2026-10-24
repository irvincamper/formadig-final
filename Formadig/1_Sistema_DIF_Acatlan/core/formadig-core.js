// Core: Gestión de Autenticación y API para DIF Acatlán (FORMADIG)
const CORE_CONFIG = {
    SUPABASE_URL: "https://ctiqbycbkcftwuqgzxjb.supabase.co",
    SUPABASE_KEY: "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk",
    AUTH_BACKEND: "/api/auth"
};

const Auth = {
    // Validar si el usuario tiene una sesión activa
    checkSession: function () {
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
    logout: function () {
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
    getUser: function () {
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
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';

        const roleLabel = user && user.role ? user.role.toUpperCase() : '';
        const headerInner = `
            <div style="display:flex; align-items:center; gap:1rem;">
                <div class="header__logo">FORMADIG</div>
                ${title ? `<span style="font-size:0.85rem; color:rgba(255,255,255,0.7); border-left:1px solid rgba(255,255,255,0.2); padding-left:0.75rem; font-weight:500;">${title}</span>` : ''}
            </div>
            <div class="header__user-info">
                <span class="user-name">${user ? user.fullName : 'Bienvenido'}${roleLabel ? ` <span style="font-size:0.7rem; font-weight:700; opacity:0.85; background:rgba(255,255,255,0.18); padding:2px 8px; border-radius:999px; margin-left:6px; letter-spacing:0.04em;">${roleLabel}</span>` : ''}</span>
                <button onclick="Auth.logout()" class="btn-logout-small" title="Cerrar Sesión">
                    <span>Cerrar Sesión</span>
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="vertical-align:middle; margin-left:4px;"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>
                </button>
            </div>
        `;

        const headerEl = document.querySelector('header.header');
        if (headerEl) {
            headerEl.innerHTML = headerInner;
        } else if (typeof document !== 'undefined' && document.body) {
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

            const sidebarElement = document.getElementById('sidebarMenu');
            if (sidebarElement) {
                // Determinar si el dropdown debe estar abierto inicialmente
                const operativeModules = [
                    'admin_traslados', 'admin_desayunos_frios',
                    'admin_desayunos_calientes', 'admin_espacios_eaeyd',
                    'sms', 'chatbot', 'admin_psicologia', 'admin_dentista'
                ];
                const isOperativeActive = operativeModules.some(m => currentPath.includes(m));

                let menuHTML = `
                    <div class="sidebar-header">
                        <button class="btn-sidebar-toggle" onclick="UI.toggleSidebar()" title="Alternar menú">☰</button>
                        <div class="sidebar-logo-text">Menú Principal</div>
                    </div>
                    <nav class="sidebar-menu">
                        <a href="${basePath}dashboard.html" class="menu-item ${!isModule ? 'active' : ''}" title="Panel Central">
                            🏠 <span>Panel Central</span>
                        </a>

                        <div class="menu-item dropdown-toggle ${isOperativeActive ? 'is-open' : ''}" 
                             onclick="UI.toggleModules(this)" title="Módulos">
                            <div>📦 <span>Módulos</span></div>
                            <span class="dropdown-chevron">▼</span>
                        </div>
                        <div class="sidebar-dropdown-content ${isOperativeActive ? 'is-open' : ''}" id="modulesDropdown">
                            <div class="sidebar-section-label">Operación</div>
                            ${isAdmin || userRole.includes('traslado') ? `
                                <a href="${basePath}modulos/admin_traslados/vistas/admin_traslados.html" class="menu-item" title="Traslados">🚑 <span>Traslados</span></a>
                            ` : ''}
                            ${isAdmin || userRole.includes('desayuno') ? `
                                <a href="${basePath}modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html" class="menu-item" title="Fríos">🥛 <span>Fríos</span></a>
                                <a href="${basePath}modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html" class="menu-item" title="Calientes">🍲 <span>Calientes</span></a>
                                <a href="${basePath}modulos/admin_espacios_eaeyd/vistas/admin_espacios_eaeyd.html" class="menu-item" title="Espacios">🏢 <span>Espacios</span></a>
                            ` : ''}
                            
                            ${['admin', 'psicologo', 'dentista'].includes(userRole) ? `
                                <div class="sidebar-section-label">Atención clínica</div>
                                ${['admin', 'psicologo'].includes(userRole) ? `<a href="${basePath}modulos/admin_psicologia/vistas/admin_psicologia.html" class="menu-item ${currentPath.includes('psicologia') ? 'active' : ''}" title="Psicología">🧠 <span>Psicología</span></a>` : ''}
                                ${['admin', 'dentista'].includes(userRole) ? `<a href="${basePath}modulos/admin_dentista/vistas/admin_dentista.html" class="menu-item ${currentPath.includes('dentista') ? 'active' : ''}" title="Dentista">🦷 <span>Dentista</span></a>` : ''}
                            ` : ''}
                            <div class="sidebar-section-label">Soporte</div>
                            ${userRole !== 'admin_desayunos' ? `
                                <a href="${basePath}modulos/sms/vistas/admin_sms.html" class="menu-item" title="SMS">📱 <span>SMS</span></a>
                            ` : ''}
                            <a href="${basePath}modulos/chatbot/vistas/chatbot.html" class="menu-item" title="Chatbot">🤖 <span>Chatbot</span></a>
                        </div>
                `;

                // Sección Sistema: Usuarios y Mi Perfil
                menuHTML += `
                    <div class="sidebar-section-label">Sistema</div>
                    ${isAdmin ? `<a href="${basePath}modulos/admin_usuarios/vistas/admin_usuarios.html" class="menu-item ${currentPath.includes('admin_usuarios') ? 'active' : ''}" title="Usuarios">👤 <span>Usuarios</span></a>` : ''}
                    <a href="${basePath}modulos/perfil/vistas/admin_perfil.html" class="menu-item ${currentPath.includes('perfil') ? 'active' : ''}" title="Mi Perfil">⚙️ <span>Mi Perfil</span></a>
                `;

                menuHTML += `</nav>`;
                sidebarElement.innerHTML = menuHTML;

                // Aplicar estado inicial
                if (isCollapsed) {
                    sidebarElement.classList.add('collapsed');
                    const workspace = document.querySelector('.workspace');
                    if (workspace) workspace.classList.add('collapsed');
                }
            }
        }
    },

    // Alternar visibilidad (Modo Mini-Sidebar 70px)
    toggleSidebar: function () {
        const sidebar = document.getElementById('sidebarMenu');
        const workspace = document.querySelector('.workspace');
        if (sidebar) {
            const isNowCollapsed = sidebar.classList.toggle('collapsed');
            if (workspace) workspace.classList.toggle('collapsed');
            localStorage.setItem('sidebarCollapsed', isNowCollapsed);
        }
    },

    // Alternar visibilidad del menú de módulos (Accordion)
    toggleModules: function (button) {
        const content = document.getElementById('modulesDropdown');
        if (content) {
            content.classList.toggle('is-open');
            button.classList.toggle('is-open');
        }
    },

    // Mostrar mensaje de notificación
    notify: function (msg, type = 'success') {
        const box = typeof document !== 'undefined' ? document.getElementById('formMessage') : null;
        if (box) {
            box.textContent = msg;
            box.className = `message ${type}`;
            box.classList.remove('hidden');
            setTimeout(() => box.classList.add('hidden'), 5000);
        } else if (typeof window !== 'undefined' && typeof window.alert === 'function') {
            window.alert(msg);
        }
    },

    // Notificación flotante Toast
    toast: function (msg, type = 'success') {
        if (typeof document === 'undefined') return;
        let container = document.getElementById('globalToastContainer');
        if (!container && document.body) {
            container = document.createElement('div');
            container.id = 'globalToastContainer';
            container.style.cssText = 'position:fixed; top:24px; right:24px; z-index:99999; display:flex; flex-direction:column; gap:10px; max-width:380px; width:100%; pointer-events:none;';
            document.body.appendChild(container);
        }
        if (container) {
            const toast = document.createElement('div');
            toast.className = `message ${type}`;
            toast.style.cssText = 'pointer-events:auto; box-shadow:0 12px 30px rgba(0,0,0,0.18); margin:0; border-radius:10px; animation:fadeIn 0.25s ease-out;';
            toast.textContent = msg;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-10px)';
                toast.style.transition = 'all 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 4500);
        }
    }
};
