async (page) => {
    const base = 'http://127.0.0.1:8011';
    let role = 'admin', sessionStatus = 200;
    const results = [], errors = [];
    page.on('pageerror', e => errors.push(e.message));
    await page.context().route('**/*', route => {
        const url = new URL(route.request().url());
        if (url.origin !== base) return route.abort();
        if (url.pathname === '/api/auth/login') return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({role,nombre_completo:'Cuenta sintética',session:{access_token:'browser-synthetic'}})});
        if (url.pathname === '/api/auth/me') return route.fulfill({status:sessionStatus,contentType:'application/json',body:JSON.stringify({role,nombre_completo:'Cuenta sintética'})});
        return route.continue();
    });
    const ok = (value, message) => { if (!value) throw new Error(message); };
    for (role of ['admin','admin_traslados','admin_desayunos','psicologo','dentista']) {
        await page.goto(base + '/modulos/login/vistas/login.html');
        await page.evaluate(() => localStorage.clear());
        await page.locator('#loginEmail').fill('fixture@example.invalid');
        await page.locator('#loginPassword').fill('exclusivamente-sintetica');
        await page.locator('#btnLogin').click();
        await page.waitForURL('**/dashboard.html');
        await page.waitForFunction(role => localStorage.getItem('user_role') === role,role);
        const sidebar = await page.locator('#sidebarMenu').textContent();
        ok(sidebar.includes('Psicología') === ['admin','psicologo'].includes(role),'Psicología visible para ' + role);
        ok(sidebar.includes('Dentista') === ['admin','dentista'].includes(role),'Dental visible para ' + role);
        results.push({name:role+': login y dashboard con API simulada',passed:true});
    }
    role = 'dentista';
    await page.evaluate(() => localStorage.setItem('user_role','admin'));
    await page.goto(base + '/dashboard.html');
    await page.waitForFunction(() => localStorage.getItem('user_role') === 'dentista');
    await page.waitForFunction(() => !document.querySelector('#sidebarMenu')?.textContent.includes('Usuarios'));
    results.push({name:'rol manipulado se reemplaza por el verificado',passed:true});
    sessionStatus = 403;
    await page.goto(base + '/dashboard.html');
    await page.waitForURL('**/login/vistas/login.html');
    ok(await page.evaluate(() => !localStorage.getItem('supabase_token')),'Token retenido');
    results.push({name:'sesión revocada no conserva acceso al dashboard',passed:true});
    ok(errors.length === 0,JSON.stringify(errors));
    return {results,errors,scope:'Frontend real con respuestas Auth simuladas; no Supabase real'};
}
