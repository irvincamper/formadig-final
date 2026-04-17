// sms.js — Lógica completa con reglas de negocio DIF Acatlán
const SMS = {
    get API_URL() { return `/api/sms`; },
    trasladosData: [],

    // ═══════════════════════════════════════════════════════════
    // INIT
    // ═══════════════════════════════════════════════════════════
    async init() {
        const user = Auth.getUser();
        if (user && user.role === 'admin_desayunos') {
            alert('Acceso Denegado: No tienes permisos para este módulo.');
            window.location.href = '../../../dashboard.html';
            return;
        }

        if (typeof UI !== 'undefined' && UI.setupHeader) {
            UI.setupHeader('Gestión de Notificaciones');
        }

        const isOnline = await this.checkServerStatus();
        if (isOnline) {
            await this.cargarHistorialSMS();
            await this.loadTraslados();
        }

        // ── Contador de caracteres + Vista previa en tiempo real ──
        const msgTextarea  = document.getElementById('messageText');
        const charCounter  = document.getElementById('charCount');
        const previewBubble = document.getElementById('previewBubble');

        if (msgTextarea) {
            const updateLive = () => {
                const len = msgTextarea.value.length;
                if (charCounter) {
                    charCounter.textContent = `${len}/160 caracteres`;
                    charCounter.classList.toggle('limit-reached', len > 160);
                }
                if (previewBubble) {
                    previewBubble.textContent = msgTextarea.value || 'El mensaje aparecerá aquí...';
                }
            };
            msgTextarea.addEventListener('input', updateLive);
        }

        // ── Selector de traslado → auto-llenado con plantilla DIF ──
        const selectInfo = document.getElementById('trasladoSelect');
        if (selectInfo) {
            selectInfo.addEventListener('change', (e) => {
                const val = e.target.value;
                if (!val) {
                    if (document.getElementById('targetPhone')) document.getElementById('targetPhone').value = '';
                    if (msgTextarea) { msgTextarea.value = ''; msgTextarea.dispatchEvent(new Event('input')); }
                    return;
                }

                // Buscar el objeto completo del traslado
                const t = this.trasladosData.find(x => String(x.id) === String(val));
                if (!t) return;

                // Autocompletar Teléfono
                const phoneInput = document.getElementById('targetPhone');
                if (phoneInput) {
                    phoneInput.value = t.telefono_principal || '';
                }

                // Autocompletar Mensaje (Plantilla corta solicitada)
                const traslado = t;
                const mensajeCorto = `DIF Acatlán: Hola ${traslado.paciente_nombre}, tiene traslado el ${traslado.fecha_viaje}. Responda SÍ para confirmar o NO para cancelar.`;

                if (msgTextarea) {
                    msgTextarea.value = mensajeCorto;
                    // Disparar evento input para actualizar contador y previsualización
                    msgTextarea.dispatchEvent(new Event('input'));
                }
            });
        }
    },

    // ═══════════════════════════════════════════════════════════
    // 1. CARGAR TRASLADOS (solo Aceptados y fechas futuras)
    //    El filtro real está en el backend; aquí igual filtramos
    //    por seguridad doble en el cliente.
    // ═══════════════════════════════════════════════════════════
    async loadTraslados() {
        try {
            const res = await fetch(`${this.API_URL}/traslados`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            // Guardar resultados en la variable global
            this.trasladosData = data;

            const select = document.getElementById('trasladoSelect');
            if (!select) return;

            // Limpiar el select con opción por defecto
            select.innerHTML = '<option value="">Seleccionar Paciente...</option>';

            if (this.trasladosData && this.trasladosData.length > 0) {
                this.trasladosData.forEach(t => {
                    const opt = document.createElement('option');
                    opt.value = t.id;
                    opt.textContent = `${t.paciente_nombre} - ${t.fecha_viaje}`;
                    select.appendChild(opt);
                });
            }
        } catch(e) {
            console.error('Error cargando traslados:', e);
        }
    },

    // ═══════════════════════════════════════════════════════════
    // 2. HISTORIAL EN TIEMPO REAL desde sms_logs
    // ═══════════════════════════════════════════════════════════
    async cargarHistorialSMS() {
        const table = document.getElementById('smsLogTable');
        const statEnviadosHoy = document.getElementById('statEnviadosHoy');

        if (!table) return;

        try {
            const response = await fetch(`${this.API_URL}/history`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            // ── Contador de hoy ──
            const hoyStr = new Date().toLocaleDateString('sv-SE'); // 'YYYY-MM-DD' local
            const enviadosHoy = (data || []).filter(log => {
                if (!log.fecha) return false;
                const logFecha = new Date(log.fecha).toLocaleDateString('sv-SE');
                return logFecha === hoyStr;
            }).length;

            if (statEnviadosHoy) statEnviadosHoy.innerText = enviadosHoy;

            if (data.length === 0) {
                table.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#64748b; padding: 20px;">No hay mensajes registrados aún.</td></tr>`;
                return;
            }

            // ── Render filas ──
            table.innerHTML = data.map(log => {
                const badgeClass   = (log.estatus || '').toLowerCase() === 'enviado' ? 'enviado' : 'error';
                const fechaStr     = log.fecha ? new Date(log.fecha).toLocaleString('es-MX') : '--';
                const mensajeCort  = (log.mensaje || '--').substring(0, 120) + ((log.mensaje || '').length > 120 ? '…' : '');
                return `
                <tr>
                    <td style="font-size:0.85rem; white-space:nowrap;">${fechaStr}</td>
                    <td style="font-family:monospace; font-size:0.85rem;">${log.telefono || '--'}</td>
                    <td style="max-width:260px; word-break:break-word; font-size:0.82rem; color:#475569;">${mensajeCort}</td>
                    <td><span class="status-tag ${badgeClass}">${log.estatus || '--'}</span></td>
                </tr>`;
            }).join('');

        } catch (error) {
            console.error('Error cargando historial SMS:', error);
            table.innerHTML = `<tr><td colspan="4" style="text-align:center; color:red; padding: 20px;">Error al conectar con el servidor de mensajes</td></tr>`;
            if (statEnviadosHoy) statEnviadosHoy.innerText = '—';
        }
    },

    // ═══════════════════════════════════════════════════════════
    // 3. ESTADO DEL SERVIDOR
    // ═══════════════════════════════════════════════════════════
    async checkServerStatus() {
        const statusIndicator = document.querySelector('.status-indicator');
        try {
            const res = await fetch(`${this.API_URL}/ping`, { mode: 'cors' });
            if (res.ok) {
                if (statusIndicator) {
                    statusIndicator.classList.add('connected');
                    statusIndicator.innerHTML = '<span class="pulse-dot"></span>Conectado';
                }
                return true;
            }
        } catch (e) {
            console.error('❌ SMS Backend Offline');
            if (statusIndicator) {
                statusIndicator.classList.remove('connected');
                statusIndicator.style.background = '#ffebee';
                statusIndicator.style.color = '#c62828';
                statusIndicator.innerHTML = 'Desconectado';
            }
        }
        return false;
    },

    // ═══════════════════════════════════════════════════════════
    // 4. ENVIAR SMS + REFRESCO AUTOMÁTICO
    // ═══════════════════════════════════════════════════════════
    async enviarSMS() {
        const phoneInput = document.getElementById('targetPhone');
        const textInput  = document.getElementById('messageText');
        const selectEl   = document.getElementById('trasladoSelect');

        if (!phoneInput || !textInput) {
            console.error('❌ Error: No se encontraron los campos del formulario en el DOM.');
            return;
        }

        const phone = (phoneInput.value || '').trim();
        const text  = (textInput.value  || '').trim();

        if (!phone || !text) {
            alert('Por favor completa el teléfono y el mensaje.');
            return;
        }

        const btn = document.querySelector('.sms-action-card .button');
        const originalText = btn ? btn.innerText : 'Enviar SMS';
        if (btn) { btn.disabled = true; btn.innerText = 'Enviando…'; }

        try {
            const response = await fetch(`${this.API_URL}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone:   phone,
                    message: text,
                    user_id: localStorage.getItem('user_email') || 'admin_dif'
                })
            });

            const result = await response.json();

            if (result.status === 'Enviado') {
                // ── Limpiar formulario ──
                phoneInput.value = '';
                textInput.value = ''; 
                textInput.dispatchEvent(new Event('input'));
                if (selectEl) selectEl.value = '';

                // ── Refresco automático del historial ──
                await this.cargarHistorialSMS();

                if (result.mode === 'Mock') {
                    alert(`✅ SMS enviado (Modo Simulación)`);
                } else {
                    alert(`✅ SMS enviado`);
                }
            } else {
                alert(`❌ Error: ${result.error || 'No se pudo enviar el mensaje'}`);
            }

        } catch (error) {
            console.error('Error enviando SMS:', error);
            alert('❌ No se pudo conectar con el servidor de SMS.');
        } finally {
            if (btn) { btn.disabled = false; btn.innerText = originalText; }
        }
    }

};

document.addEventListener('DOMContentLoaded', () => SMS.init());
