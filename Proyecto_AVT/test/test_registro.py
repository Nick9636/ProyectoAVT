# test/test_registro.py
import re
import pytest
from datetime import date
from pathlib import Path


# ══════════════════════════════════════════════════
# LIGA
# ══════════════════════════════════════════════════

def test_guardar_liga_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """POST /registro/liga/guardar con datos válidos debe registrar la liga."""
    mysql_mock, cursor = mock_mysql

    # No existe liga con ese nombre
    cursor.fetchone.return_value = None
    cursor.lastrowid = 42

    respuesta = cliente_flask.post(
        '/registro/liga/guardar',
        data={'nombre_liga': 'liga premier', 'categoria': 'varonil'}
    )

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['ok'] is True
    assert data['nombre'] == 'LIGA PREMIER'
    assert data['categoria'] == 'VARONIL'
    assert data['id'] == 42


def test_guardar_liga_duplicada(cliente_flask, mock_mysql):
    """POST con liga ya existente debe devolver 400."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'id_liga': 1}  # ya existe

    respuesta = cliente_flask.post(
        '/registro/liga/guardar',
        data={'nombre_liga': 'LIGA PREMIER', 'categoria': 'VARONIL'}
    )

    assert respuesta.status_code == 400
    assert 'ya existe' in respuesta.get_json()['mensaje'].lower()


def test_eliminar_liga_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """POST /registro/liga/eliminar/<id> debe devolver ok=True."""
    mysql_mock, cursor = mock_mysql

    respuesta = cliente_flask.post('/registro/liga/eliminar/1')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# EQUIPO
# ══════════════════════════════════════════════════

def test_guardar_equipo_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """POST /registro/equipo/guardar con datos válidos debe registrar el equipo."""
    mysql_mock, cursor = mock_mysql

    # Primera llamada: verificar duplicado (None)
    # Segunda llamada: obtener nombre de liga
    cursor.fetchone.side_effect = [
        None,
        {'nombre_liga': 'LIGA PREMIER'}
    ]
    cursor.lastrowid = 7

    respuesta = cliente_flask.post(
        '/registro/equipo/guardar',
        data={'nombre_equipo': 'aguilas', 'id_liga': '1', 'categoria': 'JUVENIL'}
    )

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['ok'] is True
    assert data['nombre'] == 'AGUILAS'
    assert data['nombre_liga'] == 'LIGA PREMIER'


def test_eliminar_equipo_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """POST /registro/equipo/eliminar/<id> debe devolver ok=True."""
    mysql_mock, cursor = mock_mysql

    respuesta = cliente_flask.post('/registro/equipo/eliminar/5')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# PAGO
# ══════════════════════════════════════════════════

def test_guardar_pago_datos_incompletos(cliente_flask, mock_mysql):
    """POST sin jugador o sin fecha debe devolver 400."""
    respuesta = cliente_flask.post(
        '/registro/pago/guardar',
        data={'id_persona': '', 'fecha_pago': ''}
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()['ok'] is False


def test_guardar_pago_nuevo(cliente_flask, mock_mysql, mock_notificar):
    """POST con datos válidos y sin pago previo debe insertar uno nuevo."""
    mysql_mock, cursor = mock_mysql

    # 1ª: afiliación existente. 2ª: no hay pago previo.
    cursor.fetchone.side_effect = [
        {'id_afiliacion': 10},
        None
    ]
    cursor.lastrowid = 99

    respuesta = cliente_flask.post(
        '/registro/pago/guardar',
        data={
            'id_persona': '1',
            'fecha_pago': '2026-04-01',
            'estatus': 'Pendiente',
            'metodo_pago': 'EFECTIVO',
            'referencia': 'REF-001'
        }
    )

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['ok'] is True
    assert data['id'] == 99
    assert data['folio'] == 'PAG-000099'
    assert 'registrado' in data['mensaje'].lower()
    assert any(
        'UPDATE pago SET folio_pago' in llamada.args[0]
        for llamada in cursor.execute.call_args_list
    )


def test_actualizar_pago_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """POST con estatus válido debe actualizar el pago."""
    mysql_mock, cursor = mock_mysql

    respuesta = cliente_flask.post(
        '/registro/pago/actualizar/1',
        data={'estatus': 'Completado'}
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# SIGUIENTE REGISTRO
# ══════════════════════════════════════════════════


def test_siguiente_registro_jugador(cliente_flask, mock_mysql):
    """GET con tipo=jugador debe devolver el siguiente número JUG-XXX."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'ultimo': 5}

    respuesta = cliente_flask.get('/registro/persona/siguiente_registro?tipo=jugador')

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['ok'] is True
    assert data['numero'] == 'JUG-006'
    assert 'MAX(CAST(SUBSTRING(numero_registro, 5)' in \
        cursor.execute.call_args.args[0]


# ══════════════════════════════════════════════════
# PRUEBAS: años de vigencia dinámicos
# ══════════════════════════════════════════════════


def test_registro_persona_envia_anios_vigencia(cliente_flask, mock_mysql, mocker):
    """GET /registro/persona debe pasar los años a la plantilla."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = {'ultimo': 0}
    render = mocker.patch('registro.registro.render_template', return_value='OK')

    respuesta = cliente_flask.get('/registro/persona')

    assert respuesta.status_code == 200
    assert render.call_args.kwargs['anios_vigencia'][0] == date.today().year
    assert 'ligas' in render.call_args.kwargs
    assert render.call_args.kwargs['sig_jugador'] == 'JUG-001'
    assert render.call_args.kwargs['sig_entrenador'] == 'ENT-001'
    assert render.call_args.kwargs['sig_arbitro'] == 'ARB-001'
    assert cursor.execute.call_count == 6


def test_registro_persona_muestra_carga_obligatoria_ine_tutor(cliente_flask, mock_mysql):
    """El formulario presenta el campo de archivo para la INE del tutor."""
    _, cursor = mock_mysql
    cursor.fetchall.side_effect = [
        [],
        [],
        [{'id_liga': 7, 'nombre_liga': 'LIGA DE PRUEBA'}],
    ]
    cursor.fetchone.return_value = {'ultimo': 0}

    respuesta = cliente_flask.get('/registro/persona')
    contenido = respuesta.get_data(as_text=True)

    assert respuesta.status_code == 200
    assert 'id="ineTutor"' in contenido
    assert 'accept=".png,.jpg,.jpeg,.pdf"' in contenido
    assert 'ineTutor.required = true' in contenido
    assert 'id="ligasParticipa" multiple required' in contenido
    assert '<option value="7">LIGA DE PRUEBA</option>' in contenido


# ══════════════════════════════════════════════════
# PRUEBAS: firma obligatoria en guardarPersona()
# ══════════════════════════════════════════════════

FIRMA_VALIDA = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=='


@pytest.mark.parametrize('tipo', ['jugador'])
@pytest.mark.parametrize('datos_firma', [
    {},                                                  # no se envía la firma
    {'firma_base64': 'texto-que-no-es-imagen'},          # formato inválido
])
def test_guardar_persona_sin_firma_valida(cliente_flask, mock_mysql, tipo, datos_firma):
    """Sin una firma PNG válida no se debe guardar ningún tipo de persona."""
    mysql_mock, cursor = mock_mysql
    datos = {'tipo_persona': tipo}
    datos.update(datos_firma)

    respuesta = cliente_flask.post('/registro/persona/guardar', data=datos)

    assert respuesta.status_code == 400
    assert respuesta.get_json()['ok'] is False
    assert 'firma' in respuesta.get_json()['mensaje'].lower()
    mysql_mock.connection.cursor.assert_not_called()


def test_guardar_persona_con_firma_valida_continua(cliente_flask, mock_mysql, mock_notificar):
    """Con firma válida ya no se rechaza por la firma y se guarda en la base de datos."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'ultimo': 0, 'id_municipio': 1}
    cursor.fetchall.return_value = [
        {'id_liga': 1, 'nombre_liga': 'LIGA DE PRUEBA'},
        {'id_liga': 2, 'nombre_liga': 'LIGA SECUNDARIA'},
    ]

    respuesta = cliente_flask.post('/registro/persona/guardar', data={
        'tipo_persona': 'jugador',
        'fecha_nacimiento': '2000-01-01',
        'firma_base64': FIRMA_VALIDA,
        'ligas_participa': ['1', '2'],
    })

    mensaje = (respuesta.get_json() or {}).get('mensaje', '')
    assert 'firma' not in mensaje.lower()
    mysql_mock.connection.cursor.assert_called()
    insert_jugador = next(
        llamada for llamada in cursor.execute.call_args_list
        if 'INSERT INTO jugador' in llamada.args[0]
    )
    assert insert_jugador.args[1][23] == 'LIGA DE PRUEBA, LIGA SECUNDARIA'


def test_guardar_persona_rechaza_liga_no_registrada(cliente_flask, mock_mysql):
    """No se acepta una liga que no exista en la tabla liga."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchall.return_value = []

    respuesta = cliente_flask.post('/registro/persona/guardar', data={
        'tipo_persona': 'jugador',
        'fecha_nacimiento': '2000-01-01',
        'firma_base64': FIRMA_VALIDA,
        'ligas_participa': ['999'],
    })

    assert respuesta.status_code == 400
    assert 'no están registradas' in respuesta.get_json()['mensaje']
    assert not any('INSERT INTO jugador' in sql for sql in _sqls(cursor))


def test_guardar_menor_sin_ine_tutor_no_continua(cliente_flask, mock_mysql):
    """Un jugador menor de edad sin INE del tutor debe rechazarse antes del SQL."""
    mysql_mock, _ = mock_mysql

    respuesta = cliente_flask.post('/registro/persona/guardar', data={
        'tipo_persona': 'jugador',
        'fecha_nacimiento': f'{date.today().year - 10}-01-01',
        'nombre_padre': 'TUTORA DE PRUEBA',
        'firma_base64': FIRMA_VALIDA,
        'ligas_participa': ['1'],
    })

    assert respuesta.status_code == 400
    assert 'INE' in respuesta.get_json()['mensaje']
    mysql_mock.connection.cursor.assert_not_called()


def test_guardar_menor_persiste_ruta_ine_tutor(
        cliente_flask, mock_mysql, mock_notificar, mocker):
    """La ruta del archivo INE se guarda en la fila del tutor."""
    from io import BytesIO

    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'ultimo': 0}
    cursor.fetchall.return_value = [
        {'id_liga': 1, 'nombre_liga': 'LIGA DE PRUEBA'}
    ]
    cursor.lastrowid = 44
    mocker.patch('registro.registro.os.makedirs')
    guardar_archivo = mocker.patch('werkzeug.datastructures.FileStorage.save')

    respuesta = cliente_flask.post('/registro/persona/guardar', data={
        'tipo_persona': 'jugador',
        'fecha_nacimiento': f'{date.today().year - 10}-01-01',
        'nombre_padre': 'TUTORA DE PRUEBA',
        'firma_base64': FIRMA_VALIDA,
        'ligas_participa': ['1'],
        'ineTutor': (BytesIO(b'archivo de prueba'), 'identificacion.jpg'),
    })

    assert respuesta.status_code == 200
    insert_tutor = next(
        llamada for llamada in cursor.execute.call_args_list
        if 'INSERT INTO tutor_padre' in llamada.args[0]
    )
    assert 'fotografia_ine' in insert_tutor.args[0]
    assert insert_tutor.args[1][-1].startswith('static/uploads/ine_tutor/ine_tutor_')
    assert insert_tutor.args[1][-1].endswith('.jpg')
    guardar_archivo.assert_called_once()


# ══════════════════════════════════════════════════
# PRUEBAS: método de pago obligatorio y predeterminado
# ══════════════════════════════════════════════════

def _datos_pago(**cambios):
    datos = {
        'id_persona': '1',
        'tipo_persona': 'jugador',
        'fecha_pago': '2026-04-01',
        'estatus': 'Completado',
        'metodo_pago': 'Efectivo',
    }
    datos.update(cambios)
    return datos


# ══════════════════════════════════════════════════
# PRUEBAS: asignar jugador a equipo
# ══════════════════════════════════════════════════

def _sqls(cursor):
    """Devuelve los textos SQL ejecutados con el cursor simulado."""
    return [llamada.args[0] for llamada in cursor.execute.call_args_list]


def test_asignar_get_renderiza_con_datos(cliente_flask, mock_mysql, mocker):
    """GET /registro/asignar debe cargar jugadores, equipos y asignados."""
    mysql_mock, cursor = mock_mysql
    jugadores = [{'id_jugador': 1, 'nombre': 'PEREZ JUAN', 'curp': 'AAAA'}]
    equipos = [{'id_equipo': 7, 'nombre_equipo': 'AGUILAS', 'categoria': 'JUVENIL',
                'nombre_liga': 'LIGA PREMIER'}]
    asignados = []
    cursor.fetchall.side_effect = [jugadores, equipos, asignados]
    render = mocker.patch('registro.registro.render_template', return_value='OK')

    respuesta = cliente_flask.get('/registro/asignar')

    assert respuesta.status_code == 200
    assert render.call_args.args[0] == 'registro/asignarJugador.html'
    assert render.call_args.kwargs['jugadores'] == jugadores
    assert render.call_args.kwargs['equipos'] == equipos
    assert render.call_args.kwargs['asignados'] == asignados


def test_menu_registro_tiene_enlace_a_asignar(cliente_flask):
    """El menú de registro debe tener la tarjeta para asignar jugadores."""
    respuesta = cliente_flask.get('/registro/')

    assert respuesta.status_code == 200
    assert b'/registro/asignar' in respuesta.data


def test_guardar_asignacion_exitosa(cliente_flask, mock_mysql, mock_notificar):
    """POST con jugador y equipo existentes debe actualizar jugador.id_equipo."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.side_effect = [{'nombre': 'PEREZ LOPEZ JUAN'}, {'nombre_equipo': 'AGUILAS'}]

    respuesta = cliente_flask.post('/registro/asignar/guardar',
                                   data={'id_jugador': '3', 'id_equipo': '7'})

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['ok'] is True
    assert 'AGUILAS' in data['mensaje']

    update = [c for c in cursor.execute.call_args_list
              if 'UPDATE jugador SET id_equipo' in c.args[0]]
    assert len(update) == 1
    assert update[0].args[1] == ('7', '3')      # (id_equipo, id_jugador)
    mysql_mock.connection.commit.assert_called()
    mock_notificar.assert_called_once()


def test_quitar_asignacion_exitoso(cliente_flask, mock_mysql, mock_notificar):
    """POST /registro/asignar/quitar/<id> debe dejar id_equipo en NULL."""
    mysql_mock, cursor = mock_mysql

    respuesta = cliente_flask.post('/registro/asignar/quitar/3')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True
    update = [c for c in cursor.execute.call_args_list
              if 'SET id_equipo = NULL' in c.args[0]]
    assert len(update) == 1
    assert update[0].args[1] == (3,)
    mock_notificar.assert_called_once()
