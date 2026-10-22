const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const ui = require('../Formadig/1_Sistema_DIF_Acatlan/core/clinical-ui.js');

test('Psicología serializa sesión entera, nulos y fecha UTC sin headers de rol', () => {
    const payload = ui.serialize('psicologia', {paciente_id: ' ficticio ', tipo_atencion: ' Individual ',
        motivo_consulta: ' Sintético ', diagnostico_inicial: '', numero_sesion: '3', estatus_caso: 'En proceso',
        fecha_sesion: '2026-10-21T10:00:00-06:00', role: 'admin', atendido_por: 'spoof'});
    assert.equal(payload.numero_sesion, 3);
    assert.equal(payload.fecha_sesion, '2026-10-21T16:00:00.000Z');
    assert.equal(payload.diagnostico_inicial, null);
    assert.equal(payload.paciente_id, 'ficticio');
    assert.equal(payload.role, undefined);
    assert.equal(payload.atendido_por, undefined);
});
test('Dentista conserva centavos como decimal textual y omite fecha vacía', () => {
    const payload = ui.serialize('dentista', {paciente_id: 'p', motivo_consulta: 'x', costo_recuperacion: '123.40'});
    assert.equal(payload.costo_recuperacion, '123.40');
    assert.equal(payload.fecha_atencion, undefined);
    assert.throws(() => ui.serialize('dentista', {fecha_atencion: 'ayer'}));
});
test('Edición parcial preserva precisión de fechas y no reasigna paciente/profesional', () => {
    const date = '2026-10-21T16:00:23.123456+00:00';
    const row = {paciente_id: 'real', atendido_por: 'profesional', motivo_consulta: 'previo',
        diagnostico: null, tratamiento_realizado: null, costo_recuperacion: '25.50', fecha_atencion: date};
    const payload = ui.serializeUpdate('dentista', {motivo_consulta: 'nuevo', diagnostico: '',
        tratamiento_realizado: '', costo_recuperacion: '25.50', fecha_atencion: ui.localDate(date)}, row);
    assert.deepEqual(payload, {motivo_consulta: 'nuevo'});
});
test('Edición sin cambios no construye un PATCH vacío ni borra columnas NULL históricas', () => {
    const row = {motivo_consulta: 'igual', tipo_atencion: 'Individual', diagnostico_inicial: null,
        estatus_caso: 'En proceso', numero_sesion: 1, fecha_sesion: null};
    assert.deepEqual(ui.serializeUpdate('psicologia', {...row, diagnostico_inicial: '', fecha_sesion: ''}, row), {});
});
test('HTML mantiene campos obligatorios, scripts separados y enlaces resolubles', () => {
    for (const kind of ['psicologia', 'dentista']) {
        const file = path.resolve(__dirname, `../Formadig/1_Sistema_DIF_Acatlan/modulos/admin_${kind}/vistas/admin_${kind}.html`);
        const html = fs.readFileSync(file, 'utf8');
        for (const id of ['attention-form', 'search-form', 'history', 'results', 'detail', 'status', 'previous', 'next', 'sidebarMenu', 'new-attention']) {
            assert.ok(html.includes(`id="${id}"`));
        }
        assert.match(html, /name="paciente_id" required/);
        assert.match(html, /name="motivo_consulta"[^>]*required/);
        assert.ok(!html.includes('Registrar atención'));
        assert.ok(!html.includes('Nueva atención'));
        for (const [, target] of html.matchAll(/(?:src|href)="([^"]+)"/g)) {
            assert.ok(fs.existsSync(path.resolve(path.dirname(file), target.split('?')[0])), target);
        }
    }
});

test('Sidebar conserva áreas previas y separa los dos accesos nuevos', () => {
    const vm = require('node:vm');
    const code = fs.readFileSync(path.resolve(__dirname, '../Formadig/1_Sistema_DIF_Acatlan/core/formadig-core.js'), 'utf8');
    for (const role of ['admin', 'admin_traslados', 'admin_desayunos', 'psicologo', 'dentista']) {
        const sidebar = {innerHTML: '', classList: {add() {}}};
        const context = {localStorage: {getItem: key => key === 'user_role' ? role : null},
            window: {location: {pathname: '/dashboard.html'}}, document: {
                querySelector: () => ({innerHTML: ''}), getElementById: () => sidebar
            }};
        vm.createContext(context); vm.runInContext(code, context); context.UI.setupHeader('Test');
        const html = sidebar.innerHTML;
        assert.equal(html.includes('modulos/admin_psicologia/'), ['admin', 'psicologo'].includes(role), role);
        assert.equal(html.includes('modulos/admin_dentista/'), ['admin', 'dentista'].includes(role), role);
        assert.equal(html.includes('modulos/admin_traslados/'), ['admin', 'admin_traslados'].includes(role), role);
        assert.equal(html.includes('modulos/admin_desayunos_frios/'), ['admin', 'admin_desayunos'].includes(role), role);
    }
});
