
import os
from flask import Blueprint, request, jsonify

whatsapp_bp = Blueprint(
    'whatsapp',
    __name__,
    url_prefix='/webhook'
)


@whatsapp_bp.route('/whatsapp', methods=['GET', 'POST'])
def webhook_whatsapp():

    if request.method == 'GET':

        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')

        if mode == 'subscribe' and token == verify_token:
            return challenge, 200

        return 'Token no válido', 403

    if request.method == 'POST':

        data = request.get_json(silent=True)

        print("Notificación recibida de WhatsApp:")
        print(data)

        return jsonify({
            'status': 'EVENT_RECEIVED'
        }), 200
