import os
import unittest
from unittest.mock import Mock, patch
import requests
from clinical.repository import SupabaseRepository
from clinical.validation import ClinicalError
from tests_clinical.fakes import ADMIN, RECORD


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'SUPABASE_URL': 'https://synthetic.supabase.co', 'SUPABASE_KEY': 'sb_publishable_synthetic'})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.transport = Mock()
        self.response = Mock(status_code=200)
        self.response.json.return_value = []
        self.transport.request.return_value = self.response
        self.repo = SupabaseRepository('verified-user-token', self.transport)

    def test_identity_uses_auth_server_and_each_request_has_user_jwt(self):
        self.response.json.return_value = {'id': ADMIN}
        self.repo.identity()
        args, kwargs = self.transport.request.call_args
        self.assertEqual(args, ('GET', 'https://synthetic.supabase.co/auth/v1/user'))
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer verified-user-token')
        self.assertEqual(kwargs['timeout'], (3, 15))
        self.assertFalse(kwargs['allow_redirects'])

    def test_profile_filtered_by_verified_id_and_no_privileged_fallback(self):
        self.repo.profile(ADMIN)
        self.assertIn(('id', 'eq.' + ADMIN), self.transport.request.call_args.kwargs['params'])
        other = SupabaseRepository('different-user', self.transport)
        self.assertEqual(other.headers['Authorization'], 'Bearer different-user')
        self.assertEqual(self.repo.headers['Authorization'], 'Bearer verified-user-token')

    def test_query_filters_are_sent_to_supabase_not_filtered_after_download(self):
        self.repo.list('psicologia', {'limit': 25, 'offset': 50, 'paciente_id': ADMIN, 'q': 'sintético',
                                      'desde': '2026-10-21T00:00:00+00:00', 'hasta': '2026-10-22T00:00:00+00:00'})
        params = self.transport.request.call_args.kwargs['params']
        self.assertIn(('paciente_id', 'eq.' + ADMIN), params)
        self.assertIn(('limit', '26'), params)
        self.assertIn(('offset', '50'), params)
        self.assertEqual(sum(k == 'fecha_sesion' for k, v in params), 2)
        self.assertTrue(any(k == 'or' for k, v in params))

    def test_errors_are_sanitized_and_mapped(self):
        for http, code, status in [(401, None, 401), (403, '42501', 403), (400, '23503', 422),
                                   (400, '23505', 409), (400, '23514', 422), (500, None, 502), (302, None, 502)]:
            with self.subTest(http=http, code=code):
                self.response.status_code = http
                self.response.json.return_value = {'code': code, 'message': 'SECRET PATIENT VALUE'}
                with self.assertRaises(ClinicalError) as context:
                    self.repo.list('dentista', {'limit': 25, 'offset': 0})
                self.assertEqual(context.exception.status, status)
                self.assertNotIn('SECRET', str(context.exception))
        for error, status in [(requests.Timeout(), 504), (requests.ConnectionError(), 503)]:
            self.transport.request.side_effect = error
            with self.assertRaises(ClinicalError) as context:
                self.repo.identity()
            self.assertEqual(context.exception.status, status)

    def test_empty_update_is_not_success_and_writes_request_representation(self):
        with self.assertRaises(ClinicalError) as context:
            self.repo.update('dentista', RECORD, {'diagnostico': 'Sintético'})
        self.assertEqual(context.exception.code, 'UPDATE_NOT_APPLIED')
        args, kwargs = self.transport.request.call_args
        self.assertEqual(args[0], 'PATCH')
        self.assertEqual(kwargs['headers']['Prefer'], 'return=representation')
        self.assertIn(('id', 'eq.' + RECORD), kwargs['params'])
        with self.assertRaises(ClinicalError):
            self.repo.create('dentista', {'paciente_id': ADMIN})

    def test_malformed_upstream_response(self):
        self.response.json.side_effect = ValueError('bad json')
        with self.assertRaises(ClinicalError):
            self.repo.identity()
        self.response.json.side_effect = None
        self.response.json.return_value = {'error': 'not a list'}
        with self.assertRaises(ClinicalError):
            self.repo.list('dentista', {'limit': 25, 'offset': 0})

    def test_reject_privileged_keys_and_invalid_urls(self):
        for key in ('sb_secret_no', 'invalid', '', 'eyJhbGciOiJub25lIn0.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.x'):
            with self.subTest(key=key), patch.dict(os.environ, {'SUPABASE_KEY': key}):
                with self.assertRaises(ClinicalError):
                    SupabaseRepository('token', self.transport)
        for url in ('http://remote.test', 'https://user:pass@test.co', 'https://test.co/path', 'https://test.co?secret=1'):
            with patch.dict(os.environ, {'SUPABASE_URL': url}):
                with self.assertRaises(ClinicalError):
                    SupabaseRepository('token', self.transport)


if __name__ == '__main__':
    unittest.main()
