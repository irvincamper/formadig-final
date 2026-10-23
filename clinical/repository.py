"""Adaptador Supabase REST: clave pública + JWT del solicitante en cada llamada.

Sin sesión global compartida, service_role, fallback privilegiado ni acceso directo a SQL.
"""
import base64
import json
import os
from urllib.parse import urlparse
import requests
from .validation import ClinicalError, SCHEMAS


def public_key(key):
    if key.startswith('sb_publishable_'):
        return True
    try:
        payload = key.split('.')[1]
        return json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))['role'] == 'anon'
    except (ValueError, KeyError, IndexError, TypeError):
        return False


class SupabaseRepository:
    def __init__(self, token, transport=None):
        self.url = os.getenv('SUPABASE_URL', '').rstrip('/')
        key = os.getenv('SUPABASE_KEY', '')
        parsed = urlparse(self.url)
        local = parsed.hostname in ('localhost', '127.0.0.1', '::1')
        if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path or (parsed.scheme != 'https' and not (local and parsed.scheme == 'http')) or not public_key(key):
            raise ClinicalError('CONFIGURATION_ERROR', 'Configura SUPABASE_URL y una clave pública SUPABASE_KEY.', 503)
        self.headers = {'apikey': key, 'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
        self.transport = transport or requests

    def _call(self, method, path, params=None, payload=None, representation=False, identity=False):
        headers = dict(self.headers)
        if representation:
            headers['Prefer'] = 'return=representation'
        try:
            response = self.transport.request(method, self.url + path, headers=headers,
                                              params=params, json=payload, timeout=(3, 15), allow_redirects=False)
        except requests.Timeout:
            raise ClinicalError('UPSTREAM_TIMEOUT', 'Supabase no respondió a tiempo.', 504)
        except requests.RequestException:
            raise ClinicalError('UPSTREAM_UNAVAILABLE', 'No se pudo contactar con Supabase.', 503)
        if response.status_code in (401, 403):
            if identity or response.status_code == 401:
                raise ClinicalError('UNAUTHENTICATED', 'Sesión inválida o expirada.', 401)
            raise ClinicalError('DATABASE_PERMISSION_DENIED', 'Supabase no autoriza esta operación.', 403)
        if not 200 <= response.status_code < 300:
            try:
                code = response.json().get('code')
            except (ValueError, AttributeError):
                code = None
            if code == '23503':
                raise ClinicalError('INVALID_REFERENCE', 'El perfil indicado no existe o no es accesible.', 422)
            if code in ('23514', '23502', '22P02', '22007', '22008', '22003'):
                raise ClinicalError('DATABASE_VALIDATION_ERROR', 'La base de datos rechazó los campos enviados.', 422)
            if code == '23505':
                raise ClinicalError('CONFLICT', 'El registro entra en conflicto con una restricción.', 409)
            raise ClinicalError('UPSTREAM_ERROR', 'Supabase rechazó la solicitud.', 502)
        try:
            return response.json()
        except ValueError:
            raise ClinicalError('UPSTREAM_ERROR', 'Supabase devolvió una respuesta inválida.', 502)

    def identity(self):
        return self._call('GET', '/auth/v1/user', identity=True)

    def profile(self, user_id):
        rows = self._call('GET', '/rest/v1/perfiles', [('select', 'id,rol,nombre_completo'), ('id', f'eq.{user_id}'), ('limit', '1')])
        if not isinstance(rows, list):
            raise ClinicalError('UPSTREAM_ERROR', 'Respuesta de perfil inválida.', 502)
        return rows[0] if rows else None

    def _columns(self, kind):
        s = SCHEMAS[kind]
        patient = f"paciente:perfiles!{s['table']}_paciente_id_fkey(nombre_completo)"
        return ','.join(['id', 'paciente_id', 'atendido_por', *s['text'], *s['extra'], s['date'], patient])

    def list(self, kind, filters):
        s = SCHEMAS[kind]
        params = [('select', self._columns(kind)), ('order', f"{s['date']}.desc.nullslast,id.desc"),
                  ('limit', str(filters['limit'] + 1)), ('offset', str(filters['offset']))]
        for key in ('paciente_id', 'tipo_atencion', 'estatus_caso'):
            if key in filters:
                params.append((key, 'eq.' + filters[key]))
        for key, op in (('desde', 'gte'), ('hasta', 'lte')):
            if key in filters:
                params.append((s['date'], op + '.' + filters[key]))
        if filters.get('q'):
            terms = ','.join(f'{column}.ilike.*{filters["q"]}*' for column in s['text'])
            params.append(('or', '(' + terms + ')'))
        rows = self._call('GET', '/rest/v1/' + s['table'], params)
        return self._rows(rows)

    @staticmethod
    def _rows(value):
        if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
            raise ClinicalError('UPSTREAM_ERROR', 'Respuesta de registros inválida.', 502)
        return value

    def get(self, kind, record_id):
        rows = self._rows(self._call('GET', '/rest/v1/' + SCHEMAS[kind]['table'],
                                     [('select', self._columns(kind)), ('id', 'eq.' + record_id), ('limit', '1')]))
        return rows[0] if rows else None

    def create(self, kind, payload):
        rows = self._rows(self._call('POST', '/rest/v1/' + SCHEMAS[kind]['table'], payload=payload, representation=True))
        if len(rows) != 1:
            raise ClinicalError('WRITE_NOT_CONFIRMED', 'No se confirmó la creación. Consulta antes de reintentar.', 409)
        return rows[0]

    def update(self, kind, record_id, payload):
        rows = self._rows(self._call('PATCH', '/rest/v1/' + SCHEMAS[kind]['table'],
                                     [('id', 'eq.' + record_id)], payload, representation=True))
        if len(rows) != 1:
            raise ClinicalError('UPDATE_NOT_APPLIED', 'No se aplicó la edición. Revisa permisos RLS o si el registro sigue existiendo.', 409)
        return rows[0]
