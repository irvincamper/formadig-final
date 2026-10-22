async (page) => {
    const results = [];
    for (const [role, kind] of [['psicologo', 'psicologia'], ['dentista', 'dentista']]) {
        await page.goto('http://127.0.0.1:8011/demo');
        await page.locator('[data-role="' + role + '"]').click();
        await page.goto('http://127.0.0.1:8011/modulos/admin_' + kind + '/vistas/admin_' + kind + '.html');
        await page.waitForFunction(() => document.querySelector('#status').textContent.includes('atenciones. Página'));
        await page.locator('#new-attention').click();
        const form = page.locator('#attention-form');
        await form.locator('[name=paciente_id]').fill('00000000-0000-0000-0000-000000000002');
        await form.locator('[name=motivo_consulta]').fill('VALIDACION-NUMERICA-SINTETICA');
        if (kind === 'psicologia') await form.locator('[name=tipo_atencion]').fill('Prueba sintética');
        const numeric = form.locator('[name=' + (kind === 'psicologia' ? 'numero_sesion' : 'costo_recuperacion') + ']');
        let posts = 0;
        const listener = request => { if (request.method() === 'POST') posts++; };
        page.on('request', listener);
        const cases = kind === 'psicologia' ? ['-1', '1.5'] : ['-1', '0.001'];
        for (const value of cases) {
            await numeric.fill(value); await form.locator('[type=submit]').click();
            const valid = await form.evaluate(form => form.checkValidity());
            results.push({name: kind + ': valor numérico inválido ' + value, passed: !valid && posts === 0});
        }
        page.off('request', listener);
        await page.locator('#search-form [name=desde]').fill('fecha-invalida');
        const response = page.waitForResponse(r => r.url().includes('/api/' + kind + '/') && r.status() === 400);
        await page.locator('#search-form [type=submit]').click(); await response;
        await page.waitForFunction(() => document.querySelector('#status').dataset.error === 'true');
        results.push({name: kind + ': filtro temporal inválido muestra HTTP 400', passed: await page.locator('#status').innerText().then(t => t.includes('Fecha inválida'))});
    }
    const favicon = await page.request.get('http://127.0.0.1:8011/favicon.ico');
    results.push({name: 'favicon de demostración sin 404', passed: favicon.status() === 204});
    return {results, browser: page.context().browser().browserType().name(), version: page.context().browser().version()};
}
