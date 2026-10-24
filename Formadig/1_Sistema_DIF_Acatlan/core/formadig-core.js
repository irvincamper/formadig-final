// Core: Gestión de Autenticación y API para DIF Acatlán (FORMADIG)
const CORE_CONFIG = {
    SUPABASE_URL: "https://ctiqbycbkcftwuqgzxjb.supabase.co",
    SUPABASE_KEY: "sb_publishable_VkOge6lzgO3Yh37jjW3P4Q_KA4HUeWk",
    AUTH_BACKEND: "/api/auth"
};

const Auth = {
    // Sólo la respuesta verificada del servidor determina la sesión vigente.
    verifySession: async function () {
        const token = localStorage.getItem('supabase_token');
        if (!token) { await this.logout(); return false; }
        try {
            const response = await fetch('/api/auth/me', {headers: {Authorization: 'Bearer ' + token}, cache: 'no-store'});
            if (response.status === 401 || response.status === 403) { await this.logout(); return false; }
            if (!response.ok) return false;
            const data = await response.json();
            if (!['admin', 'admin_traslados', 'admin_desayunos', 'psicologo', 'dentista'].includes(data.role)) {
                await this.logout(); return false;
            }
            const changed = localStorage.getItem('user_role') !== data.role;
            localStorage.setItem('user_role', data.role);
            localStorage.setItem('user_fullname', data.nombre_completo || 'Usuario DIF');
            if (changed) window.location.reload();
            return true;
        } catch (_) { return false; }
    },
    fetch: function (input, options = {}) {
        const url = new URL(input, window.location.href);
        const headers = new Headers(options.headers || {});
        if (url.origin === window.location.origin && url.pathname.startsWith('/api/')) {
            const token = localStorage.getItem('supabase_token');
            if (token) headers.set('Authorization', 'Bearer ' + token);
        }
        return fetch(input, {...options, headers});
    },
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
    logout: async function () {
        const token = localStorage.getItem('supabase_token');
        localStorage.clear();
        if (token) {
            try {
                await fetch('/api/auth/logout', {method: 'POST', headers: {Authorization: 'Bearer ' + token}, cache: 'no-store'});
            } catch (_) { /* El navegador siempre elimina la sesión local. */ }
        }
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

        const headerInner = `
            <div style="display:flex; align-items:center;">
                <div class="header__logo">FORMADIG</div>
            </div>
            <div class="header__user-info">
                <span class="user-name">${String(user ? user.fullName : 'Bienvenido').replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]))}</span>
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
                                ${['admin', 'psicologo'].includes(userRole) ? `<a href="${basePath}modulos/admin_psicologia/vistas/admin_psicologia.html" class="menu-item">Psicología</a>` : ''}
                                ${['admin', 'dentista'].includes(userRole) ? `<a href="${basePath}modulos/admin_dentista/vistas/admin_dentista.html" class="menu-item">Dentista</a>` : ''}
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


// La página estática no es una barrera de seguridad: cada API verifica su JWT.
if (typeof document.addEventListener === 'function') {
    document.addEventListener('DOMContentLoaded', async () => {
        if (!window.location.pathname.includes('/login/')) {
            const valid = await Auth.verifySession();
            if (!valid && localStorage.getItem('supabase_token')) {
                const status = document.getElementById('status') || document.getElementById('formMessage');
                if (status) status.textContent = 'No se pudo verificar la sesión. Intenta nuevamente.';
            }
        }
    });
}
