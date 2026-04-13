// sms.js
const SMS = {
    // Usar rutas relativas para que funcione en desarrollo local y en producción (Render)
    get API_URL() {
        return `/api/sms`;
    },
    trasladosData: [],

    async init() {
        if (typeof UI !== 'undefined' && UI.setupHeader) {
            UI.setupHeader('Gestión de Notificaciones');
        }
        
        // Verificar si el servidor está "despierto"
        const isOnline = await this.checkServerStatus();
        if (isOnline) {
            await this.renderHistory();
            await this.loadTraslados();
        }

        // ── Contador de caracteres + Vista previa en tiempo real ──
        const msgTextarea = document.getElementById('messageText');
        const charCounter = document.getElementById('charCount');
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

        // ── Selector de traslado → auto-llenado ──
        const selectInfo = document.getElementById('trasladoSelect');
        if (selectInfo) {
            selectInfo.addEventListener('change', (e) => {
                const val = e.target.value;
                if (!val) {
                    document.getElementById('targetPhone').value = '';
                    if (msgTextarea) msgTextarea.value = '';
                    if (charCounter) charCounter.textContent = '0/160 caracteres';
                    if (previewBubble) previewBubble.textContent = 'El mensaje aparecerá aquí...';
                    return;
                }
                const t = this.trasladosData.find(x => x.id == val);
                if (t) {
                    const phone = t.telefono_principal || t.telefono_secundario || '';
                    const name = `${t.paciente_nombre || ''} ${t.paciente_apellidos || ''}`.trim() || 'Beneficiario';

                    let date = t.fecha_viaje || 'su fecha programada';
                    let time = t.hora_cita || 'su hora asignada';

                    if (t.fecha_viaje) {
                        try {
                            const dateObj = new Date(t.fecha_viaje);
                            if (!isNaN(dateObj)) {
                                date = dateObj.toLocaleDateString('es-MX', { year: 'numeric', month: '2-digit', day: '2-digit' });
                            }
                        } catch(e){}
                    }

                    const msg = `FORMADIG: Hola ${name}, le recordamos su cita de traslado médico programada para el ${date} a las ${time}. ¿Confirma su asistencia?`;
                    document.getElementById('targetPhone').value = phone;
                    if (msgTextarea) {
                        msgTextarea.value = msg;
                        msgTextarea.dispatchEvent(new Event('input')); // dispara contador+preview
                    }
                }
            });
        }
    },

    async loadTraslados() {
        try {
            const res = await fetch(`${this.API_URL}/traslados`);
            if (res.ok) {
                this.trasladosData = await res.json();
                const select = document.getElementById('trasladoSelect');
                if (select && this.trasladosData.length > 0) {
                    this.trasladosData.forEach(t => {
                        const name = `${t.paciente_nombre || ''} ${t.paciente_apellidos || ''}`.trim() || 'Sin Nombre';
                        let dateText = t.fecha_viaje || 'Sin fecha';
                        if (t.fecha_viaje) {
                            try {
                                const dateObj = new Date(t.fecha_viaje);
                                if (!isNaN(dateObj)) dateText = dateObj.toLocaleDateString('es-MX', { year: 'numeric', month: '2-digit', day: '2-digit' });
                            } catch(e){}
                        }
                        const opt = document.createElement('option');
                        opt.value = t.id;
                        opt.textContent = `${name} - ${dateText}`;
                        select.appendChild(opt);
                    });
                }
            }
        } catch(e) {
            console.error('Error cargando traslados:', e);
        }
    },

    async checkServerStatus() {
        try {
            const res = await fetch(`${this.API_URL}/ping`, { mode: 'cors' });
            if (res.ok) {
                console.log('✅ SMS Backend Online');
                const statusIndicator = document.querySelector('.status-indicator');
                if (statusIndicator) {
                    statusIndicator.classList.add('connected');
                    statusIndicator.innerText = 'Conectado';
                }
                return true;
            }
        } catch (e) {
            console.error('❌ SMS Backend Offline');
            const statusIndicator = document.querySelector('.status-indicator');
            if (statusIndicator) {
                statusIndicator.classList.remove('connected');
                statusIndicator.style.background = '#ffebee';
                statusIndicator.style.color = '#c62828';
                statusIndicator.innerText = 'Desconectado (Inicia el servidor)';
            }
            return false;
        }
        return false;
    },

    async renderHistory() {
        const table = document.getElementById('smsLogTable');
        const statEnviadosHoy = document.getElementById('statEnviadosHoy');
        try {
            const response = await fetch(`${this.API_URL}/history`);
            const data = await response.json();
            
            if (data.error) throw new Error(data.error);

            if (data.length === 0) {
                table.innerHTML = `<tr><td colspan="4" style="text-align:center; color:#64748b; padding: 20px;">No hay mensajes registrados aún.</td></tr>`;
                if(statEnviadosHoy) statEnviadosHoy.innerText = '0';
                return;
            }

            // Calcular mensajes de hoy
            const hoyStr = new Date().toISOString().split('T')[0];
            const enviadosHoy = data.filter(log => log.fecha && log.fecha.startsWith(hoyStr)).length;
            if(statEnviadosHoy) statEnviadosHoy.innerText = enviadosHoy;

            table.innerHTML = data.map(log => {
                const badgeClass = (log.estatus || '').toLowerCase() === 'enviado' ? 'enviado' : 'error';
                const fechaStr = log.fecha ? new Date(log.fecha).toLocaleString('es-MX') : '--';
                return `
                <tr>
                    <td>${fechaStr}</td>
                    <td>${log.telefono || '--'}</td>
                    <td style="max-width:280px; word-break:break-word; font-size:0.85rem;">${log.mensaje || '--'}</td>
                    <td><span class="status-tag ${badgeClass}">${log.estatus || '--'}</span></td>
                </tr>`;
            }).join('');
        } catch (error) {
            console.error('Error cargando historial:', error);
            table.innerHTML = `<tr><td colspan="4" style="text-align:center; color:red; padding: 20px;">Error al conectar con el servidor de mensajes</td></tr>`;
            if(statEnviadosHoy) statEnviadosHoy.innerText = 'Error';
        }
    },

    async sendManual() {
        const phoneInput = document.getElementById('targetPhone');
        const textInput = document.getElementById('messageText');
        const phone = phoneInput.value;
        const text = textInput.value;

        if (!phone || !text) {
            alert('Por favor completa todos los campos');
            return;
        }

        const btn = document.querySelector('.sms-action-card .button');
        const originalText = btn.innerText;
        btn.disabled = true;
        btn.innerText = 'Enviando...';

        try {
            const response = await fetch(`${this.API_URL}/send`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    phone: phone,
                    message: text,
                    user_id: localStorage.getItem('user_email') || 'admin_dif'
                })
            });

            const result = await response.json();

            if (result.status === 'Enviado') {
                alert(`✅ Mensaje enviado correctamente (${result.mode} Mode)`);
                phoneInput.value = '';
                textInput.value = '';
                await this.renderHistory();
            } else {
                alert(`❌ Error: ${result.error || 'No se pudo enviar el mensaje'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('❌ No se pudo conectar con el servidor de SMS. Verifica que el backend esté en línea.');
        } finally {
            btn.disabled = false;
            btn.innerText = originalText;
        }
    }
};

document.addEventListener('DOMContentLoaded', () => SMS.init());
