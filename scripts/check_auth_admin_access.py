"""Diagnóstico de sólo lectura. Nunca imprime claves, tokens ni respuestas Auth."""
import base64
import json
import logging
import os
from pathlib import Path
from importlib.metadata import version

import requests
from dotenv import dotenv_values
from supabase import create_client


def main():
    logging.disable(logging.CRITICAL)
    root = Path(__file__).resolve().parents[1]
    config = dotenv_values(root / '.env')
    target = 'https://ctiqbycbkcftwuqgzxjb.supabase.co'
    file_key = (config.get('SUPABASE_SERVICE_ROLE_KEY') or '').strip()
    process_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    effective_key = process_key if process_key is not None else file_key
    effective_url = os.environ.get('SUPABASE_URL', config.get('SUPABASE_URL', '')).rstrip('/')
    # Decodificación únicamente diagnóstica; no establece identidad ni autorización.
    claims = {}
    try:
        fragment = file_key.split('.')[1]
        claims = json.loads(base64.urlsafe_b64decode(fragment + '=' * (-len(fragment) % 4)))
    except (ValueError, IndexError, TypeError):
        pass
    inventory = Path(os.environ['LOCALAPPDATA']) / 'FORMADIG/security-activation/REVISION_ROLES_EXISTENTES.json'
    rows = json.loads(inventory.read_text(encoding='utf-8-sig'))['rows']
    user_id = rows[0]['auth_user_id']
    import uuid
    assert str(uuid.UUID(user_id)) == user_id
    result = {
        'project': 'ctiqbycbkcftwuqgzxjb',
        'file_url_matches': (config.get('SUPABASE_URL') or '').rstrip('/') == target,
        'file_key_present': bool(file_key),
        'file_key_new_secret_format': file_key.startswith('sb_secret_'),
        'file_key_legacy_service_role_claim': claims.get('role') == 'service_role',
        'file_key_legacy_project_claim_matches': claims.get('ref') == 'ctiqbycbkcftwuqgzxjb',
        'process_key_is_set': process_key is not None,
        'process_key_differs_from_file': process_key is not None and process_key != file_key,
        'effective_url_matches': effective_url == target,
        'sdk_version': version('supabase'),
        'mode': 'read_only_auth_admin_exact_inventory_user',
    }
    for label, key in [('file', file_key), ('effective', effective_key)]:
        if not key or (label == 'effective' and effective_url != target):
            result[label + '_probe'] = 'missing_or_wrong_project'
            continue
        try:
            response = requests.get(target + '/auth/v1/admin/users/' + user_id,
                                    headers={'apikey': key, 'Authorization': 'Bearer ' + key},
                                    timeout=(3, 15), allow_redirects=False)
            result[label + '_http_status'] = response.status_code
            result[label + '_identity_verified'] = response.status_code == 200 and response.json().get('id') == user_id
        except Exception as error:
            result[label + '_http_error_type'] = type(error).__name__
        try:
            client = create_client(target, key)
            user = client.auth.admin.get_user_by_id(user_id).user
            result[label + '_sdk_identity_verified'] = user.id == user_id
        except Exception as error:
            result[label + '_sdk_error_type'] = type(error).__name__
            status = getattr(error, 'status', None)
            if isinstance(status, int):
                result[label + '_sdk_status'] = status
    print(json.dumps(result, ensure_ascii=True))


if __name__ == '__main__':
    main()
