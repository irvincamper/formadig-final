// sms.js
const SMS = {
    // Usar rutas relativas para que funcione en desarrollo local y en producción (Render)
    get API_URL() {
        return `/api/sms`;
    },

    async init() {
        if (typeof UI !== 'undefined' && UI.setupHeader) {
            UI.setupHeader('Gestión de Notificaciones');
        }
        
        // Verificar si el servidor está "despierto"
        const isOnline = await this.checkServerStatus();
        if (isOnline) {
            await this.renderHistory();
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

            table.innerHTML = data.map(log => `
                <tr>
                    <td>${new Date(log.fecha).toLocaleString()}</td>
                    <td>${log.telefono}</td>
                    <td>${log.mensaje}</td>
                    <td><span class="status-tag ${log.estatus.toLowerCase()}">${log.estatus}</span></td>
                </tr>
            `).join('');
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
            alert('❌ No se pudo conectar con el servidor de SMS. Asegúrate de que el backend esté corriendo en el puerto 5009.');
        } finally {
            btn.disabled = false;
            btn.innerText = originalText;
        }
    }
};

document.addEventListener('DOMContentLoaded', () => SMS.init());
