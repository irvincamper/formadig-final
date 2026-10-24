"""Aprovisionamiento autorizado: Auth Admin, sin SQL de escritura ni salida de secretos.

El manifiesto y las contraseñas sólo se guardan en el directorio privado de Windows.
Por defecto verifica; --apply permite las altas/roles explícitos del manifiesto revisado.
"""
import argparse
import json
import logging
import os
from pathlib import Path
import secrets
import subprocess
import uuid

from dotenv import dotenv_values
from supabase import create_client

ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'ctiqbycbkcftwuqgzxjb'
ROLES = {'admin', 'admin_traslados', 'admin_desayunos', 'psicologo', 'dentista'}
PRIVATE = Path(os.environ['LOCALAPPDATA']) / 'FORMADIG/security-activation'


def sql_read(query):
    result = subprocess.run(['npx.cmd' if os.name == 'nt' else 'npx', '--yes',
                             'supabase', 'db', 'query', '--linked', query], cwd=ROOT,
                            capture_output=True, text=True, encoding='utf-8', timeout=60,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    if result.returncode:
        raise RuntimeError('CLI_READ_FAILED')
    return json.loads(result.stdout)['rows']


def literal(value):
    return "'" + value.replace("'", "''") + "'"


def account_state(ids, emails=()):
    predicates = []
    if ids:
        predicates.append('u.id IN (' + ','.join(literal(str(uuid.UUID(i))) for i in ids) + ')')
    if emails:
        predicates.append('u.email IN (' + ','.join(literal(e) for e in emails) + ')')
    return sql_read('SELECT u.id,u.email,u.raw_app_meta_data->>\'role\' AS auth_role,'
                    'p.id AS profile_id,p.rol AS profile_role,r.role AS protected_role '
                    'FROM auth.users u LEFT JOIN public.perfiles p ON p.id=u.id '
                    'LEFT JOIN formadig_private.web_roles r ON r.user_id=u.id WHERE '
                    + ' OR '.join(predicates))


def save_private(path, value):
    temporary = path.with_suffix(path.suffix + '.pending')
    temporary.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temporary.replace(path)


def main():
    logging.disable(logging.CRITICAL)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    config = dotenv_values(ROOT / '.env')
    assert config['SUPABASE_URL'].rstrip('/') == f'https://{PROJECT}.supabase.co'
    assert (ROOT / 'supabase/.temp/project-ref').read_text().strip() == PROJECT
    manifest = json.loads((PRIVATE / 'APROBACION_11_USUARIOS.json').read_text(encoding='utf-8'))
    assert manifest['project_ref'] == PROJECT
    old, new = manifest['historical'], manifest['new']
    assert len(old) == 8 and len(new) == 3 and len({u['id'] for u in old}) == 8
    assert {u['role'] for u in new} == {'admin', 'psicologo', 'dentista'}
    assert all(u['role'] in ROLES for u in old + new)
    admin = create_client(config['SUPABASE_URL'], config['SUPABASE_SERVICE_ROLE_KEY']).auth.admin
    states = account_state([u['id'] for u in old], [u['email'] for u in new])
    indexed = {u['id']: u for u in states}
    before = []
    for approved in old:
        row = indexed[approved['id']]
        assert row['email'] == approved['email'] and row['profile_id'] == approved['id']
        assert row['profile_role'] == approved['role']
        user = admin.get_user_by_id(approved['id']).user
        assert user.id == approved['id'] and user.email == approved['email']
        before.append({'id': user.id, 'app_metadata': dict(user.app_metadata or {})})
    if not args.apply:
        print(json.dumps({'mode': 'read_only', 'historical_matches': len(before),
                          'new_identities_already_present': sum(r['email'] in {u['email'] for u in new} for r in states)}))
        return
    # Snapshot antes del primer cambio. Nunca sobrescribir el original al reintentar.
    backup = PRIVATE / 'AUTH_METADATA_ANTES_APROVISIONAMIENTO.json'
    if not backup.exists():
        save_private(backup, before)
    for approved, previous in zip(old, before):
        metadata = dict(previous['app_metadata'])
        metadata['role'] = approved['role']
        if previous['app_metadata'].get('role') != approved['role']:
            admin.update_user_by_id(approved['id'], {'app_metadata': metadata})
        fresh = admin.get_user_by_id(approved['id']).user
        assert fresh.id == approved['id'] and fresh.email == approved['email']
        assert fresh.app_metadata == metadata
    credentials_path = PRIVATE / 'CREDENCIALES_SUPABASE_REALES.private.json'
    credentials = json.loads(credentials_path.read_text()) if credentials_path.exists() else []
    for approved in new:
        matches = account_state([], [approved['email']])
        saved = next((v for v in credentials if v['email'] == approved['email']), None)
        if matches:
            assert len(matches) == 1 and saved is not None, 'EXISTING_IDENTITY_REQUIRES_REVIEW'
            assert matches[0]['auth_role'] == approved['role'], 'EXISTING_ROLE_REQUIRES_REVIEW'
            saved['id'] = matches[0]['id']
            saved['status'] = 'created'
        else:
            if saved is None:
                saved = dict(approved, password=secrets.token_urlsafe(30), status='pending')
                credentials.append(saved)
                save_private(credentials_path, credentials)
            # No invitación, generate_link ni correo saliente: confirmación por administrador.
            created = admin.create_user({'email': approved['email'], 'password': saved['password'],
                                        'email_confirm': True,
                                        'app_metadata': {'role': approved['role'], 'formadig_test': True},
                                        'user_metadata': {'nombre_usuario': 'formadig_test_' + approved['role'],
                                                          'nombre_completo': 'FORMADIG Prueba ' + approved['role'],
                                                          'apellidos': 'Prueba académica'}}).user
            saved.update(id=created.id, status='created')
        save_private(credentials_path, credentials)
    all_accounts = old + credentials
    final = {r['id']: r for r in account_state([u['id'] for u in all_accounts])}
    results = []
    for approved in all_accounts:
        row = final[approved['id']]
        fresh = admin.get_user_by_id(approved['id']).user
        assert row['email'] == approved['email'] and fresh.id == approved['id']
        assert row['profile_id'] == approved['id']
        assert row['auth_role'] == row['profile_role'] == row['protected_role'] == approved['role']
        results.append({'role': approved['role'], 'historical': approved in old, 'verified': True})
    lines = ['FORMADIG — SUPABASE DIF REAL',
             'Entrega privada local. No copiar a Git, informes, chat, capturas ni logs.',
             'Credenciales temporales de prueba; no se enviaron correos.', '']
    for account in credentials:
        lines.extend(['Rol: ' + account['role'], 'Correo: ' + account['email'],
                      'Contraseña temporal: ' + account['password'], ''])
    (PRIVATE / 'CREDENCIALES_SUPABASE_REALES.txt').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'mode': 'real_supabase_auth_admin', 'historical_preserved': 8,
                      'new_verified': 3, 'identity_profile_registry_verified': 11,
                      'passwords_historical_changed': False, 'emails_sent': False, 'results': results}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Nunca imprimir str(error): un proveedor puede incluir cuerpos de solicitud.
        print(json.dumps({'status': 'stopped', 'error_type': type(error).__name__,
                          'action': 'review_private_state_before_retry'}))
        raise SystemExit(1)
