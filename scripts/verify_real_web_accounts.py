"""Pruebas reales con las tres cuentas nuevas. Sin leer expedientes ni imprimir secretos."""
import contextlib
import io
import json
import logging
import os
from pathlib import Path
import sys

import requests
from dotenv import dotenv_values
from supabase import create_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
PRIVATE = Path(os.environ['LOCALAPPDATA']) / 'FORMADIG/security-activation'
CURRENT_STAGE = 'initialization'


def stage(value):
    global CURRENT_STAGE
    CURRENT_STAGE = value
    (ROOT / 'output/eleven-real-auth-progress.json').write_text(json.dumps({'stage': value}), encoding='utf-8')


def main():
    logging.disable(logging.CRITICAL)
    config = dotenv_values(ROOT / '.env')
    url = config['SUPABASE_URL'].rstrip('/')
    assert url == 'https://ctiqbycbkcftwuqgzxjb.supabase.co'
    for name in ('SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_ROLE_KEY'):
        os.environ[name] = config[name]
    with contextlib.redirect_stdout(io.StringIO()):
        from run import app
    app.config.update(TESTING=True, CLINICAL_ENABLE_UPDATES=False, CLINICAL_ENABLE_CREATION=False)
    assert 'CLINICAL_REPOSITORY_FACTORY' not in app.config
    client = app.test_client()
    accounts = json.loads((PRIVATE / 'CREDENCIALES_SUPABASE_REALES.private.json').read_text())
    result = {'mode': 'real_supabase_auth_local_flask', 'accounts': [], 'unexpected_failures': [],
              'known_security_blocks': [], 'clinical_records_read': False, 'ordinary_service_role_used': False}
    for account in accounts:
        role = account['role']
        stage(role + ':login')
        detail = {'role': role}
        # Login Flask real: SDK público y GetUser verificado en Supabase.
        login = client.post('/api/auth/login', json={'email': account['email'], 'password': account['password']})
        assert login.status_code == 200 and login.json['role'] == role
        token = login.json['session']['access_token']
        headers = {'Authorization': 'Bearer ' + token}
        assert client.get('/api/auth/me', headers=headers).json['role'] == role
        detail['flask_password_login_identity_profile'] = True
        stage(role + ':permissions')
        detail['area_capabilities'] = {}
        for area, expected in [('psicologia', 'psicologo'), ('dentista', 'dentista')]:
            allowed = role in ('admin', expected)
            response = client.get('/api/' + area + '/capacidades', headers=headers)
            assert response.status_code == (200 if allowed else 403)
            if allowed:
                assert response.json['data']['create'] is False and response.json['data']['update'] is False
            detail['area_capabilities'][area] = response.status_code
            if allowed:
                assert client.post('/api/' + area, headers=headers, json={}).status_code == 405
        if role != 'admin':
            detail['other_area_denials'] = {}
            for area in ('admin_usuarios', 'traslados', 'desayunos_frios', 'desayunos_calientes', 'espacios_eaeyd'):
                response = client.get('/api/' + area + '?role=admin', headers=dict(headers, **{'X-User-Role': 'admin'}))
                assert response.status_code == 403
                detail['other_area_denials'][area] = 403
        # No GET sin filtro de expedientes: limit=0 no retorna filas.
        detail['direct_rest'] = {}
        stage(role + ':direct_rest_no_rows')
        for table in ('modulo_psicologia', 'modulo_dental', 'traslados', 'desayunos_frios',
                      'desayunos_calientes', 'desayunos_eaeyd'):
            response = requests.get(url + '/rest/v1/' + table, headers=dict(headers, apikey=config['SUPABASE_KEY']),
                                    params={'select': 'id', 'limit': '0'}, timeout=(3, 15), allow_redirects=False)
            detail['direct_rest'][table] = response.status_code
            if table.startswith('modulo_'):
                assert response.status_code in (401, 403)
            elif role != 'admin' and response.status_code == 200:
                result['known_security_blocks'].append({'role': role, 'table': table,
                                                       'expected': 'denied', 'actual_status': 200,
                                                       'rows_returned': 0})
        if role != 'admin':
            stage(role + ':user_metadata_negative_and_restore')
            # Sólo la metadata editable de esta cuenta nueva; se restaura siempre.
            public = create_client(url, config['SUPABASE_KEY'])
            original = dict(public.auth.get_user(token).user.user_metadata or {})
            try:
                response = requests.put(url + '/auth/v1/user',
                                        headers=dict(headers, apikey=config['SUPABASE_KEY']),
                                        json={'data': dict(original, role='admin', rol='admin')},
                                        timeout=(3, 15), allow_redirects=False)
                assert response.status_code == 200
                assert client.get('/api/auth/me', headers=headers).json['role'] == role
                assert client.get('/api/admin_usuarios', headers=headers).status_code == 403
                detail['user_metadata_elevation_denied'] = True
            finally:
                # GoTrue fusiona metadata: NULL elimina claves que antes no existían.
                restored = dict(original)
                for name in ('role', 'rol'):
                    if name not in original:
                        restored[name] = None
                restored_response = requests.put(url + '/auth/v1/user',
                                                  headers=dict(headers, apikey=config['SUPABASE_KEY']),
                                                  json={'data': restored}, timeout=(3, 15), allow_redirects=False)
                assert restored_response.status_code == 200
            assert public.auth.get_user(token).user.user_metadata == original
        stage(role + ':logout')
        assert client.post('/api/auth/logout', headers=headers).status_code == 204
        # Refresh revocado: sesión nueva con clave pública y cierre local por el mismo endpoint.
        public = create_client(url, config['SUPABASE_KEY'])
        session = public.auth.sign_in_with_password({'email': account['email'], 'password': account['password']}).session
        assert client.post('/api/auth/logout', headers={'Authorization': 'Bearer ' + session.access_token}).status_code == 204
        response = requests.post(url + '/auth/v1/token', params={'grant_type': 'refresh_token'},
                                 headers={'apikey': config['SUPABASE_KEY']}, json={'refresh_token': session.refresh_token},
                                 timeout=(3, 15), allow_redirects=False)
        assert response.status_code in (400, 401, 403)
        detail['logout_refresh_rejected'] = True
        # Los JWT de acceso pueden durar hasta su expiración; no afirmar revocación inmediata.
        detail['access_jwt_after_logout_status'] = client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + session.access_token}).status_code
        result['accounts'].append(detail)
        (ROOT / 'output/eleven-real-auth-checkpoint.json').write_text(json.dumps(result), encoding='utf-8')
    assert client.get('/api/auth/me', headers={'Authorization': 'Bearer invalid'}).status_code == 401
    result['invalid_token_denied'] = True
    result['deployment_ready'] = not result['known_security_blocks']
    print(json.dumps(result))
    return result['deployment_ready']


if __name__ == '__main__':
    try:
        if not main():
            raise SystemExit(2)  # Diagnóstico completo, pero puerta de publicación cerrada.
    except Exception as error:
        print(json.dumps({'status': 'stopped', 'stage': CURRENT_STAGE, 'error_type': type(error).__name__, 'sensitive_details_omitted': True}))
        raise SystemExit(1)
