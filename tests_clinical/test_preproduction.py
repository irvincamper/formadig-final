"""Pruebas de soporte web aislado; aplicación móvil fuera del alcance."""
import unittest
from unittest.mock import MagicMock
from flask import Flask
from twilio.request_validator import RequestValidator
from clinical.sms_security import receive_webhook, automatic_sms

class WebhookTests(unittest.TestCase):
    def setUp(self):
        self.app=Flask(__name__)
        self.app.add_url_rule('/callback',view_func=receive_webhook,methods=['POST'])
        self.url='https://fixture.invalid/callback'
        self.token='synthetic-twilio-token'
        self.account='AC'+'0'*32
        self.events={}
        class Queue:
            def enqueue_once(_,key,event):
                if event['sender']!='+520000000000': raise PermissionError()
                self.events.setdefault(key,event)
        self.app.config.update(SMS_WEBHOOK_ENABLED=True,SMS_WEBHOOK_PUBLIC_URL=self.url,
            SMS_WEBHOOK_AUTH_TOKEN=self.token,SMS_WEBHOOK_ACCOUNT_SID=self.account,SMS_WEBHOOK_QUEUE=Queue())
        self.form={'AccountSid':self.account,'MessageSid':'SM'+'1'*32,'From':'+520000000000','Body':'SI'}
        self.client=self.app.test_client()
    def send(self,form=None,signature=None,**headers):
        form=form or self.form
        sig=signature if signature is not None else RequestValidator(self.token).compute_signature(self.url,form)
        return self.client.post('/callback',data=form,headers={'X-Twilio-Signature':sig,**headers})
    def test_disabled_by_default(self):
        self.app.config.pop('SMS_WEBHOOK_ENABLED')
        self.assertEqual(self.send().status_code,503)
    def test_signature_replay_and_sender_binding(self):
        self.assertEqual(self.send(signature='invalid').status_code,403)
        self.assertEqual(self.send().status_code,200)
        self.assertEqual(self.send().status_code,200)
        self.assertEqual(len(self.events),1)
        self.assertEqual(self.send(dict(self.form,From='+520000000001')).status_code,403)
    def test_account_and_configuration_fail_closed(self):
        self.assertEqual(self.send(dict(self.form,AccountSid='AC'+'2'*32)).status_code,403)
        self.app.config.pop('SMS_WEBHOOK_QUEUE')
        self.assertEqual(self.send().status_code,503)
    def test_forwarded_headers_do_not_change_signed_url(self):
        self.assertEqual(self.send(**{'X-Forwarded-Host':'attacker.invalid','X-Forwarded-Proto':'http'}).status_code,200)
    def test_automatic_sms_uses_internal_api_and_ordinary_token(self):
        app=MagicMock();app.config={'SMS_AUTOMATIC_ENABLED':True}
        client=app.test_client.return_value.__enter__.return_value
        client.post.return_value.status_code=200
        self.assertEqual(automatic_sms(app,'ordinary-fixture-token',{'telefono_principal':'+520000000000'}),'accepted')
        self.assertEqual(client.post.call_args.kwargs['headers']['Authorization'],'Bearer ordinary-fixture-token')


if __name__=='__main__': unittest.main()
