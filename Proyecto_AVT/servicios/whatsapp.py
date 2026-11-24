
import os
import logging

from flask import Blueprint, request, jsonify

whatsapp_bp = Blueprint(
    'whatsapp',
    __name__,
    url_prefix='/webhook'
)

logger = logging.getLogger(__name__)


@whatsapp_bp.route('/whatsapp', methods=['GET', 'POST'])
def webhook_whatsapp():

    # VERIFICACIÓN DE META
    if request.method == 'GET':

        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')

        logger.info("Verificación de webhook recibida")

        if not verify_token:
            logger.error("No está configurado WHATSAPP_VERIFY_TOKEN")
            return "Configuración incompleta", 500

        if mode == 'subscribe' and token == verify_token:
            logger.info("Webhook verificado correctamente")
            return challenge or '', 200

        logger.warning("Verificación de webhook rechazada")
        return "Token no válido", 403

    # RECEPCIÓN DE NOTIFICACIONES
    elif request.method == 'POST':

        data = request.get_json(silent=True)

        if data is None:
            return jsonify({
                'status': 'invalid_json'
            }), 400

        logger.info("Notificación recibida de WhatsApp")
        logger.info("Datos recibidos: %s", data)

        return jsonify({
            'status': 'EVENT_RECEIVED'
        }), 200

    return "Método no permitido", 405
