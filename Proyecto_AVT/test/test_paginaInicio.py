# test/test_paginaInicio.py
# Pruebas unitarias para el módulo paginaInicio/paginaInicio.py

import pytest


# ══════════════════════════════════════════════════
# PRUEBAS PARA paginaInicio()
# ══════════════════════════════════════════════════

def test_pagina_inicio_renderiza(cliente_flask, mocker):
    """GET /paginaInicio debe renderizar la plantilla."""
    mocker.patch('paginaInicio.paginaInicio.render_template', return_value='OK')

    respuesta = cliente_flask.get('/paginaInicio')

    assert respuesta.status_code == 200


# ══════════════════════════════════════════════════
# PRUEBAS PARA notificaciones()
# ══════════════════════════════════════════════════

def test_notificaciones_sin_filtro(cliente_flask, mock_mysql, mocker):
    """GET /notificaciones sin filtro debe mostrar todas las notificaciones."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchall.return_value = []
    mocker.patch('paginaInicio.paginaInicio.render_template', return_value='OK')

    respuesta = cliente_flask.get('/notificaciones')

    assert respuesta.status_code == 200


# ══════════════════════════════════════════════════
# PRUEBAS PARA marcar_todas_leidas()
# ══════════════════════════════════════════════════

def test_marcar_todas_leidas(cliente_flask, mock_mysql):
    """POST /notificaciones/marcar_todas debe devolver ok=True."""
    respuesta = cliente_flask.post('/notificaciones/marcar_todas')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# PRUEBAS PARA marcar_leida()
# ══════════════════════════════════════════════════

def test_marcar_leida(cliente_flask, mock_mysql):
    """POST /notificaciones/marcar/1 debe devolver ok=True."""
    respuesta = cliente_flask.post('/notificaciones/marcar/1')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# PRUEBAS PARA digitalizar()
# ══════════════════════════════════════════════════

def test_digitalizar_renderiza(cliente_flask, mock_mysql, mocker):
    """GET /digitalizarDocumentos debe renderizar la plantilla."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchall.return_value = []
    mocker.patch('paginaInicio.paginaInicio.render_template', return_value='OK')

    respuesta = cliente_flask.get('/digitalizarDocumentos')

    assert respuesta.status_code == 200


# ══════════════════════════════════════════════════
# PRUEBAS PARA subir_documento()
# ══════════════════════════════════════════════════


def test_subir_documento_formato_invalido(cliente_flask, mock_mysql):
    """POST con archivo .txt debe devolver 400."""
    from io import BytesIO
    archivo_falso = (BytesIO(b'contenido'), 'documento.txt')

    respuesta = cliente_flask.post(
        '/digitalizarDocumentos/subir',
        data={
            'tipoDocumento': 'ine',
            'id_persona': '1',
            'archivo': archivo_falso
        },
        content_type='multipart/form-data'
    )

    assert respuesta.status_code == 400
    assert b'Solo PNG' in respuesta.data or 'Solo PNG' in respuesta.get_json().get('mensaje', '')


def test_subir_documento_exitoso(cliente_flask, mock_mysql, mock_notificar, tmp_path, mocker):
    """POST con datos válidos debe subir el documento."""
    from io import BytesIO
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'nombre': 'Juan Perez'}
    cursor.lastrowid = 1

    # Mockear os.path.join para que guarde en tmp_path
    mocker.patch('paginaInicio.paginaInicio.os.makedirs')
    mocker.patch('paginaInicio.paginaInicio.os.path.join', return_value=str(tmp_path / 'archivo.jpg'))

    archivo_falso = (BytesIO(b'contenido'), 'ine.jpg')

    respuesta = cliente_flask.post(
        '/digitalizarDocumentos/subir',
        data={
            'tipoDocumento': 'ine',
            'id_persona': '1',
            'tipo_persona': 'jugador',
            'archivo': archivo_falso
        },
        content_type='multipart/form-data'
    )

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# PRUEBAS PARA eliminar_documento()
# ══════════════════════════════════════════════════

def test_eliminar_documento_exitoso(cliente_flask, mock_mysql, mock_notificar, mocker):
    """POST /digitalizarDocumentos/eliminar/1 debe eliminar el documento."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = {'ruta': 'static/uploads/archivo.jpg'}
    mocker.patch('paginaInicio.paginaInicio.os.path.exists', return_value=False)

    respuesta = cliente_flask.post('/digitalizarDocumentos/eliminar/1')

    assert respuesta.status_code == 200
    assert respuesta.get_json()['ok'] is True


# ══════════════════════════════════════════════════
# PRUEBAS PARA expedientes()
# ══════════════════════════════════════════════════

def test_expedientes_renderiza(cliente_flask):
    """GET /expedientes debe renderizar la plantilla."""
    respuesta = cliente_flask.get('/expedientes')

    assert respuesta.status_code == 200
    contenido = respuesta.get_data(as_text=True)
    assert 'Reporte de expedientes activos sin fotografías' in contenido
    assert 'Expediente individual SIRED con fotografía' in contenido
    assert 'name="fecha_inicio"' in contenido
    assert 'name="fecha_fin"' in contenido


# ══════════════════════════════════════════════════
# PRUEBAS PARA buscar_expediente()
# ══════════════════════════════════════════════════


def test_buscar_expediente_con_resultados(cliente_flask, mock_mysql):
    """GET /expedientes/buscar?termino=Juan debe devolver solo 1 resultado."""
    mysql_mock, cursor = mock_mysql

    # La ruta hace 3 fetchall(): jugadores, entrenadores, árbitros.
    # Solo el primero devuelve resultado; los otros van vacíos.
    cursor.fetchall.side_effect = [
        [   # 1) jugadores → 1 resultado
            {
                'id_expediente': 1,
                'estatus': 'activo',
                'fecha_creacion': None,
                'id_persona': 1,
                'nombre_completo': 'Juan Perez',
                'numero_registro': 'JUG-001',
                'categoria': 'JUVENIL',
                'tipo': 'jugador'
            }
        ],
        [],  # 2) entrenadores → 0
        []   # 3) árbitros → 0
    ]

    respuesta = cliente_flask.get('/expedientes/buscar?termino=Juan')

    assert respuesta.status_code == 200
    data = respuesta.get_json()
    assert data['ok'] is True
    assert len(data['resultados']) == 1
    assert data['resultados'][0]['nombre'] == 'Juan Perez'


# ══════════════════════════════════════════════════
# PRUEBAS PARA generar_expediente()
# ══════════════════════════════════════════════════


def test_generar_expediente_sin_datos(cliente_flask, mock_mysql):
    """POST con id_persona inexistente debe devolver 404."""
    mysql_mock, cursor = mock_mysql
    cursor.fetchone.return_value = None

    respuesta = cliente_flask.post(
        '/expedientes/generar',
        json={'id_persona': 999, 'tipo': 'jugador'}
    )

    assert respuesta.status_code == 404
    assert respuesta.get_json()['ok'] is False


@pytest.mark.parametrize(('fecha_inicio', 'fecha_fin'), [
    ('2026-03-01', '2026-02-01'),
    ('no-es-fecha', '2026-02-01'),
])
def test_reporte_expedientes_rechaza_rango_invalido(
        cliente_flask, mock_mysql, fecha_inicio, fecha_fin):
    """Un rango inválido no debe ejecutar la consulta del reporte."""
    mysql_mock, _ = mock_mysql

    respuesta = cliente_flask.get(
        '/expedientes/reporte',
        query_string={'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
    )

    assert respuesta.status_code == 400
    assert respuesta.get_json()['ok'] is False
    mysql_mock.connection.cursor.assert_not_called()


def test_reporte_expedientes_descarga_excel_activos_sin_fotos(
        cliente_flask, mock_mysql):
    """El reporte incluye datos y filtra expedientes activos por fecha sin imágenes."""
    from datetime import date
    from io import BytesIO
    from openpyxl import load_workbook

    _, cursor = mock_mysql
    cursor.fetchall.return_value = [{
        'id_expediente': 3,
        'estatus': 'activo',
        'fecha_creacion': date(2026, 2, 10),
        'id_jugador': 12,
        'numero_registro': 'JUG-012',
        'apellido_paterno': 'PEREZ',
        'apellido_materno': 'LOPEZ',
        'nombres': 'JUAN',
        'curp': 'PELJ000101HPLRPN00',
        'fecha_nacimiento': date(2000, 1, 1),
        'nombre_estado': 'TLAXCALA',
        'nombre_municipio': 'TLAXCALA',
        'nombre_equipo': 'EQUIPO AVT',
        'nombre_liga': 'LIGA AVT',
    }]

    respuesta = cliente_flask.get(
        '/expedientes/reporte',
        query_string={'fecha_inicio': '2026-02-01', 'fecha_fin': '2026-02-28'}
    )

    assert respuesta.status_code == 200
    assert 'spreadsheet' in respuesta.content_type
    assert 'expedientes_activos_sin_fotos_20260201_20260228.xlsx' in \
        respuesta.headers['Content-Disposition']

    sql, parametros = cursor.execute.call_args.args
    assert "e.estatus = 'activo'" in sql
    assert 'e.fecha_creacion BETWEEN %s AND %s' in sql
    assert 'fotografia' not in sql.lower()
    assert parametros == (date(2026, 2, 1), date(2026, 2, 28))

    libro = load_workbook(BytesIO(respuesta.data))
    hoja = libro['Expedientes activos']
    assert hoja['A2'].value == 3
    assert hoja['F2'].value == 'PEREZ'
    assert hoja['AF2'].value == 'EQUIPO AVT'
    assert hoja._images == []


def test_generar_expediente_descarga_cedula_sired_con_foto(
        cliente_flask, mock_mysql):
    """La descarga debe ser un Excel legible con formato SIRED y fotografía."""
    from base64 import b64encode
    from io import BytesIO
    from zipfile import ZipFile
    from xml.etree import ElementTree
    from openpyxl import load_workbook
    from PIL import Image

    _, cursor = mock_mysql
    firma_png = BytesIO()
    Image.new('RGB', (40, 15), 'white').save(firma_png, format='PNG')
    firma_base64 = 'data:image/png;base64,' + b64encode(firma_png.getvalue()).decode()
    cursor.execute.side_effect = [
        Exception('la versión actual no tiene id_equipo en jugador'),
        None,
        None,
    ]
    cursor.fetchone.return_value = {
        'id_expediente': 12,
        'estatus': 'activo',
        'apellido_paterno': 'PEREZ',
        'apellido_materno': 'LOPEZ',
        'nombres': 'JUAN',
        'numero_registro': 'JUG-012',
        'curp': 'PELJ000101HPLRPN00',
        'fecha_nacimiento': '2000-01-01',
        'lugar_nacimiento': 'PUEBLA',
        'nacionalidad': 'MEXICANA',
        'peso': 70,
        'estatura': 1.75,
        'tipo_sangre': 'O+',
        'vigencia': '2025,2026',
        'ocupacion': 'ESTUDIANTE',
        'escolaridad': 'BACHILLERATO',
        'escuela': 'ESCUELA DE PRUEBA',
        'enfermedades_cronicas': 'NINGUNA',
        'medicamentos': 'NINGUNA',
        'nombre_estado': 'TLAXCALA',
        'nombre_municipio': 'TLAXCALA',
        'calle': 'AVENIDA CENTRAL',
        'numero_exterior': '10',
        'colonia': 'CENTRO',
        'codigo_postal': '90000',
        'telefono': '2460000000',
        'celular': '2461111111',
        'correo_electronico': 'juan@example.com',
        'club': 'CLUB AVT',
        'nombre_equipo': 'EQUIPO AVT',
        'nombre_liga': 'LIGA AVT',
        'categoria': 'JUVENIL',
        'rama': 'VARONIL',
        'ligas_participa': 'LIGA AVT',
        'nombre_tutor': 'MARIA LOPEZ',
        'celular_tutor': '2462222222',
        'correo_tutor': 'tutor@example.com',
        'curp_tutor': 'LOPM000101MPLRPR00',
        'fotografia': 'static/uploads/fotos/jugador/8.jpeg',
        'firma_base64': firma_base64,
    }
    cursor.fetchall.return_value = []

    respuesta = cliente_flask.post(
        '/expedientes/generar',
        json={'id_persona': 12, 'tipo': 'jugador'}
    )

    assert respuesta.status_code == 200
    assert 'spreadsheet' in respuesta.content_type

    paquete = ZipFile(BytesIO(respuesta.data))
    assert paquete.testzip() is None
    espacio_xml = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    for nombre in paquete.namelist():
        if nombre.endswith('.xml') or nombre.endswith('.rels'):
            ElementTree.fromstring(paquete.read(nombre))
    xml_hoja = ElementTree.fromstring(paquete.read('xl/worksheets/sheet1.xml'))
    rangos_combinados = xml_hoja.findall('.//x:mergeCell', espacio_xml)
    assert all(':' in rango.attrib['ref'] for rango in rangos_combinados)

    consulta_respaldo = cursor.execute.call_args_list[1].args[0]
    assert 'j.numero_registro' in consulta_respaldo
    assert 'j.lugar_nacimiento' in consulta_respaldo
    assert 'tp.nombre_completo' in consulta_respaldo

    libro = load_workbook(BytesIO(respuesta.data))
    hoja = libro['Cédula SIRED']
    assert hoja['A1'].value == 'REGISTRO DE AFILIACIÓN A LA A.V.T.'
    assert hoja['B6'].value == 'JUAN'
    assert hoja['B7'].value == 'JUG-012'
    assert hoja['B10'].value == 'PUEBLA'
    assert hoja['E24'].value == 'TLAXCALA'
    assert hoja['C39'].value == 'MARIA LOPEZ'
    assert hoja['C44'].value == 'Firma digital adjunta'
    assert len(hoja._images) == 2


# ══════════════════════════════════════════════════
# PRUEBAS PARA _formatear_tamano()
# ══════════════════════════════════════════════════


def test_formatear_tamano_cero():
    """_formatear_tamano(0) debe devolver '0 Bytes'."""
    from paginaInicio.paginaInicio import _formatear_tamano
    resultado = _formatear_tamano(0)
    assert resultado == '0 Bytes'
