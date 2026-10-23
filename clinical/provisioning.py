"""Altas web por Auth Admin; nunca insertar identidades ni roles por SQL/REST público."""
from .security import trusted_role, WEB_ROLES
from .validation import ClinicalError, uuid_value


def create_web_user(admin_api, profile_client, actor, actor_profile, attributes):
    if trusted_role(actor, actor_profile) != 'admin':
        raise ClinicalError('FORBIDDEN', 'Sólo administración general puede crear cuentas.', 403)
    role = attributes.get('app_metadata', {}).get('role')
    if role not in WEB_ROLES:
        raise ClinicalError('INVALID_ROLE', 'Rol web no permitido.', 400)
    attributes = dict(attributes)
    attributes['app_metadata'] = {'role': role}
    attributes['user_metadata'] = {k:v for k,v in attributes.get('user_metadata', {}).items()
                                   if k not in ('role','rol')}
    try:
        created = admin_api.create_user(attributes).user
        user_id = uuid_value(created.id, 'usuario')
    except Exception:
        raise ClinicalError('AUTH_ADMIN_FAILURE',
                            'Auth no confirmó el alta. Revisa el resultado antes de reintentar.', 502)
    try:
        verified = admin_api.get_user_by_id(user_id).user
        rows = profile_client.table('perfiles').select('id,rol').eq('id',user_id).execute().data
        if (verified.id != user_id or (verified.app_metadata or {}).get('role') != role
                or not isinstance(rows,list) or len(rows)!=1 or rows[0].get('id')!=user_id
                or rows[0].get('rol')!=role):
            raise ValueError('El vínculo Auth/perfil no coincide')
    except Exception:
        # No borrar Auth ni crear un perfil alternativo para ocultar un alta parcial.
        return {'status':'pending','user_id':user_id,'account_created':True,
                'code':'PROVISIONING_RECONCILIATION_REQUIRED',
                'message':'Cuenta creada en Auth; falta verificar el perfil y rol administrado. No reintentar el alta.'},409
    return {'status':'success','user_id':user_id,'account_created':True,
            'access_validation_pending':True,
            'message':'Cuenta Auth y perfil vinculados. Falta validar acceso real y RLS antes de activarla operativamente.'},201
