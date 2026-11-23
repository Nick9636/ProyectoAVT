
import os
import requests

TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
API_VERSION = os.getenv("WHATSAPP_API_VERSION")

URL = (
    f"https://graph.facebook.com/"
    f"{API_VERSION}/{PHONE_NUMBER_ID}/messages"
)


def enviar_plantilla(numero, plantilla, idioma="es_MX",
                     parametros=None):

    if not TOKEN or not PHONE_NUMBER_ID or not API_VERSION:
        raise ValueError("Faltan credenciales de WhatsApp")

    # Número internacional sin espacios ni símbolos.
    numero = "".join(
        caracter for caracter in numero if caracter.isdigit()
    )
    if len(numero) == 10:
        numero = f"52{numero}"

    componentes = []

    if parametros:
        componentes.append({
            "type": "body",
            "parameters": [
                {
                    "type": "text",
                    "text": str(valor)
                }
                for valor in parametros
            ]
        })

    payload = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "template",
        "template": {
            "name": plantilla,
            "language": {
                "code": idioma
            }
        }
    }

    if componentes:
        payload["template"]["components"] = componentes

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        respuesta = requests.post(
            URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        respuesta.raise_for_status()

        return {
            "exito": True,
            "respuesta": respuesta.json()
        }

    except requests.RequestException as error:
        return {
            "exito": False,
            "error": str(error)
        }


def notificar_estado_registro(numero, estado, nombre, comentario=None):
    """Envía una plantilla aprobada para informar el resultado del registro."""
    plantillas = {
        "aprobado": os.getenv("WHATSAPP_TEMPLATE_REGISTRO_APROBADO"),
        "rechazado": os.getenv("WHATSAPP_TEMPLATE_REGISTRO_RECHAZADO"),
    }
    plantilla = plantillas.get(estado)
    if not plantilla:
        raise ValueError(
            f"Falta configurar la plantilla de WhatsApp para el estado: {estado}"
        )

    parametros = [nombre]
    if estado == "rechazado":
        parametros.append(comentario or "")

    return enviar_plantilla(numero, plantilla, parametros=parametros)
