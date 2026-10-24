import unittest
from types import SimpleNamespace
from unittest.mock import Mock
from clinical.provisioning import create_web_user
from clinical.validation import ClinicalError
from tests_clinical.fakes import ADMIN, PATIENT


class ProvisioningTests(unittest.TestCase):
    def setUp(self):
        self.api,self.db=Mock(),Mock()
        self.actor={'id':ADMIN,'app_metadata':{'role':'admin'}}
        self.profile={'id':ADMIN,'rol':'admin'}
        self.api.create_user.return_value=SimpleNamespace(user=SimpleNamespace(id=PATIENT))
    def attributes(self,role):
        return {'email':'fixture@example.invalid','password':'synthetic-only',
                'app_metadata':{'role':role},'user_metadata':{'rol':'admin','role':'admin','nombre_completo':'Ficticio'}}
    def test_professionals_are_created_through_auth_and_verified(self):
        for role in ('psicologo','dentista'):
            self.api.get_user_by_id.return_value=SimpleNamespace(user=SimpleNamespace(id=PATIENT,app_metadata={'role':role}))
            self.db.table.return_value.select.return_value.eq.return_value.execute.return_value.data=[{'id':PATIENT,'rol':role}]
            result,status=create_web_user(self.api,self.db,self.actor,self.profile,self.attributes(role))
            self.assertEqual(status,201)
            self.assertTrue(result['access_validation_pending'])
            attrs=self.api.create_user.call_args.args[0]
            self.assertEqual(attrs['app_metadata'],{'role':role})
            self.assertNotIn('rol',attrs['user_metadata'])
            self.assertNotIn('role',attrs['user_metadata'])
            self.db.table.return_value.insert.assert_not_called()
    def test_a_profile_role_alone_cannot_authorize_creation(self):
        with self.assertRaises(ClinicalError):
            create_web_user(self.api,self.db,{'id':ADMIN,'app_metadata':{},'user_metadata':{'role':'admin'}},self.profile,self.attributes('dentista'))
        self.api.create_user.assert_not_called()
    def test_partial_creation_requires_reconciliation_without_deleting(self):
        self.api.get_user_by_id.return_value=SimpleNamespace(user=SimpleNamespace(id=PATIENT,app_metadata={'role':'dentista'}))
        self.db.table.return_value.select.return_value.eq.return_value.execute.return_value.data=[]
        result,status=create_web_user(self.api,self.db,self.actor,self.profile,self.attributes('dentista'))
        self.assertEqual(status,409)
        self.assertTrue(result['account_created'])
        self.api.delete_user.assert_not_called()
        self.db.table.return_value.upsert.assert_not_called()
    def test_auth_mismatch_does_not_grant_access_from_profile(self):
        self.api.get_user_by_id.return_value=SimpleNamespace(user=SimpleNamespace(id=PATIENT,app_metadata={}))
        self.db.table.return_value.select.return_value.eq.return_value.execute.return_value.data=[{'id':PATIENT,'rol':'dentista'}]
        result,status=create_web_user(self.api,self.db,self.actor,self.profile,self.attributes('dentista'))
        self.assertEqual(status,409)
