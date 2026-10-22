"""Validación estricta de los contratos clínicos; nunca construye SQL."""
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import UUID


class ClinicalError(Exception):
    def __init__(self, code, message, status=400, fields=None):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status
        self.fields = fields or {}


SCHEMAS = {
    'psicologia': {
        'table': 'modulo_psicologia', 'date': 'fecha_sesion',
        'required': ('paciente_id', 'tipo_atencion', 'motivo_consulta'),
        'text': ('tipo_atencion', 'motivo_consulta', 'diagnostico_inicial', 'estatus_caso'),
        'extra': ('numero_sesion',),
        'defaults': {'numero_sesion': 1, 'estatus_caso': 'En proceso'},
    },
    'dentista': {
        'table': 'modulo_dental', 'date': 'fecha_atencion',
        'required': ('paciente_id', 'motivo_consulta'),
        'text': ('motivo_consulta', 'diagnostico', 'tratamiento_realizado'),
        'extra': ('costo_recuperacion',), 'defaults': {'costo_recuperacion': '0.00'},
    },
}


def uuid_value(value, field):
    try:
        if not isinstance(value, str):
            raise ValueError()
        return str(UUID(value))
    except (ValueError, AttributeError):
        raise ClinicalError('VALIDATION_ERROR', 'Identificador UUID inválido.', fields={field: 'UUID requerido.'})


def timestamp(value, field):
    try:
        if not isinstance(value, str) or not re.match(r'^\d{4}-\d{2}-\d{2}T', value):
            raise ValueError()
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if dt.tzinfo is None or dt.utcoffset() is None or not 1900 <= dt.year <= 2100:
            raise ValueError()
        return dt.astimezone(timezone.utc).isoformat()
    except (ValueError, OverflowError):
        raise ClinicalError('VALIDATION_ERROR', 'Fecha inválida.', fields={field: 'ISO 8601 con zona horaria; años 1900–2100.'})


def validate_payload(kind, data, partial=False):
    schema = SCHEMAS[kind]
    if not isinstance(data, dict) or not data:
        raise ClinicalError('VALIDATION_ERROR', 'Se requiere un objeto JSON no vacío.')
    allowed = {'paciente_id', schema['date'], *schema['text'], *schema['extra']}
    unknown = set(data) - allowed
    if unknown:
        raise ClinicalError('VALIDATION_ERROR', 'Campos desconocidos o no editables.',
                            fields={str(k): 'No permitido.' for k in sorted(unknown)})
    result = {}
    if not partial:
        missing = [k for k in schema['required'] if k not in data]
        if missing:
            raise ClinicalError('VALIDATION_ERROR', 'Faltan campos obligatorios.', fields={k: 'Obligatorio.' for k in missing})
        result.update(schema['defaults'])
    for key, value in data.items():
        if key == 'paciente_id':
            result[key] = uuid_value(value, key)
        elif key == schema['date']:
            result[key] = timestamp(value, key)
        elif key in schema['text']:
            required = key in schema['required'] or key == 'estatus_caso'
            if value is None and not required:
                result[key] = None
                continue
            maximum = 120 if key in ('tipo_atencion', 'estatus_caso') else 10000
            if not isinstance(value, str) or len(value) > maximum or (required and not value.strip()):
                raise ClinicalError('VALIDATION_ERROR', 'Texto inválido.', fields={key: f'Texto de hasta {maximum} caracteres; obligatorio si corresponde.'})
            result[key] = value.strip() or None
        elif key == 'numero_sesion':
            if type(value) is not int or not 1 <= value <= 2147483647:
                raise ClinicalError('VALIDATION_ERROR', 'Número de sesión inválido.', fields={key: 'Entero entre 1 y 2147483647.'})
            result[key] = value
        elif key == 'costo_recuperacion':
            try:
                if isinstance(value, bool) or not isinstance(value, (str, int, float)):
                    raise InvalidOperation()
                amount = Decimal(str(value))
                if not amount.is_finite() or amount < 0 or amount > Decimal('99999999.99') or amount != amount.quantize(Decimal('0.01')):
                    raise InvalidOperation()
                result[key] = format(amount, '.2f')
            except (InvalidOperation, ValueError):
                raise ClinicalError('VALIDATION_ERROR', 'Costo inválido.', fields={key: 'Entre 0 y 99999999.99, máximo dos decimales.'})
    if not partial and schema['date'] not in result:
        result[schema['date']] = datetime.now(timezone.utc).isoformat()
    return result


def validate_filters(kind, args):
    schema = SCHEMAS[kind]
    allowed = {'q', 'paciente_id', 'desde', 'hasta', 'limit', 'offset'}
    if kind == 'psicologia':
        allowed |= {'tipo_atencion', 'estatus_caso'}
    if set(args) - allowed or any(len(args.getlist(k)) != 1 for k in args):
        raise ClinicalError('VALIDATION_ERROR', 'Parámetros desconocidos o repetidos.')
    result = {}
    for key in ('limit', 'offset'):
        raw = args.get(key, '25' if key == 'limit' else '0')
        if not re.fullmatch(r'\d{1,7}', raw):
            raise ClinicalError('VALIDATION_ERROR', 'Paginación inválida.')
        value = int(raw)
        if (key == 'limit' and not 1 <= value <= 100) or (key == 'offset' and value > 1000000):
            raise ClinicalError('VALIDATION_ERROR', 'Paginación fuera de rango.')
        result[key] = value
    for key in ('q', 'tipo_atencion', 'estatus_caso'):
        if key not in args:
            continue
        value = args[key].strip()
        # Evitar operadores/grupos PostgREST inyectados en filtros OR/ILIKE.
        if len(value) > 120 or (key == 'q' and not re.fullmatch(r'[\w\sáéíóúüñÁÉÍÓÚÜÑ-]*', value)):
            raise ClinicalError('VALIDATION_ERROR', 'Filtro inválido.', fields={key: 'Hasta 120 caracteres; búsqueda sólo con letras, números, espacios y guiones.'})
        if value:
            result[key] = value
    if 'paciente_id' in args:
        result['paciente_id'] = uuid_value(args['paciente_id'], 'paciente_id')
    for key in ('desde', 'hasta'):
        if key in args:
            result[key] = timestamp(args[key], key)
    if 'desde' in result and 'hasta' in result and datetime.fromisoformat(result['desde']) > datetime.fromisoformat(result['hasta']):
        raise ClinicalError('VALIDATION_ERROR', 'El inicio no puede ser posterior al fin.')
    return result
