from Proyecto_AVT.servicios import whatsapp_servicio
from Proyecto_AVT.blueprints.autorizar.autorizar import _enviar_aviso_whatsapp


def test_notifica_aprobacion_a_numero_mexicano(monkeypatch, mocker):
    monkeypatch.setenv(
        'WHATSAPP_TEMPLATE_REGISTRO_APROBADO',
        'registro_aprobado'
    )
    monkeypatch.setattr(whatsapp_servicio, 'TOKEN', 'token-de-prueba')
    monkeypatch.setattr(whatsapp_servicio, 'PHONE_NUMBER_ID', '123')
    monkeypatch.setattr(whatsapp_servicio, 'API_VERSION', 'v23.0')
    monkeypatch.setattr(
        whatsapp_servicio,
        'URL',
        'https://graph.facebook.com/v23.0/123/messages'
    )
    respuesta = mocker.Mock()
    respuesta.json.return_value = {'messages': [{'id': 'wamid.test'}]}
    post = mocker.patch.object(
        whatsapp_servicio.requests,
        'post',
        return_value=respuesta
    )

    resultado = whatsapp_servicio.notificar_estado_registro(
        '246 123 4567',
        'aprobado',
        'Juan Pérez'
    )

    assert resultado['exito'] is True
    payload = post.call_args.kwargs['json']
    assert payload['to'] == '522461234567'
    assert payload['template']['name'] == 'registro_aprobado'
    assert payload['template']['components'][0]['parameters'][0]['text'] == 'Juan Pérez'


def test_notifica_rechazo_con_motivo(monkeypatch, mocker):
    monkeypatch.setenv(
        'WHATSAPP_TEMPLATE_REGISTRO_RECHAZADO',
        'registro_rechazado'
    )
    monkeypatch.setattr(whatsapp_servicio, 'TOKEN', 'token-de-prueba')
    monkeypatch.setattr(whatsapp_servicio, 'PHONE_NUMBER_ID', '123')
    monkeypatch.setattr(whatsapp_servicio, 'API_VERSION', 'v23.0')
    monkeypatch.setattr(
        whatsapp_servicio,
        'URL',
        'https://graph.facebook.com/v23.0/123/messages'
    )
    respuesta = mocker.Mock()
    respuesta.json.return_value = {'messages': [{'id': 'wamid.test'}]}
    post = mocker.patch.object(
        whatsapp_servicio.requests,
        'post',
        return_value=respuesta
    )

    whatsapp_servicio.notificar_estado_registro(
        '522461234567',
        'rechazado',
        'Ana López',
        'Falta la identificación'
    )

    parametros = post.call_args.kwargs['json']['template']['components'][0]['parameters']
    assert [parametro['text'] for parametro in parametros] == [
        'Ana López',
        'Falta la identificación'
    ]


def test_aviso_de_decision_usa_telefono_de_solicitud(mocker):
    enviar = mocker.patch(
        'Proyecto_AVT.blueprints.autorizar.autorizar.notificar_estado_registro',
        return_value={'exito': True}
    )

    detalle = _enviar_aviso_whatsapp({
        'id_referencia': 7,
        'telefono_solicitante': '2461234567',
        'nombre_solicitante': 'Juan Pérez'
    }, 'aprobado')

    assert detalle == ''
    enviar.assert_called_once_with('2461234567', 'aprobado', 'Juan Pérez', None)
