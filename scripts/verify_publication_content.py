"""Busca valores privados conocidos en TODOS los blobs salientes, sin imprimirlos."""
import json
import os
from pathlib import Path
import subprocess
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]


def main():
    private=Path(os.environ['LOCALAPPDATA'])/'FORMADIG/security-activation'
    values=dotenv_values(ROOT/'.env')
    secrets=[]
    for name,value in values.items():
        if value and any(word in name for word in ('SECRET','TOKEN','PASSWORD','SERVICE_ROLE')):
            secrets.append(value.encode())
    accounts=json.loads((private/'CREDENCIALES_SUPABASE_REALES.private.json').read_text(encoding='utf-8-sig'))
    identifiers=[]
    for account in accounts:
        secrets.append(account['password'].encode())
        identifiers.extend(account[k].encode() for k in ('id','email') if account.get(k))
    approvals=json.loads((private/'APROBACION_11_USUARIOS.json').read_text(encoding='utf-8-sig'))
    for account in approvals['historical']:
        identifiers.extend(account[k].encode() for k in ('id','email') if account.get(k))
    lines=subprocess.check_output(['git','rev-list','--objects','origin/main..HEAD'],cwd=ROOT).splitlines()
    count=0
    for line in lines:
        oid=line.split(b' ',1)[0]
        if subprocess.check_output(['git','cat-file','-t',oid],cwd=ROOT).strip()!=b'blob':continue
        content=subprocess.check_output(['git','cat-file','blob',oid],cwd=ROOT)
        if any(value in content for value in secrets+identifiers):
            path=line.split(b' ',1)[-1].decode(errors='replace')
            category='secret' if any(value in content for value in secrets) else 'private_identifier'
            raise RuntimeError('Contenido privado detectado ('+category+') en '+path+'; no publicar')
        count+=1
    tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    assert not any(Path(f).name.startswith('.env') and Path(f).name!='.env.example' for f in tracked)
    print(json.dumps({'outgoing_blobs_checked':count,'known_secrets_or_private_account_identifiers':0}))


if __name__=='__main__':main()
