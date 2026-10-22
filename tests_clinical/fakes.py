from copy import deepcopy
from datetime import datetime
from uuid import uuid4
from flask import Flask
from clinical.api import make_blueprint
from clinical.validation import ClinicalError, SCHEMAS

ADMIN = '00000000-0000-0000-0000-000000000001'
PATIENT = '00000000-0000-0000-0000-000000000002'
RECORD = '00000000-0000-0000-0000-000000000003'


class FakeRepository:
    def __init__(self, token, store):
        self.token, self.store = token, store

    def identity(self):
        if self.token in ('invalid', 'expired'):
            raise ClinicalError('UNAUTHENTICATED', 'Sesión inválida.', 401)
        role = 'admin' if self.token == 'synthetic-admin' else self.token
        return {'id': ADMIN, 'is_anonymous': self.token == 'anonymous',
                'app_metadata': {'role': role}, 'user_metadata': {'role': 'admin'}}

    def profile(self, user_id):
        if user_id not in (ADMIN, PATIENT):
            return None
        if user_id == PATIENT:
            return {'id': PATIENT, 'rol': 'usuario'}
        if self.token == 'missing':
            return None
        return {'id': ADMIN, 'rol': 'admin' if self.token == 'synthetic-admin' else self.token}

    def list(self, kind, filters):
        self.store['last_filters'] = filters
        rows = list(self.store[kind].values())
        for field in ('paciente_id', 'tipo_atencion', 'estatus_caso'):
            if field in filters:
                rows = [r for r in rows if r.get(field) == filters[field]]
        date = SCHEMAS[kind]['date']
        for key, op in (('desde', lambda a, b: a >= b), ('hasta', lambda a, b: a <= b)):
            if key in filters:
                rows = [r for r in rows if op(datetime.fromisoformat(r[date]), datetime.fromisoformat(filters[key]))]
        if filters.get('q'):
            rows = [r for r in rows if any(filters['q'].casefold() in str(r.get(k, '')).casefold() for k in SCHEMAS[kind]['text'])]
        rows.sort(key=lambda r: (r.get(date) or '', r['id']), reverse=True)
        return deepcopy(rows[filters['offset']:filters['offset'] + filters['limit'] + 1])

    def get(self, kind, record_id):
        return deepcopy(self.store[kind].get(record_id))

    def create(self, kind, payload):
        row = dict(payload, id=str(uuid4()), paciente={'nombre_completo': 'Paciente sintético'})
        self.store[kind][row['id']] = row
        return deepcopy(row)

    def update(self, kind, record_id, payload):
        if self.store.get('deny_update'):
            raise ClinicalError('UPDATE_NOT_APPLIED', 'RLS bloqueó la edición.', 409)
        self.store[kind][record_id].update(payload)
        return self.get(kind, record_id)


def synthetic_app(static_folder=None):
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    store = {'psicologia': {}, 'dentista': {}}
    app.config.update(TESTING=True, CLINICAL_REPOSITORY_FACTORY=lambda token: FakeRepository(token, store))
    for kind in ('psicologia', 'dentista'):
        app.register_blueprint(make_blueprint(kind))
    return app, store


def sample(kind):
    value = {'paciente_id': PATIENT, 'motivo_consulta': 'Atención sintética de prueba'}
    if kind == 'psicologia':
        value.update(tipo_atencion='Individual', numero_sesion=1, estatus_caso='En proceso')
    else:
        value.update(costo_recuperacion='25.50')
    return value
