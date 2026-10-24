import importlib.util
import os
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from flask import Flask

FILE = Path(__file__).resolve().parents[1] / 'Formadig/1_Sistema_DIF_Acatlan/modulos/login/logica/login_backend.py'
spec = importlib.util.spec_from_file_location('login_under_test', FILE)
login = importlib.util.module_from_spec(spec)
spec.loader.exec_module(login)

class LoginSecurityTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.register_blueprint(login.auth_bp)
        self.client = app.test_client()

    def test_missing_configuration_names_only(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post('/api/auth/login', json={})
        self.assertEqual(response.status_code, 503)
        self.assertIn('SUPABASE_URL', response.json['error'])
        self.assertIn('SUPABASE_KEY', response.json['error'])

    def test_rejects_privileged_key(self):
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://example.supabase.co', 'SUPABASE_KEY': 'sb_secret_test'}):
            self.assertEqual(self.client.post('/api/auth/login', json={}).status_code, 503)

    def test_editable_metadata_cannot_grant_role(self):
        self.check_role({}, 403)

    def test_trusted_role_must_match_profile(self):
        self.check_role({'role': 'dentista'}, 403)

    def test_trusted_matching_role_synthetic_only(self):
        self.check_role({'role': 'admin'}, 200)

    def check_role(self, metadata, expected):
        client = MagicMock()
        client.auth.sign_in_with_password.return_value = SimpleNamespace(
            user=SimpleNamespace(id='00000000-0000-0000-0000-000000000001', app_metadata=metadata, user_metadata={'role': 'admin'}),
            session=SimpleNamespace(access_token='synthetic-token'))
        client.auth.get_user.return_value = SimpleNamespace(user=client.auth.sign_in_with_password.return_value.user)
        client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{'id': '00000000-0000-0000-0000-000000000001', 'rol': 'admin', 'nombre_completo': 'Synthetic'}]
        with patch.object(login, 'login_client', return_value=(client, None)):
            response = self.client.post('/api/auth/login', json={'email': 'synthetic@example.invalid', 'password': 'synthetic'})
        self.assertEqual(response.status_code, expected)

    def test_legacy_registration_disabled(self):
        self.assertEqual(self.client.post('/api/auth/register', json={'role': 'admin'}).status_code, 403)

    def test_clients_are_created_per_request(self):
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://example.supabase.co', 'SUPABASE_KEY': 'sb_publishable_test'}), patch.object(login, 'create_client') as create:
            login.login_client()
            login.login_client()
            self.assertEqual(create.call_count, 2)
