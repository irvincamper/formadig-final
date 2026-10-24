"""Pruebas sintéticas: no credenciales, cuentas ni peticiones remotas."""
import importlib.util
import os
import re
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from clinical.security import WEB_ROLES, AreaClient, trusted_role
from clinical.validation import ClinicalError
from tests_clinical.fakes import ADMIN, PATIENT, synthetic_app


class WebSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://synthetic.supabase.co',
                                    'SUPABASE_KEY': 'sb_publishable_synthetic'}):
            spec = importlib.util.spec_from_file_location('web_security_app', Path(__file__).resolve().parents[1] / 'run.py')
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)
        fake, _ = synthetic_app()
        cls.module.app.config['CLINICAL_REPOSITORY_FACTORY'] = fake.config['CLINICAL_REPOSITORY_FACTORY']

    def setUp(self):
        env = patch.dict(os.environ, {'SUPABASE_URL': 'https://synthetic.supabase.co', 'SUPABASE_KEY': 'sb_publishable_synthetic'})
        env.start()
        self.addCleanup(env.stop)
        self.client = self.module.app.test_client()

    def test_identity_endpoint_all_five_roles(self):
        for role in WEB_ROLES:
            token = 'synthetic-admin' if role == 'admin' else role
            r = self.client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + token})
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r.json['role'], role)
            self.assertEqual(r.headers['Cache-Control'], 'no-store')
            self.assertNotIn(token, r.get_data(as_text=True) if token != role else '')

    def test_identity_endpoint_rejects_missing_expired_and_anonymous(self):
        self.assertEqual(self.client.get('/api/auth/me').status_code, 401)
        for token in ('expired', 'invalid', 'anonymous'):
            self.assertEqual(self.client.get('/api/auth/me', headers={'Authorization': 'Bearer ' + token}).status_code, 401)

    def test_role_requires_exact_identity_and_known_canonical_claim(self):
        for role in WEB_ROLES:
            identity = {'id': ADMIN, 'app_metadata': {'role': role}, 'user_metadata': {'role': 'admin'}}
            self.assertEqual(trusted_role(identity, {'id': ADMIN, 'rol': role}), role)
            for profile in (None, {'id': PATIENT, 'rol': role}, {'id': ADMIN, 'rol': 'usuario'}):
                with self.assertRaises(ClinicalError): trusted_role(identity, profile)
        for metadata in (None, [], {'role': ['admin']}, {'role': 'directora'}, {'role': 'ADMIN'}):
            with self.assertRaises(ClinicalError):
                trusted_role({'id': ADMIN, 'app_metadata': metadata, 'user_metadata': {'role': 'admin'}}, {'id': ADMIN, 'rol': 'admin'})

    def test_previous_modules_deny_forged_headers_and_cross_area(self):
        groups = {'traslados': {'admin','admin_traslados'}, 'desayunos_frios': {'admin','admin_desayunos'},
                  'desayunos_calientes': {'admin','admin_desayunos'}, 'espacios_eaeyd': {'admin','admin_desayunos'}}
        for module, allowed in groups.items():
            path = '/api/' + module
            self.assertEqual(self.client.get(path, headers={'X-User-Role': 'admin', 'X-User-Email': 'fake@example.invalid'}).status_code, 401)
            for role in WEB_ROLES - allowed:
                headers = {'Authorization': 'Bearer ' + role, 'X-User-Role': 'admin'}
                for rule in self.module.app.url_map.iter_rules():
                    if not rule.rule.startswith(path):
                        continue
                    target = re.sub(r'<[^>]+>', PATIENT, rule.rule)
                    for method in rule.methods - {'OPTIONS', 'HEAD'}:
                        r = self.client.open(target, method=method, headers=headers, json={})
                        self.assertEqual(r.status_code, 403, (module, role, method, target))

    def test_previous_module_reads_use_verified_jwt_and_ignore_role_header(self):
        for module, role in [('traslados','admin_traslados'), ('desayunos_frios','admin_desayunos'),
                             ('desayunos_calientes','admin_desayunos'), ('espacios_eaeyd','admin_desayunos')]:
            sdk = Mock()
            chain = sdk.table.return_value.select.return_value.order.return_value.limit.return_value
            chain.execute.return_value = SimpleNamespace(data=[])
            with patch('supabase.create_client', return_value=sdk):
                r = self.client.get('/api/' + module, headers={'Authorization': 'Bearer ' + role, 'X-User-Role': 'dentista'})
            self.assertEqual(r.status_code, 200, (module, r.json))
            sdk.postgrest.auth.assert_called_once_with(role)
            sdk.table.assert_called()

    def test_support_cannot_export_clinical_or_profile_tables(self):
        for role in ('synthetic-admin', 'dentista', 'psicologo'):
            for table in ('modulo_dental', 'modulo_psicologia', 'perfiles', 'auth.users'):
                sdk = Mock()
                with patch('supabase.create_client', return_value=sdk):
                    r = self.client.get('/api/chatbot/export?table=' + table,
                                        headers={'Authorization': 'Bearer ' + role})
                self.assertEqual(r.status_code, 403)
                sdk.table.assert_not_called()

    def test_support_rejects_requests_before_calling_external_services(self):
        for path, method in [('/api/chatbot/ask','POST'),('/api/chatbot/upload','POST'),
                             ('/api/sms/send','POST'),('/api/sms/history','GET')]:
            with patch('requests.post') as external:
                self.assertEqual(self.client.open(path, method=method, json={'role': 'admin'}).status_code, 401)
                external.assert_not_called()
        self.assertEqual(self.client.post('/api/sms/webhook', data={'Body':'SI'}).status_code, 503)
        self.assertEqual(self.client.post('/api/sms/send', headers={'Authorization':'Bearer admin_desayunos'},json={}).status_code, 403)

    def test_support_table_client_has_no_clinical_escape(self):
        for role in WEB_ROLES:
            sdk = Mock()
            client = AreaClient(sdk, role)
            for table in ('modulo_dental', 'modulo_psicologia', 'web_roles'):
                with self.assertRaises(ClinicalError): client.table(table)
            sdk.table.assert_not_called()
        sdk = Mock()
        with self.assertRaises(ClinicalError): AreaClient(sdk, 'dentista').table('traslados')
        sdk.table.assert_not_called()

    def test_sms_client_uses_public_key_even_if_admin_key_exists(self):
        sdk = Mock()
        with patch.dict(os.environ, {'SUPABASE_SERVICE_ROLE_KEY':'privileged-synthetic-value'}), \
             patch('supabase.create_client', return_value=sdk) as create:
            r = self.client.get('/api/sms/ping', headers={'Authorization':'Bearer synthetic-admin'})
        self.assertEqual(r.status_code,200)
        self.assertEqual(create.call_args.args,('https://synthetic.supabase.co','sb_publishable_synthetic'))

    def test_staff_update_preserves_mobile_owner_and_reports_sms_disabled(self):
        response=Mock(status_code=200)
        response.json.return_value=[{'id': PATIENT,'registrado_por':PATIENT,'estatus':'ACEPTADO'}]
        with patch('requests.patch',return_value=response) as update, patch('requests.get') as read:
            r=self.client.patch('/api/traslados/'+PATIENT,
                headers={'Authorization':'Bearer synthetic-admin'},json={'estatus':'ACEPTADO','registrado_por':ADMIN})
        self.assertEqual(r.status_code,200)
        self.assertEqual(r.json['data']['registrado_por'],PATIENT)
        self.assertEqual(r.json['sms_status'],'disabled')
        self.assertNotIn('registrado_por',update.call_args.kwargs['json'])
        self.assertEqual(update.call_args.kwargs['headers']['Authorization'],'Bearer synthetic-admin')
        read.assert_not_called()

    def test_admin_creation_records_verified_owner(self):
        sdk=Mock()
        sdk.table.return_value.insert.return_value.execute.return_value.data=[{'id':PATIENT}]
        with patch('supabase.create_client',return_value=sdk):
            r=self.client.post('/api/traslados',headers={'Authorization':'Bearer synthetic-admin'},
                json={'paciente_nombre':'Ficticio','paciente_curp':'FICTICIO','destino_hospital':'Hospital ficticio','fecha_viaje':'2026-10-24','hora_cita':'10:00','registrado_por':PATIENT})
        self.assertEqual(r.status_code,201)
        self.assertEqual(sdk.table.return_value.insert.call_args.args[0]['registrado_por'],ADMIN)

    def test_food_updates_preserve_owner_and_use_confirmed_document_columns(self):
        for module,table in [('desayunos_frios','desayunos_frios'),('desayunos_calientes','desayunos_calientes'),('espacios_eaeyd','desayunos_eaeyd')]:
            sdk=Mock(); chain=Mock(); sdk.table.return_value=chain
            for method in ('select','eq','limit'):
                getattr(chain,method).return_value=chain
            chain.execute.return_value.data=[{'id':PATIENT}]
            response=Mock(status_code=200)
            response.json.return_value=[{'id':PATIENT,'registrado_por':PATIENT}]
            with patch('supabase.create_client',return_value=sdk), patch('requests.patch',return_value=response) as update, patch('requests.get') as pre_read:
                r=self.client.patch('/api/'+module+'/'+PATIENT,headers={'Authorization':'Bearer admin_desayunos'},
                    json={'url_comprobante_salud':'https://example.invalid/salud.pdf','url_ine_tutor':'https://example.invalid/ine.pdf','registrado_por':ADMIN})
            self.assertEqual(r.status_code,200,(module,r.json))
            sdk.table.assert_called_once_with(table)
            update.assert_called_once(); pre_read.assert_not_called()
            payload=update.call_args.kwargs['json']
            self.assertEqual(set(payload),{'url_salud','url_ine'})
            self.assertNotIn('registrado_por',payload)
            self.assertEqual(update.call_args.kwargs['timeout'],(3,15))
            self.assertFalse(update.call_args.kwargs['allow_redirects'])
            self.assertEqual(update.call_args.kwargs['headers']['Authorization'],'Bearer admin_desayunos')


if __name__ == '__main__':
    unittest.main()
