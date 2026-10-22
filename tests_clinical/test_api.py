import importlib.util
import os
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch
from clinical.validation import SCHEMAS, validate_payload
from tests_clinical.fakes import ADMIN, PATIENT, RECORD, sample, synthetic_app


class ClinicalAPITests(unittest.TestCase):
    def setUp(self):
        self.app, self.store = synthetic_app()
        self.client = self.app.test_client()
        self.headers = {'Authorization': 'Bearer synthetic-admin'}
        network = patch('requests.sessions.Session.request', side_effect=AssertionError('No usar red en pruebas'))
        network.start(); self.addCleanup(network.stop)

    def seed(self, kind):
        payload = validate_payload(kind, sample(kind))
        payload['atendido_por'] = ADMIN
        return self.app.config['CLINICAL_REPOSITORY_FACTORY']('synthetic-admin').create(kind, payload)

    def test_read_role_matrix_and_forged_headers(self):
        for kind in SCHEMAS:
            for token, expected in [(None, 401), ('invalid', 401), ('expired', 401), ('anonymous', 401),
                                    ('admin_desayunos', 403), ('admin_traslados', 403), ('usuario', 403),
                                    ('directora', 403), ('desarrollador', 403), ('missing', 403),
                                    ('psicologo', 200 if kind == 'psicologia' else 403),
                                    ('dentista', 200 if kind == 'dentista' else 403), ('synthetic-admin', 200)]:
                headers = {'X-User-Role': 'admin'}
                if token: headers['Authorization'] = 'Bearer ' + token
                for path in ('', '/capacidades', '/pacientes/' + PATIENT + '/historial'):
                    with self.subTest(kind=kind, token=token, path=path):
                        response = self.client.get('/api/' + kind + path, headers=headers)
                        self.assertEqual(response.status_code, expected, response.json)
                        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_role_requires_trusted_claim_not_editable_metadata(self):
        from clinical.api import authorize
        for kind, role in [('psicologia', 'psicologo'), ('dentista', 'dentista')]:
            profile = {'id': ADMIN, 'rol': role}
            self.assertFalse(authorize({'id': ADMIN, 'user_metadata': {'role': role}}, profile, kind))
            self.assertFalse(authorize({'id': ADMIN, 'app_metadata': {'role': 'usuario'}}, profile, kind))
            self.assertTrue(authorize({'id': ADMIN, 'app_metadata': {'role': role}}, profile, kind))

    def test_creation_only_in_explicit_synthetic_mode(self):
        self.app.config['CLINICAL_ENABLE_CREATION'] = True
        for kind in SCHEMAS:
            self.assertEqual(self.client.post('/api/' + kind, headers=self.headers, json=sample(kind)).status_code, 405)
        self.app.config['CLINICAL_SYNTHETIC_MODE'] = True
        for kind, role in [('psicologia', 'psicologo'), ('dentista', 'dentista')]:
            headers = {'Authorization': 'Bearer ' + role}
            path = '/api/' + kind
            self.assertEqual(self.client.post(path, headers=headers, json=dict(sample(kind), atendido_por=PATIENT)).status_code, 400)
            self.assertEqual(self.client.post(path, headers=headers, json={'paciente_id': 'invalido'}).status_code, 400)
            response = self.client.post(path, headers=headers, json=sample(kind))
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['data']['atendido_por'], ADMIN)
            self.assertEqual(self.client.get(path, headers=headers).json['data'], [response.json['data']])
            other = 'dentista' if role == 'psicologo' else 'psicologo'
            self.assertEqual(self.client.post(path, headers={'Authorization': 'Bearer ' + other}, json=sample(kind)).status_code, 403)

    def test_no_web_creation_or_deletion(self):
        for kind in SCHEMAS:
            base = '/api/' + kind
            for token in ('synthetic-admin', ('psicologo' if kind == 'psicologia' else 'dentista')):
                headers = {'Authorization': 'Bearer ' + token}
                self.assertEqual(self.client.post(base, headers=headers, json=sample(kind)).status_code, 405)
                self.assertEqual(self.client.delete(base + '/' + RECORD, headers=headers).status_code, 405)
                capabilities = self.client.get(base + '/capacidades', headers=headers).json['data']
                self.assertFalse(capabilities['create'])
                self.assertFalse(capabilities['delete'])
            self.assertEqual(self.store[kind], {})

    def test_list_detail_history_search_and_pagination(self):
        for kind in SCHEMAS:
            row = self.seed(kind); base = '/api/' + kind
            response = self.client.get(base + '?q=sintética&limit=1', headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['data'], [row])
            self.assertFalse(response.json['pagination']['has_more'])
            self.assertEqual(self.client.get(base + '/' + row['id'], headers=self.headers).json['data'], row)
            self.assertEqual(self.client.get(base + '/pacientes/' + PATIENT + '/historial', headers=self.headers).json['data'], [row])
            self.assertEqual(self.client.get(base + '?q=noexiste', headers=self.headers).json['data'], [])
            self.assertEqual(self.client.get(base + '?offset=1', headers=self.headers).json['data'], [])
            self.seed(kind)
            self.assertTrue(self.client.get(base + '?limit=1', headers=self.headers).json['pagination']['has_more'])

    def test_invalid_filters_uuid_and_dates(self):
        for kind in SCHEMAS:
            base = '/api/' + kind
            for query in ('?paciente_id=mal', '?limit=0', '?limit=101', '?offset=-1', '?limit=1&limit=2', '?role=admin',
                          '?q=x),id.neq.1', '?desde=2026-10-22T00:00:00Z&hasta=2026-10-21T00:00:00Z'):
                self.assertEqual(self.client.get(base + query, headers=self.headers).status_code, 400)
            for path in ('/mal', '/pacientes/mal/historial'):
                self.assertEqual(self.client.get(base + path, headers=self.headers).status_code, 400)
            self.assertEqual(self.client.get(base + '/' + RECORD, headers=self.headers).status_code, 404)
            response = self.client.get(base + '?desde=2026-10-21T10:00:00%2B02:00&hasta=2026-10-22T00:00:00Z', headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(self.store['last_filters']['desde'], '2026-10-21T08:00:00+00:00')

    def test_update_blocked_by_default_and_area_cross_access_denied(self):
        for kind in SCHEMAS:
            for token in ('synthetic-admin', ('psicologo' if kind == 'psicologia' else 'dentista')):
                response = self.client.patch('/api/' + kind + '/' + RECORD,
                    headers={'Authorization': 'Bearer ' + token}, json={'motivo_consulta': 'Seguimiento'})
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response.json['code'], 'UPDATES_BLOCKED')
            other = 'dentista' if kind == 'psicologia' else 'psicologo'
            self.assertEqual(self.client.patch('/api/' + kind + '/' + RECORD, headers={'Authorization': 'Bearer ' + other}, json={}).status_code, 403)

    def test_update_when_enabled_preserves_patient_and_professional(self):
        self.app.config['CLINICAL_ENABLE_UPDATES'] = True
        for kind in SCHEMAS:
            row = self.seed(kind); path = '/api/' + kind + '/' + row['id']
            response = self.client.patch(path, headers={'Authorization': 'Bearer ' + ('psicologo' if kind == 'psicologia' else 'dentista')}, json={'motivo_consulta': 'Seguimiento sintético'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['data']['paciente_id'], PATIENT)
            self.assertEqual(response.json['data']['atendido_por'], ADMIN)
            self.store['deny_update'] = True
            self.assertEqual(self.client.patch(path, headers=self.headers, json={'motivo_consulta': 'x'}).status_code, 409)
            self.store['deny_update'] = False

    def test_update_validates_types_ranges_and_reassignment(self):
        self.app.config['CLINICAL_ENABLE_UPDATES'] = True
        for kind in SCHEMAS:
            row = self.seed(kind); path = '/api/' + kind + '/' + row['id']
            payloads = [[], {}, 'texto', {'paciente_id': ADMIN}, {'atendido_por': ADMIN}, {'id': RECORD}, {'role': 'admin'},
                        {'motivo_consulta': ''}, {'motivo_consulta': 3}, {'motivo_consulta': 'x' * 10001}]
            for date in ('ayer', '2026-02-30T10:00:00Z', '2026-10-21', '2026-10-21T10:00:00', None, '2101-01-01T00:00:00Z'):
                payloads.append({SCHEMAS[kind]['date']: date})
            if kind == 'psicologia':
                for n in (0, -1, 1.5, True, '2', None, 2147483648): payloads.append({'numero_sesion': n})
            else:
                for value in ('-1', '1.001', 'NaN', 'Infinity', True, None, '100000000.00', [], {}): payloads.append({'costo_recuperacion': value})
            for payload in payloads:
                with self.subTest(kind=kind, payload=str(payload)[:90]):
                    self.assertEqual(self.client.patch(path, headers=self.headers, json=payload).status_code, 400)
            self.assertEqual(self.client.patch(path, data='{', headers=self.headers, content_type='application/json').status_code, 400)
            self.assertEqual(self.client.patch(path, data='x', headers=self.headers).status_code, 400)
            self.assertEqual(self.client.patch(path, data='x' * 70000, headers=self.headers, content_type='application/json').status_code, 413)

    def test_error_sanitization(self):
        with patch('tests_clinical.fakes.FakeRepository.list', side_effect=RuntimeError('TOKEN DATOS CLINICOS')):
            response = self.client.get('/api/psicologia', headers=self.headers)
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('TOKEN', response.get_data(as_text=True))


class IntegrationTests(unittest.TestCase):
    def test_main_registration_existing_routes_and_new_roles(self):
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://synthetic.supabase.co', 'SUPABASE_KEY': 'sb_publishable_synthetic'}), \
             patch('requests.sessions.Session.request', side_effect=AssertionError('No network allowed')):
            spec = importlib.util.spec_from_file_location('run_clinical_test', Path(__file__).resolve().parents[1] / 'run.py')
            module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
            self.assertEqual(module.total_registered, 11)
            client = module.app.test_client()
            app, store = synthetic_app()
            module.app.config['CLINICAL_REPOSITORY_FACTORY'] = app.config['CLINICAL_REPOSITORY_FACTORY']
            self.assertEqual(client.get('/health').status_code, 200)
            self.assertEqual(client.get('/api/status').json['blueprints_registered'], 11)
            self.assertEqual(client.get('/api/auth').status_code, 200)
            for name in ('auth', 'admin_usuarios', 'traslados', 'desayunos_frios', 'desayunos_calientes', 'espacios_eaeyd', 'chatbot', 'sms', 'colonias'):
                self.assertIn(name, module.app.blueprints)
            for kind in SCHEMAS:
                self.assertEqual(client.get('/api/' + kind).status_code, 401)
                self.assertEqual(client.get('/api/' + kind, headers={'Authorization': 'Bearer ' + ('psicologo' if kind == 'psicologia' else 'dentista')}).status_code, 200)
                with client.get('/modulos/admin_' + kind + '/vistas/admin_' + kind + '.html') as response:
                    self.assertEqual(response.status_code, 200)
            for path in ('/modulos/login/vistas/login.html', '/dashboard.html'):
                with client.get(path) as response: self.assertEqual(response.status_code, 200)
            for token, status in [(None, 401), ('admin_desayunos', 403), ('admin_traslados', 403), ('psicologo', 403), ('dentista', 403)]:
                headers = {'Authorization': 'Bearer ' + token} if token else {}
                for method in ('get', 'post'):
                    self.assertEqual(getattr(client, method)('/api/admin_usuarios', headers=headers).status_code, status)
            # El mismo login entrega los dos tipos nuevos desde perfiles, sin duplicar pantallas.
            login_globals = module.app.view_functions['auth.login_user'].__globals__
            for role in ('admin', 'admin_desayunos', 'admin_traslados', 'psicologo', 'dentista'):
                fake = Mock()
                fake.auth.sign_in_with_password.return_value = SimpleNamespace(user=SimpleNamespace(id=ADMIN), session=SimpleNamespace(access_token='synthetic'))
                fake.table.return_value.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(data=[{'rol': role, 'nombre_completo': 'Cuenta sintética'}])
                with patch.dict(login_globals, {'supabase': fake}):
                    response = client.post('/api/auth/login', json={'email': 'ficticio@example.test', 'password': 'ficticia'})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json['role'], role)
            user_globals = module.app.view_functions['admin_usuarios.crear_usuario'].__globals__
            for role in ('psicologo', 'dentista'):
                payload = dict(nombre_usuario='prueba', nombre_completo='Cuenta sintética', email='ficticio@example.test',
                               password='contrasena-sintetica', rol=role, telefono='0000000000')
                with patch.dict(user_globals, {'supabase_admin': None}):
                    response = client.post('/api/admin_usuarios', headers={'Authorization': 'Bearer synthetic-admin'}, json=payload)
                    self.assertEqual(response.status_code, 503)
                    self.assertNotIn('errors', response.json)  # Rol admitido; alta real aún sin proveedor configurado.

            # Alta sólo por Auth Admin mockeado; claim no editable consistente con perfil del trigger.
            auth_admin = Mock()
            auth_admin.auth.admin.create_user.return_value = SimpleNamespace(user=SimpleNamespace(id=PATIENT))
            for role in ('psicologo', 'dentista'):
                payload = dict(nombre_usuario='sintetico', nombre_completo='Profesional sintético',
                               email='sintetico@example.invalid', password='sintetica-123', rol=role, telefono='0000000000')
                with patch.dict(user_globals, {'supabase_admin': auth_admin}):
                    response = client.post('/api/admin_usuarios', headers={'Authorization': 'Bearer synthetic-admin'}, json=payload)
                self.assertEqual(response.status_code, 200)
                attributes = auth_admin.auth.admin.create_user.call_args.args[0]
                self.assertEqual(attributes['app_metadata'], {'role': role})
                self.assertEqual(attributes['user_metadata']['rol'], role)

            # Gestión usa JWT por petición, no el cliente público global, sin cambiar roles a medias.
            scoped = Mock()
            scoped.table.return_value.select.return_value.eq.return_value.execute.return_value = SimpleNamespace(data=[{'rol': 'psicologo'}])
            scoped.table.return_value.update.return_value.eq.return_value.execute.return_value = SimpleNamespace(data=[{'rol': 'psicologo', 'nombre_completo': 'Nuevo sintético'}])
            with patch.dict(user_globals, {'create_client': Mock(return_value=scoped)}):
                path = '/api/admin_usuarios/' + PATIENT
                headers = {'Authorization': 'Bearer synthetic-admin'}
                self.assertEqual(client.patch(path, headers=headers, json={'rol': 'dentista'}).status_code, 409)
                scoped.table.return_value.update.assert_not_called()
                self.assertEqual(client.patch(path, headers=headers, json={'rol': 'psicologo', 'nombre_completo': 'Nuevo sintético'}).status_code, 200)
                scoped.postgrest.auth.assert_called_with('synthetic-admin')


if __name__ == '__main__': unittest.main()
