"""Tres cuentas locales de demostración. Sin conexión a Supabase/Render."""
import json
import secrets
import time
from pathlib import Path
from flask import jsonify, request, Response
from werkzeug.security import check_password_hash
from clinical.security import request_identity
from clinical.validation import ClinicalError
from tests_clinical.fakes import synthetic_app, FakeRepository, sample, PATIENT


def build_demo(accounts):
    root=Path(__file__).resolve().parents[1]/'Formadig/1_Sistema_DIF_Acatlan'
    app,store=synthetic_app(str(root))
    app.config.update(CLINICAL_ENABLE_UPDATES=False,CLINICAL_ENABLE_CREATION=False)
    sessions={}
    def factory(token):
        entry=sessions.get(token)
        if not entry or entry['expires']<=time.time():
            raise ClinicalError('UNAUTHENTICATED','Sesión local inválida o expirada.',401)
        account=entry['account']
        class Repository(FakeRepository):
            def identity(self): return {'id':account['id'],'app_metadata':{'role':account['role']},'is_anonymous':False}
            def profile(self,user_id):
                return {'id':account['id'],'rol':account['role'],'nombre_completo':'DEMO LOCAL '+account['role']} if user_id==account['id'] else None
        return Repository(account['role'],store)
    app.config['CLINICAL_REPOSITORY_FACTORY']=factory
    for kind in store:
        store[kind]['00000000-0000-0000-0000-000000000003']=dict(sample(kind),id='00000000-0000-0000-0000-000000000003',paciente={'nombre_completo':'Paciente ficticio'},paciente_id=PATIENT)
    @app.after_request
    def local_only(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-FORMADIG-Environment']='synthetic-local-only'
        response.headers['Content-Security-Policy']="connect-src 'self'; form-action 'self'; object-src 'none'; base-uri 'self'"
        return response
    @app.errorhandler(ClinicalError)
    def error(e): return jsonify(error=e.message,code=e.code),e.status
    @app.get('/')
    def index():
        from flask import redirect
        return redirect('/modulos/login/vistas/login.html')
    @app.post('/api/auth/login')
    def login():
        data=request.get_json(silent=True)
        if not isinstance(data,dict) or not isinstance(data.get('password'),str):
            return jsonify(error='Credenciales locales requeridas.'),400
        account=next((a for a in accounts if a['email']==data.get('email')),None)
        if not account or not check_password_hash(account['password_hash'],data['password']):
            return jsonify(error='Credenciales locales inválidas.'),401
        token=secrets.token_urlsafe(32)
        sessions[token]={'account':account,'expires':time.time()+3600}
        return jsonify(role=account['role'],nombre_completo='DEMO LOCAL '+account['role'],session={'access_token':token})
    @app.get('/api/auth/me')
    def me():
        token,identity,profile,role=request_identity()
        return jsonify(role=role,nombre_completo=profile['nombre_completo'])
    @app.post('/api/auth/logout')
    def logout():
        token,identity,profile,role=request_identity()
        sessions.pop(token,None)
        return '',204
    @app.get('/core/formadig-core.js')
    def core():
        source=(root/'core/formadig-core.js').read_text(encoding='utf8')
        source+='''\nconst demoOriginalLogout=Auth.logout.bind(Auth);
Auth.logout=async function(){const t=localStorage.getItem('supabase_token');
try{if(t)await fetch('/api/auth/logout',{method:'POST',headers:{Authorization:'Bearer '+t}});}
finally{demoOriginalLogout();}};'''
        return Response(source,mimetype='application/javascript')
    # Superficie administrativa simulada; reutiliza identidad y reglas del backend web.
    permissions={'traslados':('admin','admin_traslados'),'desayunos_frios':('admin','admin_desayunos'),
                 'desayunos_calientes':('admin','admin_desayunos'),'espacios_eaeyd':('admin','admin_desayunos'),
                 'admin_usuarios':('admin',)}
    def admin_result(module):
        token,identity,profile,role=request_identity()
        if role not in permissions[module]: return jsonify(error='Área no autorizada.'),403
        if request.method!='GET': return jsonify(error='Demo de consulta; escritura administrativa bloqueada.'),405
        if module=='admin_usuarios': return jsonify(usuarios=[],total=0)
        return jsonify({module:[]})
    for module in permissions:
        app.add_url_rule('/api/'+module,endpoint='demo_'+module,
                         view_func=lambda module=module:admin_result(module),methods=['GET','POST','PATCH','DELETE'],strict_slashes=False)
    return app


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accounts',type=Path,required=True)
    parser.add_argument('--port',type=int,default=8053)
    args=parser.parse_args()
    app=build_demo(json.loads(args.accounts.read_text(encoding='utf8')))
    app.run(host='127.0.0.1',port=args.port,debug=False,use_reloader=False)
