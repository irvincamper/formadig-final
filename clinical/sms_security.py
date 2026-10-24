"""Webhook preparado, deshabilitado por defecto; sin clientes privilegiados."""
from flask import current_app, jsonify, request
from twilio.request_validator import RequestValidator


def receive_webhook():
    config = current_app.config
    if config.get('SMS_WEBHOOK_ENABLED') is not True:
        return jsonify(error='Webhook bloqueado hasta validar firma y autorización restringida.'), 503
    url = config.get('SMS_WEBHOOK_PUBLIC_URL', '')
    token = config.get('SMS_WEBHOOK_AUTH_TOKEN')
    account = config.get('SMS_WEBHOOK_ACCOUNT_SID')
    queue = config.get('SMS_WEBHOOK_QUEUE')
    if not url.startswith('https://') or not token or not account or queue is None:
        return jsonify(error='Falta configurar el receptor seguro del webhook.'), 503
    # URL externa exacta configurada; no confiar en Host/X-Forwarded-* del solicitante.
    if request.query_string or request.mimetype != 'application/x-www-form-urlencoded':
        return jsonify(error='Formato de callback no autorizado.'), 400
    if not RequestValidator(token).validate(url, request.form, request.headers.get('X-Twilio-Signature', '')):
        return jsonify(error='Firma del proveedor inválida.'), 403
    if request.form.get('AccountSid') != account:
        return jsonify(error='Cuenta del proveedor no autorizada.'), 403
    event_id, sender = request.form.get('MessageSid', ''), request.form.get('From', '')
    answer = request.form.get('Body', '').strip().upper()
    if not event_id.startswith('SM') or len(event_id) != 34 or not sender.startswith('+'):
        return jsonify(error='Identidad del evento inválida.'), 400
    if answer not in ('SI', 'SÍ', 'S', 'YES', 'CONFIRMO', 'NO', 'N', 'CANCELAR', 'RECHAZO'):
        return '', 204
    try:
        # El adaptador debe deduplicar persistentemente y vincular un único traslado
        # pendiente al remitente/outbound registrado. Nunca buscar globalmente por teléfono.
        queue.enqueue_once(event_id, {'sender': sender, 'answer': answer, 'account': account})
    except PermissionError:
        return jsonify(error='No existe una solicitud pendiente autorizada para este evento.'), 403
    except Exception:
        return jsonify(error='No se pudo aceptar el evento de forma segura.'), 503
    return '<Response></Response>', 200, {'Content-Type': 'application/xml', 'Cache-Control': 'no-store'}


def automatic_sms(app, token, record):
    if app.config.get('SMS_AUTOMATIC_ENABLED') is not True:
        return 'disabled'
    phone = record.get('telefono_principal') or record.get('telefono_secundario')
    if not phone:
        return 'missing_phone'
    # API interna unificada, JWT ordinario; nunca localhost:5009 ni clave de servicio.
    try:
        with app.test_client() as client:
            response = client.post('/api/sms/send', headers={'Authorization': 'Bearer ' + token}, json={
                'phone': phone, 'message': 'DIF Acatlan: confirma tu traslado programado respondiendo SI o NO.'})
        return 'accepted' if response.status_code == 200 else 'failed'
    except Exception:
        return 'failed'
