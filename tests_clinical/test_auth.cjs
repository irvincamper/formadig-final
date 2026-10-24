const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../Formadig/1_Sistema_DIF_Acatlan/core/formadig-core.js'), 'utf8');

function app(role = 'dentista', status = 200) {
    const store = new Map([['supabase_token', 'synthetic-token'], ['user_role', 'admin']]);
    const calls = [], events = [], header = {innerHTML: ''};
    const context = {
        URL, Headers, console,
        localStorage: {getItem: k => store.get(k) || null, setItem: (k,v) => store.set(k,v), clear: () => store.clear()},
        window: {location: {pathname: '/dashboard.html', href: 'http://127.0.0.1:8011/dashboard.html', origin: 'http://127.0.0.1:8011', reload: () => events.push('reload')}},
        document: {addEventListener() {}, querySelector: () => header, getElementById: () => null},
        fetch: async (url, options) => { calls.push({url,options}); return {ok: status === 200, status, json: async () => ({role,nombre_completo:'Synthetic'})}; }
    };
    vm.createContext(context); vm.runInContext(code, context);
    return {context, store, calls, events, header};
}

test('Los cinco roles se revalidan con JWT y sin confiar en localStorage', async () => {
    for (const role of ['admin','admin_traslados','admin_desayunos','psicologo','dentista']) {
        const a = app(role);
        assert.equal(await vm.runInContext('Auth.verifySession()', a.context), true);
        assert.equal(a.store.get('user_role'), role);
        assert.equal(a.calls[0].options.headers.Authorization, 'Bearer synthetic-token');
        assert.equal(a.calls[0].options.cache, 'no-store');
    }
});

test('401/403 eliminan sesión y devuelven al login', async () => {
    for (const status of [401,403]) {
        const a = app('admin',status);
        assert.equal(await vm.runInContext('Auth.verifySession()',a.context),false);
        assert.equal(a.store.size,0);
        assert.match(a.context.window.location.href,/login/);
    }
});

test('Un rol desconocido no se acepta aunque la respuesta sea 200', async () => {
    const a = app('directora');
    assert.equal(await vm.runInContext('Auth.verifySession()',a.context),false);
    assert.equal(a.store.size,0);
});

test('Una caída 503 no se considera sesión verificada', async () => {
    const a = app('admin',503);
    assert.equal(await vm.runInContext('Auth.verifySession()',a.context),false);
    assert.equal(a.events.length,0);
});

test('Auth.fetch añade el token sólo a la API del mismo origen', async () => {
    const a = app();
    await vm.runInContext("Auth.fetch('/api/traslados')",a.context);
    await vm.runInContext("Auth.fetch('https://example.invalid/api/traslados')",a.context);
    assert.equal(a.calls[0].options.headers.get('Authorization'),'Bearer synthetic-token');
    assert.equal(a.calls[1].options.headers.get('Authorization'),null);
});

test('El nombre de perfil se muestra como texto en el header', () => {
    const a = app();
    a.store.set('user_fullname','<img src=x onerror=alert(1)>');
    vm.runInContext("UI.setupHeader('Test')",a.context);
    assert.ok(!a.header.innerHTML.includes('<img'));
    assert.ok(a.header.innerHTML.includes('&lt;img'));
});

test('Logout limpia el navegador y solicita revocacion remota con su JWT', async () => {
    const a=app();
    await vm.runInContext('Auth.logout()',a.context);
    assert.equal(a.store.size,0);
    assert.equal(a.calls[0].url,'/api/auth/logout');
    assert.equal(a.calls[0].options.method,'POST');
    assert.equal(a.calls[0].options.headers.Authorization,'Bearer synthetic-token');
    assert.match(a.context.window.location.href,/login/);
});
