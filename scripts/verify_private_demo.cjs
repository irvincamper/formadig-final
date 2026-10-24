// Ejecuta la comprobación Playwright sin imprimir secretos ni generar trazas/capturas.
// El CLI no expone fs en su VM; el runner usa la misma dependencia ya instalada.
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const {chromium}=require(process.argv[2]);
(async()=>{
    const browser=await chromium.launch({channel:'chrome',headless:true});
    try{
        const context=await browser.newContext();
        const page=await context.newPage();
        const source=fs.readFileSync(path.join(__dirname,'../tests_clinical/visual_demo_accounts.js'),'utf8');
        const run=vm.runInNewContext('('+source+')',{require,process,URL});
        const results=await run(page);
        const target=path.join(__dirname,'../output/demo-users-browser.json');
        fs.writeFileSync(target,JSON.stringify(results,null,2));
        console.log(JSON.stringify(results));
        if(results.results.some(r=>!r.passed)||!results.invalid_session_denied)process.exitCode=1;
    }finally{await browser.close();}
})().catch(()=>{console.error('No se pudo completar la verificación privada. Detalles sensibles omitidos.');process.exitCode=1;});
