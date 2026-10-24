"""Prueba POSTERIOR al corte, sólo Auth y SELECT de UUID WEB01 reservados.

No inserta registros, no usa Auth Admin ni service_role. Requiere seed previamente
aprobado. No ejecutar mientras B/legacy estén pendientes. Nunca descarga expedientes.
"""
import argparse
import json
import os
from pathlib import Path
import requests
from dotenv import dotenv_values
from supabase import create_client

ROOT=Path(__file__).resolve().parents[1]
TABLES=['traslados','desayunos_frios','desayunos_calientes','desayunos_eaeyd','modulo_psicologia','modulo_dental']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--after-cutover',action='store_true',required=True)
    p.add_argument('--base-url',choices=['https://formadig-app.onrender.com','http://127.0.0.1:8056'],required=True)
    args=p.parse_args()
    config=dotenv_values(ROOT/'.env')
    url=config['SUPABASE_URL'].rstrip('/')
    if url!='https://ctiqbycbkcftwuqgzxjb.supabase.co':raise RuntimeError('Proyecto inesperado')
    key=config['SUPABASE_KEY']
    if key==config.get('SUPABASE_SERVICE_ROLE_KEY'):raise RuntimeError('Requiere clave pública')
    credentials=json.loads((Path(os.environ['LOCALAPPDATA'])/'FORMADIG/security-activation/CREDENCIALES_SUPABASE_REALES.private.json').read_text(encoding='utf-8-sig'))
    results=[]
    for account in credentials:
        client=create_client(url,key)
        try:
            session=client.auth.sign_in_with_password({'email':account['email'],'password':account['password']}).session
            assert session
            token=session.access_token
            verified=client.auth.get_user(token).user
            assert verified.app_metadata.get('role')==account['role']
            headers={'Authorization':'Bearer '+token,'apikey':key}
            me=requests.get(args.base_url+'/api/auth/me',headers=headers,timeout=90)
            assert me.status_code==200 and me.json()['role']==account['role']
            for batch,table in enumerate(TABLES,1):
                ids=','.join('75000000-0000-0000-'+str(batch).zfill(4)+'-'+str(i).zfill(12) for i in range(1,31))
                r=requests.get(url+'/rest/v1/'+table,headers=headers,
                               params={'select':'id','id':'in.('+ids+')'},timeout=20)
                assert r.status_code==200
                allowed=account['role']=='admin' and batch<=4 or account['role']=='psicologo' and batch==5 or account['role']=='dentista' and batch==6
                assert len(r.json())==(30 if allowed else 0), (account['role'],table,'unexpected fixture count')
                results.append({'role':account['role'],'table':table,'expected_fixture_rows':30 if allowed else 0,'passed':True})
        finally:
            client.auth.sign_out()
    print(json.dumps({'scope':'real Auth and SELECT id limited to controlled WEB01 fixture UUIDs','results':results}))


if __name__=='__main__':main()
