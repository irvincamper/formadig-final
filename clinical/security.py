"""Autorización web común. Los datos del navegador nunca conceden permisos."""
from flask import current_app, g, jsonify, request
from werkzeug.local import LocalProxy
from .repository import SupabaseRepository
from .validation import ClinicalError, uuid_value

WEB_ROLES = frozenset(('admin', 'admin_traslados', 'admin_desayunos', 'psicologo', 'dentista'))

SUPPORT_TABLE_ROLES = {
    'traslados': frozenset(('admin', 'admin_traslados')),
    'desayunos_frios': frozenset(('admin', 'admin_desayunos')),
    'desayunos_calientes': frozenset(('admin', 'admin_desayunos')),
    'desayunos_eaeyd': frozenset(('admin', 'admin_desayunos')),
    'hospitales': WEB_ROLES,
    'chatbot_conocimiento': WEB_ROLES,
    'perfiles': WEB_ROLES,
    'sms_logs': frozenset(('admin', 'admin_traslados', 'psicologo', 'dentista')),
}


class AreaClient:
    """Lista cerrada para soporte; ni un nombre de tabla recibido concede acceso."""
    def __init__(self, client, role):
        self.client, self.role = client, role

    def table(self, name):
        if self.role not in SUPPORT_TABLE_ROLES.get(name, ()):
            raise ClinicalError('FORBIDDEN', 'Tabla no autorizada para esta función.', 403)
        return self.client.table(name)


def trusted_role(identity, profile):
    if not isinstance(identity, dict) or identity.get('is_anonymous') is True:
        raise ClinicalError('UNAUTHENTICATED', 'Sesión inválida o anónima.', 401)
    user_id = uuid_value(identity.get('id'), 'usuario')
    metadata = identity.get('app_metadata')
    role = metadata.get('role') if isinstance(metadata, dict) else None
    if (not isinstance(role, str) or role not in WEB_ROLES or not isinstance(profile, dict)
            or profile.get('id') != user_id or profile.get('rol') != role):
        raise ClinicalError('ROLE_PROVISIONING_REQUIRED',
                            'El rol requiere aprovisionamiento administrativo confiable.', 403)
    return role


def request_identity():
    parts = request.headers.get('Authorization', '').split()
    if len(parts) != 2 or parts[0].lower() != 'bearer' or len(parts[1]) > 8192:
        raise ClinicalError('UNAUTHENTICATED', 'Se requiere una sesión Bearer válida.', 401)
    factory = current_app.config.get('CLINICAL_REPOSITORY_FACTORY', SupabaseRepository)
    repository = factory(parts[1])
    identity = repository.identity()  # Auth valida el JWT; nunca se decodifica sin verificar.
    if not isinstance(identity, dict) or not identity.get('id'):
        raise ClinicalError('UNAUTHENTICATED', 'Sesión inválida.', 401)
    profile = repository.profile(uuid_value(identity['id'], 'usuario'))
    return parts[1], identity, profile, trusted_role(identity, profile)


def protect_module(blueprint, roles, restrict_tables=False):
    """Cliente público con JWT aislado para los módulos anteriores."""
    @blueprint.after_request
    def private_response(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @blueprint.before_request
    def verify_module():
        if request.method == 'OPTIONS':
            return '', 204
        try:
            token, identity, profile, role = request_identity()
            if role not in roles:
                raise ClinicalError('FORBIDDEN', 'No tienes autorización para este módulo.', 403)
            from supabase import create_client
            import os
            client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
            client.postgrest.auth(token)
            g.module_client = AreaClient(client, role) if restrict_tables else client
            g.web_identity, g.web_role = identity, role
        except ClinicalError as error:
            return jsonify(error=error.message, code=error.code), error.status
        except Exception:
            return jsonify(error='No se pudieron verificar los permisos.'), 503

    return LocalProxy(lambda: g.module_client)
