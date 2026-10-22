/* Contrato clínico compartido. Presentación: data-field/data-column y CSS externos. */
(function (root) {
    'use strict';
    const schemas = {
        psicologia: {date: 'fecha_sesion', text: ['tipo_atencion', 'motivo_consulta', 'diagnostico_inicial', 'estatus_caso']},
        dentista: {date: 'fecha_atencion', text: ['motivo_consulta', 'diagnostico', 'tratamiento_realizado']}
    };
    function serialize(kind, values) {
        const s = schemas[kind];
        const payload = {paciente_id: String(values.paciente_id || '').trim()};
        s.text.forEach(key => {
            if (values[key] !== undefined) payload[key] = String(values[key]).trim() || null;
        });
        if (values[s.date]) {
            const date = new Date(values[s.date]);
            if (Number.isNaN(date.getTime())) throw new Error('Fecha inválida.');
            payload[s.date] = date.toISOString();
        }
        if (kind === 'psicologia') payload.numero_sesion = Number(values.numero_sesion);
        else payload.costo_recuperacion = String(values.costo_recuperacion || '0.00');
        return payload;
    }
    function localDate(iso) {
        if (!iso) return '';
        const d = new Date(iso);
        if (Number.isNaN(d.getTime())) return '';
        return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    }
    function serializeUpdate(kind, values, originalRow) {
        const payload = serialize(kind, values);
        delete payload.paciente_id;
        const dateField = schemas[kind].date;
        if (values[dateField] === localDate(originalRow[dateField])) delete payload[dateField];
        for (const key of Object.keys(payload)) {
            if (key !== dateField && String(payload[key] ?? '') === String(originalRow[key] ?? '')) delete payload[key];
        }
        return payload;
    }
    function mount(kind) {
        const document = root.document;
        const form = document.querySelector('#attention-form');
        const search = document.querySelector('#search-form');
        const status = document.querySelector('#status');
        const results = document.querySelector('#results');
        const detail = document.querySelector('#detail');
        const submit = form.querySelector('[type=submit]');
        const controls = Array.from(form.elements);
        let selectedId = null, originalRow = null, canUpdate = false, canCreate = false, offset = 0, hasMore = false, historyPatient = null;
        let listSequence = 0, detailSequence = 0;
        let busy = false;
        const token = root.localStorage.getItem('supabase_token');
        const api = '/api/' + kind;
        function message(text, error = false) {
            status.textContent = text;
            status.dataset.error = String(error);
        }
        async function request(path, options = {}) {
            const headers = {'Authorization': 'Bearer ' + token, ...options.headers};
            if (options.body) headers['Content-Type'] = 'application/json';
            const response = await root.fetch(api + path, {...options, headers, cache: 'no-store'});
            let value;
            try { value = await response.json(); }
            catch (_) { throw new Error('El servidor devolvió una respuesta inválida.'); }
            if (!response.ok) {
                const fields = Object.entries(value.fields || {}).map(([k, v]) => k + ': ' + v).join(' ');
                throw new Error((value.error || 'Error de servidor.') + (fields ? ' ' + fields : ''));
            }
            return value;
        }
        function valuesOf(element) { return Object.fromEntries(new root.FormData(element)); }
        function newRecord() {
            selectedId = null;
            originalRow = null;
            ++detailSequence;
            form.reset();
            controls.forEach(el => { el.disabled = !canCreate; });
            submit.textContent = canCreate ? 'Registrar atención sintética' : 'Registro bloqueado por permisos';
            detail.textContent = 'Selecciona una atención o utiliza el registro sintético local si está habilitado.';
        }
        async function loadDetail(id) {
            const seq = ++detailSequence;
            try {
                const {data} = await request('/' + encodeURIComponent(id));
                if (seq !== detailSequence) return;
                selectedId = data.id;
                originalRow = data;
                controls.forEach(el => {
                    if (el.name) el.value = el.name === schemas[kind].date ? localDate(data[el.name]) : (data[el.name] ?? '');
                    el.disabled = !canUpdate || el.name === 'paciente_id';
                });
                submit.textContent = canUpdate ? 'Guardar edición' : 'Edición pendiente de permisos RLS';
                detail.textContent = JSON.stringify(data, null, 2);
                message(canUpdate ? 'Detalle cargado. Puedes actualizar el seguimiento.' : 'Detalle cargado. Seguimiento bloqueado hasta aprobar RLS.');
            } catch (error) { if (seq === detailSequence) message(error.message, true); }
        }
        async function list() {
            const seq = ++listSequence;
            document.querySelector('#previous').disabled = true;
            document.querySelector('#next').disabled = true;
            const params = new root.URLSearchParams();
            for (const [key, value] of Object.entries(valuesOf(search))) {
                if (value.trim()) params.set(key, value.trim());
            }
            params.set('offset', String(offset));
            params.set('limit', '25');
            const path = historyPatient ? '/pacientes/' + encodeURIComponent(historyPatient) + '/historial' : '/';
            try {
                const value = await request(path + '?' + params);
                if (seq !== listSequence) return;
                results.replaceChildren();
                value.data.forEach(row => {
                    const tr = document.createElement('tr');
                    [row.paciente?.nombre_completo || row.paciente_id, row[schemas[kind].date], row.motivo_consulta].forEach(value => {
                        const td = document.createElement('td');
                        td.textContent = value ?? '';
                        tr.append(td);
                    });
                    const td = document.createElement('td');
                    const button = document.createElement('button');
                    button.type = 'button'; button.className = 'button button--secondary'; button.textContent = 'Ver detalle';
                    button.addEventListener('click', () => loadDetail(row.id));
                    td.append(button); tr.append(td); results.append(tr);
                });
                hasMore = value.pagination.has_more;
                document.querySelector('#previous').disabled = offset === 0;
                document.querySelector('#next').disabled = !hasMore;
                message((historyPatient ? 'Historial: ' : '') + value.data.length + ' atenciones. Página ' + (offset / 25 + 1));
            } catch (error) {
                if (seq === listSequence) {
                    results.replaceChildren(); hasMore = false;
                    document.querySelector('#previous').disabled = true;
                    document.querySelector('#next').disabled = true;
                    message(error.message, true);
                }
            }
        }
        search.addEventListener('submit', event => { event.preventDefault(); historyPatient = null; offset = 0; list(); });
        let searchTimer;
        search.elements.q.addEventListener('input', () => {
            root.clearTimeout(searchTimer);
            searchTimer = root.setTimeout(() => { historyPatient = null; offset = 0; list(); }, 250);
        });
        document.querySelector('#new-attention').addEventListener('click', newRecord);
        document.querySelector('#history').addEventListener('click', () => {
            const patient = search.elements.paciente_id.value.trim();
            if (!patient) return message('Indica el UUID del paciente para consultar su historial.', true);
            historyPatient = patient; offset = 0; list();
        });
        document.querySelector('#previous').addEventListener('click', () => { if (offset > 0) { offset -= 25; list(); } });
        document.querySelector('#next').addEventListener('click', () => { if (hasMore) { offset += 25; list(); } });
        form.addEventListener('submit', async event => {
            event.preventDefault();
            if (busy || (selectedId ? !canUpdate : !canCreate)) return;
            busy = true; submit.disabled = true;
            try {
                const values = valuesOf(form);
                const payload = selectedId ? serializeUpdate(kind, values, originalRow) : serialize(kind, values);
                if (selectedId) {
                    // Preservar segundos y campos históricos si el formulario no los cambió.
                    if (!Object.keys(payload).length) { message('No hay cambios para guardar.'); return; }
                }
                const path = selectedId ? '/' + encodeURIComponent(selectedId) : '/';
                const value = await request(path, {method: selectedId ? 'PATCH' : 'POST', body: JSON.stringify(payload)});
                newRecord();
                await list();
                message(value.message);
            } catch (error) { message(error.message, true); }
            finally { busy = false; submit.disabled = selectedId ? !canUpdate : !canCreate; }
        });
        async function start() {
            controls.forEach(el => { el.disabled = true; });
            if (!token) { message('Inicia sesión en FORMADIG para acceder.', true); return; }
            try {
                const {data} = await request('/capacidades');
                canUpdate = data.update === true;
                canCreate = data.create === true;
                document.querySelector('#new-attention').disabled = !canCreate;
                newRecord(); await list();
            } catch (error) { message(error.message, true); }
        }
        if (root.UI) root.UI.setupHeader(kind === 'psicologia' ? 'Psicología' : 'Dentista');
        start();
    }
    const exported = {serialize, serializeUpdate, localDate, mount};
    if (typeof module !== 'undefined' && module.exports) module.exports = exported;
    else root.ClinicalUI = exported;
})(typeof window === 'undefined' ? globalThis : window);
