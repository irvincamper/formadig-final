// Navegador real con Auth real por Flask local. No captura credenciales ni trazas.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.argv[2]);
(async()=>{
 const accounts=JSON.parse(fs.readFileSync(path.join(process.env.LOCALAPPDATA,'FORMADIG','security-activation','CREDENCIALES_SUPABASE_REALES.private.json'),'utf8'));
 const browser=await chromium.launch({channel:'chrome',headless:true});
 const results=[]; const base=process.env.FORMADIG_VALIDATION_URL||'http://127.0.0.1:8054';
 try{
  for(const account of accounts){
   const context=await browser.newContext();
   await context.route('**/*',r=>new URL(r.request().url()).origin===base?r.continue():r.abort());
   const page=await context.newPage();
   let stage='login';
   try{
    await page.goto(base+'/modulos/login/vistas/login.html');
    await page.locator('#loginEmail').fill(account.email);
    await page.locator('#loginPassword').fill(account.password);
    await page.locator('#btnLogin').click();
    await page.waitForURL('**/dashboard.html',{timeout:45000});
    await page.waitForFunction(role=>localStorage.getItem('user_role')===role,account.role);
    const verifyMenu=async()=>{
     await page.waitForFunction(role=>{
      const menu=document.querySelector('#sidebarMenu')?.textContent;
      return localStorage.getItem('user_role')===role&&menu&&
       menu.includes('Usuarios')===(role==='admin')&&
       menu.includes('Psicología')===['admin','psicologo'].includes(role)&&
       menu.includes('Dentista')===['admin','dentista'].includes(role);
     },account.role);
     const menu=await page.locator('#sidebarMenu').textContent();
     if(menu.includes('Usuarios')!==(account.role==='admin'))throw new Error();
     if(menu.includes('Psicología')!==['admin','psicologo'].includes(account.role))throw new Error();
     if(menu.includes('Dentista')!==['admin','dentista'].includes(account.role))throw new Error();
    };
    stage='verified_initial_menu'; await verifyMenu();
    if(process.env.FORMADIG_CAPTURE_DASHBOARD==='true'){
     await page.setViewportSize({width:1365,height:900});
     await page.screenshot({path:path.join(__dirname,'../output/playwright/final-'+account.role+'-desktop.png'),fullPage:true});
     await page.setViewportSize({width:390,height:844});
     await page.evaluate(async()=>{await Promise.all(document.getAnimations().filter(a=>Number.isFinite(a.effect?.getComputedTiming().endTime)).map(a=>a.finished.catch(()=>{})));});
     await page.screenshot({path:path.join(__dirname,'../output/playwright/final-'+account.role+'-mobile.png'),fullPage:true,animations:'disabled'});
     await page.setViewportSize({width:1365,height:900});
    }
    const token=await page.evaluate(()=>localStorage.getItem('supabase_token'));
    const me=await page.request.get(base+'/api/auth/me',{headers:{Authorization:'Bearer '+token}});
    if(me.status()!==200||(await me.json()).role!==account.role)throw new Error();
    if(account.role!=='admin'){
     stage='manipulated_localStorage_revalidation';
     await page.evaluate(()=>localStorage.setItem('user_role','admin'));
     await page.reload();
     await page.waitForFunction(role=>localStorage.getItem('user_role')===role,account.role);
     await verifyMenu();
     const forbidden=await page.request.get(base+'/api/admin_usuarios?role=admin',{headers:{Authorization:'Bearer '+token,'X-User-Role':'admin'}});
     if(forbidden.status()!==403)throw new Error();
    }
    stage='remote_logout';
    const logoutResponse=page.waitForResponse(r=>r.url()===base+'/api/auth/logout'&&r.request().method()==='POST');
    await page.getByRole('button',{name:'Cerrar Sesión',exact:true}).click();
    if((await logoutResponse).status()!==204)throw new Error();
    await page.waitForURL('**/login/vistas/login.html');
    if(await page.evaluate(()=>Boolean(localStorage.getItem('supabase_token'))))throw new Error();
    stage='invalid_token';
    await page.evaluate(()=>{localStorage.setItem('supabase_token','invalid');localStorage.setItem('user_role','admin');});
    await page.goto(base+'/dashboard.html');
    await page.waitForURL('**/login/vistas/login.html');
    if(await page.evaluate(()=>Boolean(localStorage.getItem('supabase_token'))))throw new Error();
    results.push({role:account.role,passed:true,checks:['real_password_login','verified_identity','dashboard','role_menu','localStorage_cannot_grant_role','remote_logout','invalid_token_redirect']});
   }catch(_){results.push({role:account.role,passed:false,stage,sensitive_error_details_omitted:true});}
   finally{await context.close();}
  }
 }finally{await browser.close();}
 const output={mode:'real_browser_local_flask_real_supabase',results,clinical_records_read:false,render_tested:false};
 fs.writeFileSync(path.join(__dirname,'../output/',process.env.FORMADIG_BROWSER_REPORT||'eleven-real-browser.json'),JSON.stringify(output,null,2));
 console.log(JSON.stringify(output));
 if(results.some(r=>!r.passed))process.exitCode=1;
})().catch(()=>{console.error('La prueba real de navegador se detuvo; detalles sensibles omitidos.');process.exitCode=1;});
