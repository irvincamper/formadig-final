async (page) => {
    await page.route(url => url.pathname === '/api/dentista/', route => route.fulfill({status: 503,
        contentType: 'application/json', body: JSON.stringify({error: 'Fallo sintético de listado'})}), {times: 1});
    await page.locator('#search-form [name=q]').fill('ERROR-SINTETICO');
    await page.waitForFunction(() => document.querySelector('#status').textContent.includes('Fallo sintético'));
    return {status: await page.locator('#status').innerText(), rows: await page.locator('#results tr').count(),
        nextDisabled: await page.locator('#next').isDisabled(), previousDisabled: await page.locator('#previous').isDisabled()};
}
