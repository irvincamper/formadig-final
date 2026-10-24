import unittest
from werkzeug.security import generate_password_hash
from tests_clinical.account_demo import build_demo


class DemoAccountTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.accounts=[{'id':f'00000000-0000-0000-0000-{i:012d}','email':role+'@formadig.example.invalid',
                       'role':role,'password_hash':generate_password_hash('synthetic-'+role)}
                      for i,role in enumerate(('admin','psicologo','dentista'),10)]
    def setUp(self): self.client=build_demo(self.accounts).test_client()
    def test_three_accounts_and_operation_matrix(self):
        for role in ('admin','psicologo','dentista'):
            r=self.client.post('/api/auth/login',json={'email':role+'@formadig.example.invalid','password':'synthetic-'+role})
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json['role'],role)
            headers={'Authorization':'Bearer '+r.json['session']['access_token']}
            self.assertEqual(self.client.get('/api/auth/me',headers=headers).json['role'],role)
            for area in ('traslados','desayunos_frios','desayunos_calientes','espacios_eaeyd','admin_usuarios','psicologia','dentista'):
                allowed=role=='admin' or (role=='psicologo' and area=='psicologia') or role==area
                self.assertEqual(self.client.get('/api/'+area,headers=headers).status_code,200 if allowed else 403,(role,area))
            self.assertEqual(self.client.post('/api/auth/logout',headers=headers).status_code,204)
            self.assertEqual(self.client.get('/api/auth/me',headers=headers).status_code,401)
    def test_invalid_credentials_and_forged_role(self):
        self.assertEqual(self.client.post('/api/auth/login',json={'email':self.accounts[0]['email'],'password':'wrong','role':'admin'}).status_code,401)
        self.assertEqual(self.client.get('/api/auth/me',headers={'Authorization':'Bearer synthetic-admin'}).status_code,401)
