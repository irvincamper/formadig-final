// sms.js — Lógica completa con reglas de negocio DIF Acatlán
const SMS = {
    get API_URL() { return `/api/sms`; },
    trasladosData: [],

    // ═══════════════════════════════════════════════════════════
    // INIT
    // ═══════════════════════════════════════════════════════════
    async init() {
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
                    document.getElementById('targetPhone').value = '';
                    if (msgTextarea) { msgTextarea.value = ''; msgTextarea.dispatchEvent(new Event('input')); }
                    return;
                }

                const t = this.trasladosData.find(x => x.id == val);
                if (!t) return;

                // ── Teléfono con prefijo +52 ──
                let phone = t.telefono_principal || t.telefono_secundario || '';
                if (phone && !phone.startsWith('+')) {
                    phone = '+52' + phone.replace(/\D/g, '').slice(-10);
                }
                document.getElementById('targetPhone').value = phone;

                // ── Nombre ──
                const name = `${t.paciente_nombre || ''} ${t.paciente_apellidos || ''}`.trim() || 'Beneficiario';

                // ── Fecha formateada ──
                let fecha = t.fecha_viaje || 'la fecha indicada';
                if (t.fecha_viaje) {
                    try {
                        // fecha_viaje puede ser 'YYYY-MM-DD'; parsear como local para evitar desfase UTC
                        const [y, m, d] = t.fecha_viaje.split('-');
                        const dateObj = new Date(Number(y), Number(m) - 1, Number(d));
                        if (!isNaN(dateObj)) {
                            fecha = dateObj.toLocaleDateString('es-MX', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
                        }
                    } catch(e){}
                }

                // ── Destino ──
                const destino = t.destino_hospital || 'el hospital asignado';

                // ── Plantilla EXACTA requerida por el DIF ──
                const msg = `Este mensaje es por parte del DIF de acatlan, usted ${name} solicitud ir ${destino} el dia ${fecha} confirma usted su asistencia Si o No (solo responda con una de esas dos opciones)`;

                if (msgTextarea) {
                    msgTextarea.value = msg;
                    msgTextarea.dispatchEvent(new Event('input')); // dispara contador + preview
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

            // Doble filtro cliente: estatus === 'Aceptado', fecha > hoy
            const hoy = new Date();
            hoy.setHours(0, 0, 0, 0);

            this.trasladosData = (data || []).filter(t => {
                if (t.estatus !== 'Aceptado') return false;
                if (!t.fecha_viaje) return false;
                const [y, m, d] = t.fecha_viaje.split('-');
                const fechaCita = new Date(Number(y), Number(m) - 1, Number(d));
                return fechaCita > hoy; // estrictamente futuro
            });

            const select = document.getElementById('trasladoSelect');
            if (!select) return;

            // Limpiar opciones previas (excepto la primera)
            while (select.options.length > 1) select.remove(1);

            if (this.trasladosData.length === 0) {
                const opt = document.createElement('option');
                opt.disabled = true;
                opt.textContent = 'No hay traslados programados próximos';
                select.appendChild(opt);
                return;
            }

            this.trasladosData.forEach(t => {
                const name = `${t.paciente_nombre || ''} ${t.paciente_apellidos || ''}`.trim() || 'Sin Nombre';
                let dateText = t.fecha_viaje;
                if (t.fecha_viaje) {
                    try {
                        const [y, m, d] = t.fecha_viaje.split('-');
                        const dObj = new Date(Number(y), Number(m) - 1, Number(d));
                        if (!isNaN(dObj)) dateText = dObj.toLocaleDateString('es-MX', { year: 'numeric', month: '2-digit', day: '2-digit' });
                    } catch(e){}
                }
                const opt = document.createElement('option');
                opt.value = t.id;
                opt.textContent = `${name} — ${dateText}`;
                select.appendChild(opt);
            });

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
                console.log('✅ SMS Backend Online');
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
    async sendManual() {
        const phoneInput = document.getElementById('targetPhone');
        const textInput  = document.getElementById('messageText');
        const selectEl   = document.getElementById('trasladoSelect');
        const phone = (phoneInput?.value || '').trim();
        const text  = (textInput?.value  || '').trim();

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
                if (phoneInput) phoneInput.value = '';
                if (textInput)  { textInput.value = ''; textInput.dispatchEvent(new Event('input')); }
                if (selectEl)   selectEl.value = '';

                // ── Refresco automático del historial ──
                await this.cargarHistorialSMS();

                alert(`✅ SMS enviado (${result.mode || 'Real'} Mode)`);
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
