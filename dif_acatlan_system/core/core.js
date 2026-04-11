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
        
        // El header ahora es blanco con borde azul inferior (Estilo DIF Clásico)
        const headerHTML = `
            <div class="header">
                <div class="header__logo">FORMADIG</div>
                <div class="header__user-info">
                    <span class="user-name">${user ? user.fullName : 'Bienvenido'}</span>
                    <button onclick="Auth.logout()" class="btn-logout-small">Cerrar Sesión</button>
                </div>
            </div>
        `;
        
        const headerElement = document.querySelector('.header');
        if (headerElement) {
            headerElement.outerHTML = headerHTML;
        } else {
            // Si no existe, lo insertamos al principio del body
            document.body.insertAdjacentHTML('afterbegin', headerHTML);
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
                        <div class="sidebar-logo-text" style="font-size:1.2rem; margin-top:10px;">Menú Principal</div>
                    </div>
                    <div class="sidebar-menu">
                        <a href="${basePath}dashboard.html" class="menu-item ${!isModule ? 'active' : ''}">🏠 <span>Panel Central</span></a>
                `;

                if (isAdmin || isTraslado) {
                    menuHTML += `
                        <div style="padding: 15px 25px 5px; font-size: 0.75rem; color: #93c5fd; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Área Médica</div>
                        <a href="${basePath}modulos/admin_traslados/vistas/admin_traslados.html" class="menu-item ${currentPath.includes('admin_traslados') ? 'active' : ''}"><span>🚑</span> <span>Traslados Médicos</span></a>
                    `;
                }

                if (isAdmin || isDesayuno) {
                    menuHTML += `
                        <div style="padding: 15px 25px 5px; font-size: 0.75rem; color: #93c5fd; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Programas Alimentarios</div>
                        <a href="${basePath}modulos/admin_desayunos_frios/vistas/admin_desayunos_frios.html" class="menu-item ${currentPath.includes('admin_desayunos_frios') ? 'active' : ''}"><span>🥛</span> <span>Desayunos Fríos</span></a>
                        <a href="${basePath}modulos/admin_desayunos_calientes/vistas/admin_desayunos_calientes.html" class="menu-item ${currentPath.includes('admin_desayunos_calientes') ? 'active' : ''}"><span>🍲</span> <span>Desayunos Calientes</span></a>
                        
                        <div style="padding: 15px 25px 5px; font-size: 0.75rem; color: #93c5fd; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;">Desarrollo Integral</div>
                        <a href="${basePath}modulos/admin_espacios_eaeyd/vistas/admin_espacios_eaeyd.html" class="menu-item ${currentPath.includes('admin_espacios_eaeyd') ? 'active' : ''}"><span>🏢</span> <span>EAEyD</span></a>
                    `;
                }

                menuHTML += `</div>`;
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
