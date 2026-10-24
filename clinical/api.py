"""Fábrica de blueprints con autorización y contratos compartidos."""
import os
from flask import Blueprint, current_app, g, jsonify, request
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge, UnsupportedMediaType
from .repository import SupabaseRepository
from .security import trusted_role
from .validation import ClinicalError, uuid_value, validate_filters, validate_payload


def authorize(identity, profile, kind):
    """Punto de extensión: pacientes/profesionales requieren diseño y RLS aprobados.

    Administrador general o responsable del área, según el alcance web autorizado.
    Nunca usar user_metadata, X-User-Role ni datos del cuerpo para autorizar.
    """
    try:
        role = trusted_role(identity, profile)
        return role in ('admin', 'psicologo' if kind == 'psicologia' else 'dentista')
    except ClinicalError:
        return False



def make_blueprint(kind):
    bp = Blueprint('admin_' + kind, __name__, url_prefix='/api/' + kind)

    @bp.before_request
    def authenticate():
        # Evitar preflight con datos; no ejecutar repositorio para OPTIONS.
        if request.method == 'OPTIONS':
            return '', 204
        parts = request.headers.get('Authorization', '').split()
        if len(parts) != 2 or parts[0].lower() != 'bearer' or len(parts[1]) > 8192:
            raise ClinicalError('UNAUTHENTICATED', 'Se requiere una sesión Bearer válida.', 401)
        factory = current_app.config.get('CLINICAL_REPOSITORY_FACTORY', SupabaseRepository)
        g.clinical_repo = factory(parts[1])
        identity = g.clinical_repo.identity()
        if not isinstance(identity, dict) or not identity.get('id') or identity.get('is_anonymous') is True:
            raise ClinicalError('UNAUTHENTICATED', 'Sesión inválida o anónima.', 401)
        user_id = uuid_value(identity['id'], 'usuario')
        identity = dict(identity, id=user_id)
        profile = g.clinical_repo.profile(user_id)
        if not authorize(identity, profile, kind):
            raise ClinicalError('FORBIDDEN', 'No tienes autorización para este módulo clínico.', 403)
        g.clinical_user_id = user_id
        g.clinical_role = profile['rol']

    @bp.after_request
    def private_response(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @bp.errorhandler(ClinicalError)
    def controlled(error):
        return jsonify(error=error.message, code=error.code, fields=error.fields), error.status

    @bp.errorhandler(BadRequest)
    @bp.errorhandler(UnsupportedMediaType)
    def malformed(error):
        return jsonify(error='Se requiere JSON válido.', code='INVALID_JSON', fields={}), 400

    @bp.errorhandler(RequestEntityTooLarge)
    def too_large(error):
        return jsonify(error='Solicitud demasiado grande.', code='PAYLOAD_TOO_LARGE', fields={}), 413

    @bp.errorhandler(Exception)
    def unexpected(error):
        # No registrar cuerpos clínicos, tokens, URLs ni mensajes de proveedores.
        current_app.logger.error('Clinical %s failed (%s)', kind, type(error).__name__)
        return jsonify(error='No se pudo completar la operación.', code='INTERNAL_ERROR', fields={}), 500

    def listing(filters):
        rows = g.clinical_repo.list(kind, filters)
        limit = filters['limit']
        return jsonify(data=rows[:limit], pagination={'limit': limit, 'offset': filters['offset'], 'has_more': len(rows) > limit})

    def updates_enabled():
        return current_app.config.get('CLINICAL_ENABLE_UPDATES', os.getenv('CLINICAL_ENABLE_UPDATES', '').lower() == 'true') is True

    @bp.get('/capacidades')
    def capabilities():
        return jsonify(data={'read': True, 'create': creation_enabled(), 'update': updates_enabled(), 'delete': False,
                             'role': g.clinical_role, 'module': kind})

    @bp.route('/', methods=['POST'], strict_slashes=False)
    def create_record():
        if not creation_enabled():
            return jsonify(error='Registro bloqueado: disponible sólo en el ensayo sintético local.', code='WEB_CREATION_DISABLED', fields={}), 405
        request.max_content_length = 65536
        payload = validate_payload(kind, request.get_json())
        payload['atendido_por'] = g.clinical_user_id
        return jsonify(data=g.clinical_repo.create(kind, payload), message='Registro sintético creado.'), 201

    def creation_enabled():
        # No se activa mediante entorno ni por las políticas INSERT públicas existentes.
        return (current_app.config.get('CLINICAL_SYNTHETIC_MODE') is True
                and current_app.config.get('CLINICAL_ENABLE_CREATION') is True
                and current_app.config.get('CLINICAL_REPOSITORY_FACTORY') is not None)

    @bp.route('/', methods=['GET'], strict_slashes=False)
    def list_records():
        return listing(validate_filters(kind, request.args))

    @bp.get('/pacientes/<patient_id>/historial')
    def history(patient_id):
        patient_id = uuid_value(patient_id, 'paciente_id')
        filters = validate_filters(kind, request.args)
        if 'paciente_id' in filters and filters['paciente_id'] != patient_id:
            raise ClinicalError('VALIDATION_ERROR', 'El filtro de paciente no coincide con la ruta.')
        filters['paciente_id'] = patient_id
        return listing(filters)

    @bp.get('/<record_id>')
    def detail(record_id):
        record_id = uuid_value(record_id, 'id')
        row = g.clinical_repo.get(kind, record_id)
        if row is None:
            raise ClinicalError('NOT_FOUND', 'Atención no encontrada o no accesible.', 404)
        return jsonify(data=row)

    @bp.patch('/<record_id>')
    def update(record_id):
        record_id = uuid_value(record_id, 'id')
        if not updates_enabled():
            raise ClinicalError('UPDATES_BLOCKED', 'Seguimiento pendiente de aprobación y validación de permisos RLS.', 409)
        request.max_content_length = 65536
        payload = validate_payload(kind, request.get_json(), partial=True)
        if 'paciente_id' in payload:
            raise ClinicalError('VALIDATION_ERROR', 'No se permite reasignar el paciente de una atención.')
        if g.clinical_repo.get(kind, record_id) is None:
            raise ClinicalError('NOT_FOUND', 'Atención no encontrada o no accesible.', 404)
        row = g.clinical_repo.update(kind, record_id, payload)
        return jsonify(data=row, message='Seguimiento actualizado.')

    return bp
