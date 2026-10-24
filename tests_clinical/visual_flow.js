async (page) => {
    const base = 'http://127.0.0.1:8011';
    const patient = '00000000-0000-0000-0000-000000000002';
    const results = [], errors = [], httpErrors = [], external = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('response', response => { if (response.status() >= 400) httpErrors.push({url: response.url(), status: response.status()}); });
    await page.context().route('**/*', route => {
        if (new URL(route.request().url()).origin === base) return route.continue();
        external.push(route.request().url()); return route.abort();
    });
    const ok = (condition, message) => { if (!condition) throw new Error(message); };
    const check = async (name, fn) => {
        try { await fn(); results.push({name, passed: true}); }
        catch (error) { results.push({name, passed: false, error: error.message}); }
    };
    const status = () => page.locator('#status');
    const waitStatus = text => page.waitForFunction(text => document.querySelector('#status')?.textContent.includes(text), text);
    const modulePath = kind => '/modulos/admin_' + kind + '/vistas/admin_' + kind + '.html';
    const login = async role => {
        await page.goto(base + '/demo');
        await page.locator('[data-role="' + role + '"]').click();
    };
    const open = async kind => {
        await page.goto(base + modulePath(kind));
        await waitStatus('atenciones. Página');
    };
    const clearFilters = async () => {
        for (const input of await page.locator('#search-form input').all()) await input.fill('');
        const response = page.waitForResponse(r => r.url().includes('/api/') && r.url().includes('offset=0') && r.request().method() === 'GET');
        await page.locator('#search-form button[type=submit]').click(); await response;
        await waitStatus('atenciones. Página');
    };
    const fillRecord = async (kind, marker, invalidPatient = false) => {
        await page.locator('#new-attention').click();
        const form = page.locator('#attention-form');
        await form.locator('[name=paciente_id]').fill(invalidPatient ? 'UUID-invalido' : patient);
        await form.locator('[name=motivo_consulta]').fill(marker);
        if (kind === 'psicologia') {
            await form.locator('[name=tipo_atencion]').fill('Individual sintética');
            await form.locator('[name=numero_sesion]').fill('2');
            await form.locator('[name=estatus_caso]').fill('En proceso');
            await form.locator('[name=diagnostico_inicial]').fill('Observación ficticia <b>sin HTML</b>');
        } else {
            await form.locator('[name=costo_recuperacion]').fill('123.40');
            await form.locator('[name=diagnostico]').fill('Observación ficticia <b>sin HTML</b>');
            await form.locator('[name=tratamiento_realizado]').fill('Seguimiento exclusivamente sintético');
        }
    };
    const save = async (kind, method, expectedStatus) => {
        const response = page.waitForResponse(r => r.url().includes('/api/' + kind) && r.request().method() === method);
        await page.locator('#attention-form [type=submit]').click();
        const r = await response;
        ok(r.status() === expectedStatus, method + ': HTTP ' + r.status());
        return r.json();
    };
    await page.setViewportSize({width: 1440, height: 1000});
    for (const [role, kind, other] of [['psicologo', 'psicologia', 'dentista'], ['dentista', 'dentista', 'psicologia']]) {
        await login(role); await open(kind);
        await check(role + ': listado y menú por área', async () => {
            ok(await page.locator('#results tr').count() >= 1, 'Listado vacío');
            ok(await page.locator('.sidebar a[href*="admin_' + kind + '/"]').count() === 1, 'Falta menú autorizado');
            ok(await page.locator('.sidebar a[href*="admin_' + other + '/"]').count() === 0, 'Menú cruzado visible');
            ok(await page.locator('.sidebar a[href*="admin_usuarios/"]').count() === 0, 'Gestión de Usuarios visible');
        });
        await check(role + ': navegación directa al área ajena denegada', async () => {
            await page.goto(base + modulePath(other)); await waitStatus('No tienes autorización');
            ok(await page.locator('#results tr').count() === 0, 'Filas ajenas visibles');
            ok(await page.locator('#attention-form [type=submit]').isDisabled(), 'Escritura ajena habilitada');
            await open(kind);
        });
        await check(role + ': formulario obligatorio y validación nativa', async () => {
            await page.locator('#new-attention').click();
            let sent = 0; const listener = r => { if (r.request().method() === 'POST') sent++; };
            page.on('response', listener);
            await page.locator('#attention-form [type=submit]').click();
            ok(await page.locator('#attention-form').evaluate(form => !form.checkValidity()), 'Formulario vacío aceptado');
            ok(sent === 0, 'Formulario inválido envió POST'); page.off('response', listener);
        });
        const marker = 'VISUAL-' + kind.toUpperCase();
        await check(role + ': UUID inválido muestra error del backend', async () => {
            await fillRecord(kind, marker, true); await save(kind, 'POST', 400); await waitStatus('UUID');
            ok(await status().getAttribute('data-error') === 'true', 'Error no marcado');
            await page.evaluate(() => window.scrollTo(0, 0));
            await page.screenshot({path: 'output/playwright/' + kind + '-validacion.png', fullPage: true});
        });
        let row;
        await check(role + ': registrar con botón y consultar listado', async () => {
            await fillRecord(kind, marker); const value = await save(kind, 'POST', 201); row = value.data;
            await waitStatus('Registro sintético creado');
            ok(row.paciente_id === patient && row.atendido_por, 'Relaciones no asignadas');
            if (kind === 'dentista') ok(row.costo_recuperacion === '123.40', 'Centavos alterados');
            ok(await page.locator('#results').innerText().then(x => x.includes(marker)), 'Alta ausente del listado');
        });
        await check(role + ': búsqueda al escribir y restauración', async () => {
            await page.locator('#search-form [name=q]').fill('NO-EXISTE-VISUAL');
            await waitStatus('0 atenciones'); ok(await page.locator('#results tr').count() === 0, 'Búsqueda no filtró');
            await page.locator('#search-form [name=q]').fill(marker);
            await waitStatus('1 atenciones'); ok(await page.locator('#results tr').count() === 1, 'No recuperó registro');
        });
        await check(role + ': selección, detalle y edición con persistencia en memoria', async () => {
            await page.locator('#results button').click(); await waitStatus('Detalle cargado');
            ok(await page.locator('#detail').innerText().then(x => x.includes(row.id)), 'Detalle equivocado');
            ok(await page.locator('#attention-form [name=paciente_id]').isDisabled(), 'Paciente editable');
            await page.locator('#attention-form [name=motivo_consulta]').fill(marker + '-EDITADO');
            await save(kind, 'PATCH', 200); await waitStatus('Seguimiento actualizado');
            await page.reload(); await waitStatus('atenciones. Página');
            await page.locator('#search-form [name=q]').fill(marker + '-EDITADO'); await waitStatus('1 atenciones');
            await page.locator('#results button').click(); await waitStatus('Detalle cargado');
            ok(await page.locator('#attention-form [name=motivo_consulta]').inputValue() === marker + '-EDITADO', 'Edición no persistió en nueva consulta');
            await page.locator('#attention-form [type=submit]').click(); await waitStatus('No hay cambios');
            await page.evaluate(() => window.scrollTo(0, 0));
            await page.screenshot({path: 'output/playwright/' + kind + '-editado.png', fullPage: true});
        });
        await check(role + ': filtros por fecha, paciente y área', async () => {
            await clearFilters();
            await page.locator('#search-form [name=desde]').fill('2030-01-01T00:00:00Z');
            await page.locator('#search-form button[type=submit]').click(); await waitStatus('0 atenciones');
            await clearFilters();
            if (kind === 'psicologia') {
                await page.locator('#search-form [name=tipo_atencion]').fill('No coincide');
                await page.locator('#search-form button[type=submit]').click(); await waitStatus('0 atenciones');
                await clearFilters();
            }
            await page.locator('#history').click(); await waitStatus('Indica el UUID');
            await page.locator('#search-form [name=paciente_id]').fill(patient);
            await page.locator('#history').click(); await waitStatus('Historial:');
            ok(await page.locator('#results tr').count() >= 2, 'Historial incompleto');
            await clearFilters();
        });
        await check(role + ': 26 registros y paginación con botones', async () => {
            for (let i = 0; i < 24; i++) {
                await fillRecord(kind, 'PAG-' + kind + '-' + i);
                await save(kind, 'POST', 201); await waitStatus('Registro sintético creado');
            }
            await clearFilters();
            ok(await page.locator('#results tr').count() === 25, 'Primera página distinta de 25');
            await page.locator('#next').click(); await waitStatus('Página 2');
            ok(await page.locator('#results tr').count() >= 1, 'Segunda página vacía');
            await page.locator('#previous').click(); await waitStatus('Página 1');
            ok(await page.locator('#results tr').count() === 25, 'No regresó a primera página');
        });
        await check(role + ': panel y regreso por tarjeta', async () => {
            await page.getByRole('link', {name: '← Volver al Panel'}).click();
            await page.waitForURL('**/dashboard.html');
            ok(await page.locator('a[href*="admin_' + other + '/"]').count() === 0, 'Panel expone área ajena');
            await page.locator('a[href*="admin_' + kind + '/"]').last().click(); await waitStatus('atenciones. Página');
        });
        await check(role + ': HTTP 503 desactiva paginación y permite recuperarse', async () => {
            await page.route(url => url.pathname === '/api/' + kind + '/', route => route.fulfill({status: 503,
                contentType: 'application/json', body: JSON.stringify({error: 'Fallo sintético de listado'})}), {times: 1});
            await page.locator('#search-form [name=q]').fill('ERROR-SINTETICO');
            await waitStatus('Fallo sintético');
            ok(await page.locator('#results tr').count() === 0, 'Tabla antigua tras fallo');
            ok(await page.locator('#next').isDisabled() && await page.locator('#previous').isDisabled(), 'Paginación obsoleta habilitada');
            await page.evaluate(() => window.scrollTo(0, 0));
            await page.screenshot({path: 'output/playwright/' + kind + '-error503.png', fullPage: false});
            await clearFilters();
            ok(await page.locator('#results tr').count() === 25, 'No recuperó listado');
        });
        await check(role + ': vista estrecha conserva controles', async () => {
            await page.setViewportSize({width: 800, height: 1000});
            ok(await page.locator('#search-form [type=submit]').isVisible(), 'Buscar no visible');
            await page.evaluate(() => window.scrollTo(0, 0));
            await page.screenshot({path: 'output/playwright/' + kind + '-estrecho.png', fullPage: false});
            await page.setViewportSize({width: 1440, height: 1000});
        });
    }
    await login('admin');
    for (const kind of ['psicologia', 'dentista']) await check('admin: acceso y menú ' + kind, async () => {
        await open(kind);
        ok(await page.locator('.sidebar a[href*="admin_psicologia/"]').count() === 1, 'Falta Psicología');
        ok(await page.locator('.sidebar a[href*="admin_dentista/"]').count() === 1, 'Falta Dentista');
        await page.screenshot({path: 'output/playwright/admin-' + kind + '.png', fullPage: true});
    });
    await check('ausencia de errores JavaScript y peticiones externas', async () => {
        ok(errors.length === 0, JSON.stringify(errors));
        ok(external.every(url => new URL(url).host === 'fonts.googleapis.com'), JSON.stringify(external));
    });
    await check('menú lateral se pliega y despliega', async () => {
        await page.locator('.btn-sidebar-toggle').click();
        ok(await page.locator('.sidebar').evaluate(el => el.classList.contains('collapsed')), 'No se plegó');
        await page.locator('.btn-sidebar-toggle').click();
        ok(await page.locator('.sidebar').evaluate(el => !el.classList.contains('collapsed')), 'No se desplegó');
    });
    await check('cerrar sesión borra acceso clínico', async () => {
        await page.getByRole('button', {name: 'Cerrar Sesión'}).click();
        await page.waitForURL('**/login/vistas/login.html');
        await page.goto(base + modulePath('dentista'));
        await page.waitForURL('**/login/vistas/login.html');
        ok(await page.evaluate(() => !localStorage.getItem('supabase_token')), 'Token retenido tras cerrar sesión');
        ok((await page.request.get(base + '/api/dentista')).status() === 401, 'API accesible sin sesión');
    });
    return {results, errors, httpErrors, external};
}
