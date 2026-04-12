// chatbot.js
document.addEventListener('DOMContentLoaded', () => {
    UI.setupHeader('Asistente Virtual');
    
    const chatWindow = document.getElementById('chatWindow');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');

    // Formateador robusto de Markdown (Tablas, Botones, Títulos)
    function formatMarkdown(text) {
        if (!text) return "";
        
        // 1. Limpieza inicial
        let html = text.trim();

        // 2. Procesar Bloque de Botones Especiales (EXPORT_BUTTONS)
        if (html.includes('EXPORT_BUTTONS:')) {
            const parts = html.split('EXPORT_BUTTONS:');
            const mainText = parts[0];
            const buttonsBlock = parts[1];
            
            // Extraer enlaces del bloque
            const buttonRegex = /\[(.*?)\]\((.*?)\)/g;
            let buttonsHtml = '<div class="report-actions">';
            let match;
            while ((match = buttonRegex.exec(buttonsBlock)) !== null) {
                const label = match[1];
                const url = match[2];
                let btnClass = "chat-link";
                if (url.includes('excel')) btnClass += " btn-excel";
                if (url.includes('word')) btnClass += " btn-word";
                if (url.includes('pdf')) btnClass += " btn-pdf";
                
                buttonsHtml += `<a href="${url}" class="${btnClass}" target="_blank">${label}</a>`;
            }
            buttonsHtml += '</div>';
            
            html = mainText + buttonsHtml;
        }

        // 3. Títulos (###) - Capturar incluso si no hay salto de línea previo
        html = html.replace(/### (.*?)(?=\n|$)/g, '<h3>$1</h3>');
        html = html.replace(/## (.*?)(?=\n|$)/g, '<h2>$1</h2>');
        html = html.replace(/# (.*?)(?=\n|$)/g, '<h1>$1</h1>');

        // 4. Enlaces estándar [texto](url) que no son botones
        html = html.replace(/\[(.*?)\]\((.*?)\)/g, (match, text, url) => {
            if (url.includes('export')) return match; // Ignorar si ya se procesó como botón
            return `<a href="${url}" class="chat-inline-link" target="_blank">${text}</a>`;
        });

        // 5. Tablas Markdown
        if (html.includes('|')) {
            const lines = html.split('\n');
            let inTable = false;
            let tableHtml = '<div class="table-container"><table>';
            let newHtml = "";
            
            lines.forEach((line) => {
                const trimmed = line.trim();
                if (trimmed.startsWith('|') || (trimmed.includes('|') && trimmed.split('|').length > 2)) {
                    const cells = trimmed.split('|').filter((c, i) => {
                        if (i === 0 && c.trim() === "") return false;
                        if (i === line.split('|').length - 1 && c.trim() === "") return false;
                        return true;
                    });
                    
                    if (cells.length > 0 && !trimmed.includes('---') && !trimmed.includes(':---')) {
                        if (!inTable) {
                            inTable = true;
                            tableHtml += '<thead><tr>' + cells.map(c => `<th>${c.trim()}</th>`).join('') + '</tr></thead><tbody>';
                        } else {
                            tableHtml += '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>';
                        }
                    }
                } else {
                    if (inTable) {
                        inTable = false;
                        tableHtml += '</tbody></table></div>';
                        newHtml += tableHtml + line + '\n';
                        tableHtml = '<div class="table-container"><table>';
                    } else {
                        newHtml += line + '\n';
                    }
                }
            });
            if (inTable) {
                tableHtml += '</tbody></table></div>';
                newHtml += tableHtml;
            }
            html = newHtml;
        }

        // 6. Negritas y Cursivas
        html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // 7. Saltos de línea
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    const attachmentBtn = document.getElementById('attachment-btn');
    const bulkUploadInput = document.getElementById('bulk-upload-input');

    function addMessage(text, type) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;
        
        const formattedText = type === 'bot' ? formatMarkdown(text) : text;
        msgDiv.innerHTML = `<div class="message-content">${formattedText}</div>`;
        
        chatWindow.appendChild(msgDiv);
        
        // Scroll suave al final
        setTimeout(() => {
            chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
        }, 30);
    }

    async function handleSend() {
        const text = userInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        userInput.value = '';

        // Indicador de "Escribiendo..." Premium (Puntos animados)
        const typingId = 'typing-' + Date.now();
        const typingMsg = document.createElement('div');
        typingMsg.className = 'message bot';
        typingMsg.id = typingId;
        typingMsg.innerHTML = `
            <div class="typing" style="display: block;">
                <span></span><span></span><span></span>
            </div>
        `;
        chatWindow.appendChild(typingMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        
        const startTime = Date.now();

        try {
            const user = Auth.getUser();
            const response = await fetch('/api/chatbot/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: text,
                    email: user.email,
                    role: user.role
                })
            });
            
            const data = await response.json();
            
            // Simular tiempo de "pensado" natural (mínimo 800ms)
            const elapsedTime = Date.now() - startTime;
            const remainingTime = Math.max(0, 800 - elapsedTime);

            setTimeout(() => {
                const typingEl = document.getElementById(typingId);
                if (typingEl) typingEl.remove();

                if (data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage("Hubo un problema al obtener respuesta de la IA.", 'bot');
                }
            }, remainingTime);

        } catch (error) {
            console.error("Error al contactar con el chatbot:", error);
            const typingEl = document.getElementById(typingId);
            if (typingEl) typingEl.remove();
            addMessage("Lo siento, tuve un problema al conectar con el servidor. Verifica su disponibilidad.", 'bot');
        }
    }

    // 📤 LÓGICA DE CARGA MASIVA
    attachmentBtn.onclick = () => bulkUploadInput.click();

    bulkUploadInput.onchange = async () => {
        const file = bulkUploadInput.files[0];
        if (!file) return;

        addMessage(`Subiendo archivo: **${file.name}**`, 'user');
        
        // Bloque de carga
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'message bot';
        loadingMsg.innerHTML = '<div class="message-content">🔍 Analizando y procesando registros... esto puede tardar unos segundos.</div>';
        chatWindow.appendChild(loadingMsg);
        chatWindow.scrollTop = chatWindow.scrollHeight;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/chatbot/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            
            loadingMsg.remove();

            if (data.error) {
                addMessage(`❌ ERROR: ${data.error}`, 'bot');
            } else {
                addMessage(`✅ **${data.message}**\n\nLos datos ya están disponibles en los módulos oficiales de ${data.table.toUpperCase()}.`, 'bot');
            }
        } catch (err) {
            loadingMsg.remove();
            addMessage("❌ Error crítico de red al intentar subir el archivo.", 'bot');
        } finally {
            bulkUploadInput.value = ''; // Reset
        }
    };

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Lógica de Impresión Directa
    const pBtn = document.getElementById('printBtn');
    if (pBtn) {
        pBtn.addEventListener('click', () => {
            window.print();
        });
    }
});


