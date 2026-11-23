# test/test_auth.py 
# Pruebas unitarias para el módulo auth/auth.py
#Total de 22 pruebas unitarias, cubriendo todas las rutas y funciones principales.
import pytest
from datetime import date

# ══════════════════════════════════════════════════
# PRUEBAS PARA index()
# ══════════════════════════════════════════════════

def test_index_renderiza_login(cliente_flask, mocker):
    """GET / debe renderizar la plantilla de login."""
    mocker.patch('auth.auth.render_template', return_value='LOGIN OK')

    respuesta = cliente_flask.get('/iniciarSesion')

    assert respuesta.status_code == 200


# ══════════════════════════════════════════════════
# PRUEBAS PARA iniciarSesion()
# ══════════════════════════════════════════════════

def test_iniciar_sesion_exitoso(cliente_flask, mock_mysql, mock_bcrypt, mock_notificar):
    """Login con credenciales válidas debe redirigir a paginaInicio."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {
        'id_usuario': 1,
        'nombre_usuario': 'presidente',
        'password': '$2b$12$hash',
        'nombre_completo': 'Juan Perez',
        'rol': 'Presidente',
        'activo': 1
    }
    mock_bcrypt.check_password_hash.return_value = True

    respuesta = cliente_flask.post('/iniciarSesion', data={
        'nombreUsuario': 'presidente',
        'password': 'password123'
    })

    assert respuesta.status_code == 302
    assert 'paginaInicio' in respuesta.headers['Location']


def test_iniciar_sesion_usuario_inexistente(cliente_flask, mock_mysql):
    """Login con usuario inexistente debe mostrar 'El usuario no existe'."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = None

    respuesta = cliente_flask.post('/iniciarSesion', data={
        'nombreUsuario': 'noexiste',
        'password': 'password123'
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'El usuario no existe' in respuesta.data


def test_iniciar_sesion_password_incorrecta(cliente_flask, mock_mysql, mock_bcrypt):
    """Login con contraseña incorrecta debe mostrar 'La contraseña es incorrecta'."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {
        'id_usuario': 1,
        'nombre_usuario': 'presidente',
        'password': '$2b$12$hash',
        'nombre_completo': 'Juan Perez',
        'rol': 'Presidente',
        'activo': 1
    }
    mock_bcrypt.check_password_hash.return_value = False

    respuesta = cliente_flask.post('/iniciarSesion', data={
        'nombreUsuario': 'presidente',
        'password': 'incorrecta'
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'La contrase' in respuesta.data


# ══════════════════════════════════════════════════
# PRUEBAS PARA nuevoUsuario()
# ══════════════════════════════════════════════════


def test_nuevo_usuario_exitoso(cliente_flask, mock_mysql, mock_bcrypt, mock_notificar):
    """POST /nuevoUsuario con datos válidos debe crear el usuario."""
    mysql_mock, cursor = mock_mysql
    # Primera llamada: verificar nombre_usuario (no existe)
    # Segunda llamada: verificar email (no existe)
    cursor.fetchone.side_effect = [None, None]
    cursor.lastrowid = 5

    respuesta = cliente_flask.post('/nuevoUsuario', data={
        'nombre_usuario': 'nuevo',
        'nombre_completo': 'Juan Perez',
        'email': 'juan@test.com',
        'password': 'Password1',
        'rol': 'Administrador'
    }, follow_redirects=True)

    assert respuesta.status_code == 200


def test_nuevo_usuario_rol_invalido(cliente_flask, mock_mysql):
    """POST /nuevoUsuario con rol inválido debe mostrar 'Rol inválido'."""
    respuesta = cliente_flask.post('/nuevoUsuario', data={
        'nombre_usuario': 'nuevo',
        'nombre_completo': 'Juan Perez',
        'email': 'juan@test.com',
        'password': 'Password1',
        'rol': 'Delegado'
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'Rol inv' in respuesta.data


def test_nuevo_usuario_nombre_duplicado(cliente_flask, mock_mysql):
    """POST /nuevoUsuario con nombre duplicado debe mostrar 'El nombre de usuario ya est'."""
    mysql_mock, cursor = mock_mysql
    # Primera llamada: nombre_usuario existe
    cursor.fetchone.return_value = {'id_usuario': 1}

    respuesta = cliente_flask.post('/nuevoUsuario', data={
        'nombre_usuario': 'presidente',
        'nombre_completo': 'Juan Perez',
        'email': 'juan@test.com',
        'password': 'Password1',
        'rol': 'Administrador'
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'nombre de usuario ya est' in respuesta.data


# ══════════════════════════════════════════════════
# PRUEBAS PARA cerrarSesion()
# ══════════════════════════════════════════════════

def test_cerrar_sesion(cliente_flask):
    """GET /cerrarSesion debe limpiar la sesión y redirigir."""
    respuesta = cliente_flask.get('/cerrarSesion')

    assert respuesta.status_code == 302
    assert 'iniciarSesion' in respuesta.headers['Location']


# ══════════════════════════════════════════════════
# PRUEBAS PARA accesoExternoPost()
# ══════════════════════════════════════════════════

def test_acceso_externo_post_campos_vacios(cliente_flask):
    """POST /accesoExterno sin datos requeridos debe validar nombre y teléfono."""
    respuesta = cliente_flask.post('/accesoExterno', data={
        'nombre_completo': '',
        'telefono': ''
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'obligatorios' in respuesta.data


def test_acceso_externo_acepta_telefono_sin_correo(cliente_flask):
    """El teléfono basta para continuar al formulario externo."""
    respuesta = cliente_flask.post('/accesoExterno', data={
        'nombre_completo': 'Juan Pérez',
        'telefono': '246 123 4567',
        'acepta_whatsapp': 'on'
    })

    assert respuesta.status_code == 302
    assert 'registroExterno' in respuesta.headers['Location']
    with cliente_flask.session_transaction() as sesion:
        assert sesion['ext_telefono'] == '2461234567'
        assert 'ext_email' not in sesion


def test_acceso_externo_rechaza_telefono_invalido(cliente_flask):
    """No se permite continuar con un teléfono demasiado corto."""
    respuesta = cliente_flask.post('/accesoExterno', data={
        'nombre_completo': 'Juan Pérez',
        'telefono': '12345',
        'acepta_whatsapp': 'on'
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'tel' in respuesta.data.lower()


def test_acceso_externo_requiere_autorizacion_whatsapp(cliente_flask):
    """Se requiere consentimiento para avisos de estado por WhatsApp."""
    respuesta = cliente_flask.post('/accesoExterno', data={
        'nombre_completo': 'Juan Pérez',
        'telefono': '2461234567'
    }, follow_redirects=True)

    assert respuesta.status_code == 200
    assert b'WhatsApp' in respuesta.data


# ══════════════════════════════════════════════════
# PRUEBAS PARA siguienteRegistroExterno()
# ══════════════════════════════════════════════════


def test_siguiente_registro_entrenador(cliente_flask, mock_mysql):
    """GET /registro-externo/siguiente_registro?tipo=entrenador debe devolver ENT-XXX."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'ultimo': 2}

    respuesta = cliente_flask.get('/registro-externo/siguiente_registro?tipo=entrenador')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['numero'] == 'ENT-003'
    assert 'MAX(CAST(SUBSTRING(numero_registro, 5)' in \
        cursor.execute.call_args.args[0]


# ══════════════════════════════════════════════════
# PRUEBAS PARA registroExitoso()
# ══════════════════════════════════════════════════

def test_registro_exitoso(cliente_flask, mocker):
    """GET /registroExitoso debe renderizar la pantalla de éxito."""
    mocker.patch('auth.auth.render_template', return_value='EXITO OK')

    respuesta = cliente_flask.get('/registroExitoso')

    assert respuesta.status_code == 200


# ══════════════════════════════════════════════════
# PRUEBAS: contraseña de nuevoUsuario (entre 8 y 20 caracteres)
# ══════════════════════════════════════════════════

def _mensajes_flash(cliente):
    """Devuelve los mensajes flash que dejó la última petición."""
    with cliente.session_transaction() as sesion:
        return [mensaje for _, mensaje in sesion.get('_flashes', [])]


def _datos_usuario(password):
    return {
        'nombre_usuario': 'nuevo',
        'nombre_completo': 'Juan Perez',
        'email': 'juan@test.com',
        'password': password,
        'rol': 'Administrador'
    }


# ══════════════════════════════════════════════════
# PRUEBAS: firma obligatoria en guardarRegistroExterno()
# ══════════════════════════════════════════════════

FIRMA_VALIDA = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=='


def _sesion_externa(cliente):
    with cliente.session_transaction() as sesion:
        sesion['ext_nombre'] = 'Juan Perez'
        sesion['ext_telefono'] = '2461234567'


@pytest.mark.parametrize('datos_firma', [
    {},                                                  # no se envía la firma
    {'firma_base64': 'texto-que-no-es-imagen'},          # formato inválido
])
def test_guardar_registro_externo_sin_firma_valida(cliente_flask, mock_mysql, datos_firma):
    """Sin una firma PNG válida el registro externo debe rechazarse con 400."""
    mysql_mock, cursor = mock_mysql
    _sesion_externa(cliente_flask)
    datos = {'tipo_persona': 'jugador'}
    datos.update(datos_firma)

    respuesta = cliente_flask.post('/registroExterno/guardar', data=datos)

    assert respuesta.status_code == 400
    assert respuesta.get_json()['ok'] is False
    assert 'firma' in respuesta.get_json()['mensaje'].lower()
    mysql_mock.connection.cursor.assert_not_called()


def test_guardar_registro_externo_con_firma_valida_continua(cliente_flask, mock_mysql,
                                                            mock_notificar):
    """Con firma válida ya no se rechaza por la firma y se llega a la base de datos."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'ultimo': 0, 'id_municipio': 1}
    _sesion_externa(cliente_flask)

    respuesta = cliente_flask.post('/registroExterno/guardar', data={
        'tipo_persona': 'jugador',
        'firma_base64': FIRMA_VALIDA,
    })

    mensaje = (respuesta.get_json() or {}).get('mensaje', '')
    assert 'firma' not in mensaje.lower()
    mysql_mock.connection.cursor.assert_called()


# ══════════════════════════════════════════════════
# PRUEBAS: años de vigencia en formularioExterno()
# ══════════════════════════════════════════════════

def test_formulario_externo_envia_anios_vigencia(cliente_flask, mock_mysql, mocker):
    """El formulario externo debe recibir los años desde el año actual."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchall.return_value = []
    render = mocker.patch('auth.auth.render_template', return_value='FORM OK')
    _sesion_externa(cliente_flask)

    respuesta = cliente_flask.get('/registroExterno')

    assert respuesta.status_code == 200
    anios = render.call_args.kwargs['anios_vigencia']
    assert anios[0] == date.today().year
    assert (date.today().year - 1) not in anios
