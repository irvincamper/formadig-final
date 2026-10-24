// HTML/CSS/JS integrados reales; Auth y persistencia simulados para los cinco roles.
// No usa credenciales, no consulta datos productivos ni envía SMS/correos.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.argv[2]);
const base=process.env.FORMADIG_VALIDATION_URL||'http://127.0.0.1:8055';
const id='70000000-0000-0000-0000-000000000001',patient='70000000-0000-0000-0000-000000000002';
const record={id:patient,registrado_por:id,paciente_id:patient,atendido_por:id,
 nombres:'LAB SUPPORT',apellidos:'FICTICIO',nombre_beneficiario:'LAB SUPPORT FICTICIO',nombre_completo:'LAB SUPPORT FICTICIO',
 paciente_nombre:'LAB SUPPORT FICTICIO',curp:'FICTICIO',paciente_curp:'FICTICIO',telefono:'0000000000',
 telefono_principal:'0000000000',localidad:'LAB',estatus:'Pendiente',destino_hospital:'LAB',
 fecha_viaje:'2026-10-23',hora_cita:'10:00',fecha_solicitud:'2026-10-23T10:00:00Z',fecha_registro:'2026-10-23',
 motivo_consulta:'LAB ONLY',diagnostico_inicial:'LAB ONLY',diagnostico:'LAB ONLY',tipo_atencion:'Individual',
 estatus_caso:'Activo',fecha_sesion:'2026-10-23T10:00:00Z',fecha_atencion:'2026-10-23T10:00:00Z',
 numero_sesion:1,costo_recuperacion:'0.00',paciente:{nombre_completo:'LAB SUPPORT FICTICIO'}};
const modules=[['Usuarios','admin_usuarios','admin_usuarios','admin_usuarios'],
 ['Traslados','admin_traslados','admin_traslados','traslados'],
 ['Fríos','admin_desayunos_frios','admin_desayunos_frios','desayunos_frios'],
 ['Calientes','admin_desayunos_calientes','admin_desayunos_calientes','desayunos_calientes'],
 ['EAEyD','admin_espacios_eaeyd','admin_espacios_eaeyd','espacios_eaeyd'],
 ['Psicología','admin_psicologia','admin_psicologia','psicologia'],
 ['Dentista','admin_dentista','admin_dentista','dentista'],['Perfil','perfil','admin_perfil','profile']];
const allowed=(role,area)=>area==='profile'||role==='admin'||(role==='admin_traslados'&&area==='traslados')||
 (role==='admin_desayunos'&&['desayunos_frios','desayunos_calientes','espacios_eaeyd'].includes(area))||
 (role==='psicologo'&&area==='psicologia')||(role==='dentista'&&area==='dentista');
(async()=>{
 const browser=await chromium.launch({channel:'chrome',headless:true}); const results=[];
 try{
  for(const role of ['admin','admin_traslados','admin_desayunos','psicologo','dentista']){
   const context=await browser.newContext({viewport:{width:1365,height:900}});
   await context.routeWebSocket('**/*',socket=>socket.close());
   const token='eyJhbGciOiJub25lIn0.'+Buffer.from(JSON.stringify({sub:id,exp:4102444800,aud:'authenticated'})).toString('base64url')+'.synthetic';
   const profile={id,rol:role,nombre_completo:'LAB PROFILE',nombre_usuario:'LAB',telefono:'0000000000'};
   await context.addInitScript(({token,role})=>{localStorage.setItem('supabase_token',token);localStorage.setItem('user_role',role);localStorage.setItem('user_fullname','LAB PROFILE');},{token,role});
   await context.route('**/*',async route=>{
    const request=route.request(),url=new URL(request.url());
    const json=(body,status=200)=>route.fulfill({status,contentType:'application/json',body:JSON.stringify(body)});
    if(url.origin===base&&url.pathname.startsWith('/api/')){
     if(url.pathname==='/api/auth/me')return json({role,nombre_completo:profile.nombre_completo});
     if(url.pathname==='/api/auth/logout')return route.fulfill({status:204});
     const area=url.pathname.split('/')[2];
     if(!allowed(role,area))return json({error:'Rol no autorizado'},403);
     if(url.pathname.endsWith('/capacidades'))return json({data:{read:true,create:false,update:false,delete:false,role,module:area}});
     if(area==='admin_usuarios')return json({usuarios:[{...profile,email:'fixture@example.invalid'}],total:1});
     if(area==='traslados')return json(url.pathname.replace(/\/$/,'')==='/api/traslados'?{traslados:[record]}:record);
     if(['desayunos_frios','desayunos_calientes','espacios_eaeyd'].includes(area))return json(url.pathname.split('/').filter(Boolean).length===2?{desayunos:[record]}:record);
     if(['psicologia','dentista'].includes(area)){
      const q=url.searchParams.get('q')||'',offset=Number(url.searchParams.get('offset')||0);
      if(q==='WEB01_ERROR')return json({error:'WEB01 error simulado'},503);
      const rows=q==='WEB01_EMPTY'?[]:Array.from({length:30},(_,i)=>({...record,motivo_consulta:'WEB01 FICTICIO '+(i+1)}));
      return json({data:rows.slice(offset,offset+25),pagination:{limit:25,offset,has_more:offset+25<rows.length}});
     }
     return json([]);
    }
    if(url.hostname==='ctiqbycbkcftwuqgzxjb.supabase.co'){
     if(url.pathname==='/auth/v1/user')return json({id,aud:'authenticated',role:'authenticated',email:'fixture@example.invalid',app_metadata:{role},user_metadata:{},is_anonymous:false});
     if(url.pathname==='/rest/v1/perfiles'){
      if(request.method()==='PATCH'){Object.assign(profile,request.postDataJSON());return json([{id}]);}
      return json((request.headers()['accept']||'').includes('object')?profile:[profile]);
     }
     return route.abort();
    }
    if(url.origin===base)return route.continue();
    if(['cdn.jsdelivr.net','cdnjs.cloudflare.com','fonts.googleapis.com','fonts.gstatic.com'].includes(url.hostname))return route.continue();
    return route.abort();
   });
   const page=await context.newPage(); const errors=[];
   page.on('pageerror',e=>errors.push(e.message.replaceAll(token,'[synthetic token]')));
   for(const [name,folder,file,area] of [['Dashboard',null,null,'dashboard'],...modules.filter(m=>allowed(role,m[3]))]){
    let stage='navigation';
    try{
     const url=folder?base+'/modulos/'+folder+'/vistas/'+file+'.html':base+'/dashboard.html';
     await page.goto(url);
     await page.locator('#sidebarMenu').waitFor({state:'attached'});
     stage='data_and_form';
     if(folder&&area!=='profile')await page.waitForFunction(()=>document.querySelectorAll('tbody tr').length>0);
     if(area==='profile')await page.waitForFunction(()=>document.querySelector('#displayNombre')?.textContent==='LAB PROFILE');
     const controls=await page.locator('input,select,textarea').count();
     if(folder&&controls===0)throw new Error('Form controls missing');
     if(area==='profile'){
      await page.locator('#btnOpenEditData').click();
      await page.locator('#editNombre').fill('LAB EDITED');
      await page.locator('#editTelefono').fill('0000000000');
      await page.locator('#formData button[type=submit]').click();
      await page.waitForFunction(()=>document.querySelector('#displayNombre')?.textContent==='LAB EDITED');
      profile.nombre_completo='LAB PROFILE';
     }
     if(['psicologia','dentista'].includes(area)){
      stage='pagination_search_errors';
      await page.locator('#next:not([disabled])').waitFor();
      await page.locator('#next').click();
      await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('Página 2'));
      if(await page.locator('#results tr').count()!==5)throw new Error('Second page must show five synthetic rows');
      await page.locator('#search-form input[name=q]').fill('WEB01_EMPTY');
      await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('0 atenciones'));
      await page.locator('#search-form input[name=q]').fill('WEB01_ERROR');
      await page.waitForFunction(()=>document.querySelector('#status')?.dataset.error==='true');
      if(!(await page.locator('#status').textContent()).includes('WEB01 error simulado'))throw new Error('Missing server error state: '+await page.locator('#status').textContent());
      await page.locator('#search-form input[name=q]').fill('');
      await page.waitForFunction(()=>document.querySelector('#status')?.textContent.includes('25 atenciones'));
     }
     stage='responsive';
     for(const [width,height] of [[1365,900],[1024,768],[768,1024],[390,844]]){
     await page.setViewportSize({width,height});
     await page.evaluate(async()=>{await Promise.all(document.getAnimations().filter(a=>Number.isFinite(a.effect?.getComputedTiming().endTime)).map(a=>a.finished.catch(()=>{})));});
     const metrics=await page.evaluate(()=>({viewport:innerWidth,width:Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)}));
     const responsive=metrics.width<=metrics.viewport+1;
     if(!responsive)throw new Error('Horizontal page overflow: '+metrics.width);
     }
     if(role==='admin')await page.screenshot({path:path.join(__dirname,'../output/playwright/integrated-fixture-'+area+'-mobile.png'),fullPage:true});
     await page.setViewportSize({width:1365,height:900});
     results.push({role,module:name,passed:true,controls,responsive:true,resolutions:[1365,1024,768,390]});
    }catch(e){results.push({role,module:name,passed:false,stage,error:e.message.replaceAll(token,'[synthetic token]')});await page.setViewportSize({width:1365,height:900});}
   }
   if(errors.length)results.push({role,module:'javascript_runtime',passed:false,errors});
   await context.close();
  }
 }finally{await browser.close();}
 const output={scope:'HTML/CSS/JS integrados; cinco roles con Auth y datos simulados; sin persistencia remota',results};
 fs.writeFileSync(path.join(__dirname,'../output/final-integrated-ui.json'),JSON.stringify(output,null,2));
 console.log(JSON.stringify({checks:results.length,passed:results.filter(r=>r.passed).length,failures:results.filter(r=>!r.passed)}));
 if(results.some(r=>!r.passed))process.exitCode=1;
})().catch(e=>{console.error('UI fixture runner stopped: '+e.name);process.exitCode=1;});
