# test/test_autorizar.py
# Pruebas unitarias para el módulo autorizar/autorizar.py


# ══════════════════════════════════════════════════
# PRUEBAS PARA autorizarRegistro()
# ══════════════════════════════════════════════════

def test_autorizar_registro_renderiza(cliente_flask, mock_mysql, mocker):
    """GET /autorizar/ debe renderizar la plantilla con contadores y solicitudes."""
    mysql_mock, cursor = mock_mysql

    # Primera llamada: contadores. Segunda: solicitudes.
    cursor.fetchone.return_value = {'pendientes': 3, 'hoy': 1, 'rechazadas': 0}
    cursor.fetchall.return_value = [
        {'id_autorizacion': 1, 'tipo_solicitud': 'jugador', 'nombre_persona': 'Juan Pérez'}
    ]

    mocker.patch('autorizar.autorizar.render_template', return_value='OK')

    respuesta = cliente_flask.get('/autorizar/')

    assert respuesta.status_code == 200


# ══════════════════════════════════════════════════
# PRUEBAS PARA contadores()
# ══════════════════════════════════════════════════

def test_contadores_devuelve_json(cliente_flask, mock_mysql):
    """GET /autorizar/contadores debe devolver los contadores en JSON."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'pendientes': 5, 'hoy': 2, 'rechazadas': 1}

    respuesta = cliente_flask.get('/autorizar/contadores')

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['pendientes'] == 5
    assert data['hoy'] == 2
    assert data['rechazadas'] == 1


# ══════════════════════════════════════════════════
# PRUEBAS PARA aprobar()
# ══════════════════════════════════════════════════

def test_aprobar_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """Aprobar una solicitud existente debe devolver ok=True."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {
        'tipo_solicitud': 'jugador',
        'id_referencia': 10,
        'estatus': 'Pendiente',
        'nombre_solicitante': 'Juan Pérez',
        'email_solicitante': 'juan@test.com'
    }

    respuesta = cliente_flask.post('/autorizar/aprobar/1')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True
    mock_notificar.assert_called_once()


def test_aprobar_solicitud_no_existe(cliente_flask, mock_mysql):
    """Aprobar una solicitud inexistente debe devolver 404."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = None

    respuesta = cliente_flask.post('/autorizar/aprobar/999')

    assert respuesta.status_code == 404
    assert respuesta.get_json()['ok'] is False


# ══════════════════════════════════════════════════
# PRUEBAS PARA rechazar()
# ══════════════════════════════════════════════════


def test_rechazar_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """Rechazar con comentario válido debe devolver ok=True."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {
        'tipo_solicitud': 'entrenador',
        'id_referencia': 5,
        'estatus': 'Pendiente',
        'nombre_solicitante': 'Ana López',
        'email_solicitante': 'ana@test.com'
    }

    respuesta = cliente_flask.post(
        '/autorizar/rechazar/1',
        data={'comentario': 'Documentación incompleta'}
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True
    mock_notificar.assert_called_once()
    assert any(
        'DELETE FROM entrenador' in llamada.args[0]
        for llamada in cursor.execute.call_args_list
    )


def test_rechazar_jugador_elimina_dependencias_y_conserva_solicitud(
        cliente_flask, mock_mysql, mock_notificar):
    """Rechazar a un jugador elimina sus datos relacionados dentro de la transacción."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.side_effect = [
        {
            'tipo_solicitud': 'jugador',
            'id_referencia': 10,
            'estatus': 'Pendiente',
            'nombre_solicitante': 'Juan Pérez',
            'email_solicitante': 'juan@test.com'
        },
        {'total': 0}
    ]

    respuesta = cliente_flask.post(
        '/autorizar/rechazar/1',
        data={'comentario': 'Documentación incompleta'}
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True
    comandos = [llamada.args[0] for llamada in cursor.execute.call_args_list]
    assert any('DELETE FROM expediente' in sql for sql in comandos)
    assert any('DELETE FROM tutor_padre' in sql for sql in comandos)
    assert any('DELETE FROM jugador' in sql for sql in comandos)
    assert any('nombre_solicitante = %s' in sql for sql in comandos)
    mysql_mock.connection.commit.assert_called_once()


def test_rechazar_jugador_con_pagos_bloquea_eliminacion(
        cliente_flask, mock_mysql, mock_notificar):
    """No se eliminan registros financieros ni se rechaza mientras haya pagos."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.side_effect = [
        {
            'tipo_solicitud': 'jugador',
            'id_referencia': 10,
            'estatus': 'Pendiente',
            'nombre_solicitante': 'Juan Pérez',
            'email_solicitante': 'juan@test.com'
        },
        {'total': 1}
    ]

    respuesta = cliente_flask.post(
        '/autorizar/rechazar/1',
        data={'comentario': 'Documentación incompleta'}
    )

    assert respuesta.status_code == 409
    assert respuesta.get_json()['ok'] is False
    assert not any(
        'DELETE FROM' in llamada.args[0]
        for llamada in cursor.execute.call_args_list
    )
    assert not any(
        'SET estatus     = ' in llamada.args[0]
        for llamada in cursor.execute.call_args_list
    )
    mysql_mock.connection.commit.assert_not_called()
    mock_notificar.assert_not_called()


def test_rechazar_solicitud_ya_resuelta_no_elimina_registro(
        cliente_flask, mock_mysql):
    """Una solicitud aprobada no se puede rechazar ni borrar después."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {
        'tipo_solicitud': 'jugador',
        'id_referencia': 10,
        'estatus': 'Autorizado',
        'nombre_solicitante': 'Juan Pérez',
        'email_solicitante': 'juan@test.com'
    }

    respuesta = cliente_flask.post(
        '/autorizar/rechazar/1',
        data={'comentario': 'Documentación incompleta'}
    )

    assert respuesta.status_code == 409
    assert not any(
        'DELETE FROM' in llamada.args[0]
        for llamada in cursor.execute.call_args_list
    )
    mysql_mock.connection.commit.assert_not_called()
