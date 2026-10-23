async (page) => {
    const fs=require('node:fs');
    const path=require('node:path');
    const credentials=JSON.parse(fs.readFileSync(path.join(process.env.LOCALAPPDATA,'FORMADIG','demo-web-accounts','credentials.private.json'),'utf8'));
    const base='http://127.0.0.1:8053',results=[];
    await page.context().route('**/*',route=>new URL(route.request().url()).origin===base?route.continue():route.abort());
    for(const account of credentials){
        try{
            await page.goto(base+'/modulos/login/vistas/login.html');
            await page.locator('#loginEmail').fill(account.email);
            await page.locator('#loginPassword').fill(account.temporary_password);
            await page.locator('#btnLogin').click();
            await page.waitForURL('**/dashboard.html');
            const token=await page.evaluate(()=>localStorage.getItem('supabase_token'));
            const me=await page.request.get(base+'/api/auth/me',{headers:{Authorization:'Bearer '+token}});
            if(me.status()!==200||(await me.json()).role!==account.role)throw new Error('identity');
            const sidebar=await page.locator('#sidebarMenu').textContent();
            if(sidebar.includes('Usuarios')!==(account.role==='admin'))throw new Error('menu');
            if(sidebar.includes('Psicología')!==['admin','psicologo'].includes(account.role))throw new Error('menu');
            if(sidebar.includes('Dentista')!==['admin','dentista'].includes(account.role))throw new Error('menu');
            for(const area of ['traslados','desayunos_frios','desayunos_calientes','espacios_eaeyd','admin_usuarios','psicologia','dentista']){
                const allowed=account.role==='admin'||(account.role==='psicologo'&&area==='psicologia')||account.role===area;
                const r=await page.request.get(base+'/api/'+area,{headers:{Authorization:'Bearer '+token}});
                if(r.status()!==(allowed?200:403))throw new Error('authorization');
            }
            if(account.role!=='admin'){
                const area=account.role==='psicologo'?'psicologia':'dentista';
                await page.goto(base+'/modulos/admin_'+area+'/vistas/admin_'+area+'.html');
                await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('atenciones. Página'));
            }
            await page.getByRole('button',{name:'Cerrar Sesión',exact:true}).click();
            await page.waitForURL('**/login/vistas/login.html');
            const invalid=await page.request.get(base+'/api/auth/me',{headers:{Authorization:'Bearer '+token}});
            if(invalid.status()!==401)throw new Error('logout');
            results.push({role:account.role,passed:true,checks:['login','identity','dashboard','menu','operation_matrix','logout_revocation']});
        }catch(_){results.push({role:account.role,passed:false,error:'Falló una comprobación; detalles sensibles omitidos.'});}
    }
    const invalid=await page.request.get(base+'/api/auth/me',{headers:{Authorization:'Bearer invalid'}});
    return {mode:'synthetic-local-only',results,invalid_session_denied:invalid.status()===401,real_supabase_auth:false};
}
