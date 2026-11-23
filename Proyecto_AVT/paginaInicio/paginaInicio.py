# Adriana Nicole Guzman Ahuatzi
# Rutas para la página de inicio: notificaciones, digitalización de documentos, expediente SIRED
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, send_file
from extensiones import mysql, notificar
from datetime import date, datetime
import os, io
from werkzeug.utils import secure_filename

principal = Blueprint('principal', __name__)


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.iniciarSesion'))
        return f(*args, **kwargs)
    return decorador


# ── Página de inicio ──────────────────────────────
@principal.route("/paginaInicio")
@login_requerido
def paginaInicio():
    return render_template("paginaInicio/paginaInicio.html")


# ══════════════════════════════════════════════════
# NOTIFICACIONES
# ══════════════════════════════════════════════════

@principal.route("/notificaciones")
@login_requerido
def notificaciones():
    fecha_filtro = request.args.get('fecha', '')
    cur = mysql.connection.cursor()
    if fecha_filtro:
        cur.execute("""
            SELECT id_notificacion, mensaje, fecha, leida
            FROM notificacion
            WHERE id_usuario = %s AND DATE(fecha) = %s
            ORDER BY fecha DESC
        """, (session['id_usuario'], fecha_filtro))
    else:
        cur.execute("""
            SELECT id_notificacion, mensaje, fecha, leida
            FROM notificacion
            WHERE id_usuario = %s
            ORDER BY fecha DESC
        """, (session['id_usuario'],))
    filas = cur.fetchall()
    cur.close()

    notifs = [
        {
            'id':      f['id_notificacion'],
            'mensaje': f['mensaje'],
            'leida':   bool(f['leida']),
            'fecha':   f['fecha'].strftime('%d/%m/%Y %H:%M') if f['fecha'] else ''
        }
        for f in filas
    ]
    sin_nuevas = all(n['leida'] for n in notifs) if notifs else True
    return render_template("paginaInicio/notificaciones.html",
                           notificaciones=notifs, fecha_filtro=fecha_filtro, sin_nuevas=sin_nuevas)


@principal.route("/notificaciones/marcar_todas", methods=["POST"])
@login_requerido
def marcar_todas_leidas():
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notificacion SET leida = 1 WHERE id_usuario = %s", (session['id_usuario'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})


@principal.route("/notificaciones/marcar/<int:id_notif>", methods=["POST"])
@login_requerido
def marcar_leida(id_notif):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE notificacion SET leida = 1 WHERE id_notificacion = %s AND id_usuario = %s",
                (id_notif, session['id_usuario']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════════
# DIGITALIZAR DOCUMENTOS
# ══════════════════════════════════════════════════

@principal.route("/digitalizarDocumentos")
@login_requerido
def digitalizar():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT fd.id_formato, fd.nombre_archivo, fd.tipo, fd.fecha_subida, fd.ruta,
               CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) AS nombre_persona
        FROM formato_digital fd
        JOIN jugador j ON j.id_jugador = fd.id_jugador
        ORDER BY fd.fecha_subida DESC
    """)
    filas = cur.fetchall()
    cur.close()
    documentos = [
        {
            'id':      f['id_formato'],
            'nombre':  f['nombre_archivo'],
            'tipo':    f['tipo'],
            'fecha':   f['fecha_subida'].strftime('%d/%m/%Y') if f['fecha_subida'] else '',
            'ruta':    f['ruta'],
            'persona': f['nombre_persona'],
        }
        for f in filas
    ]
    return render_template("paginaInicio/digitalizarDocumentos.html", documentos=documentos)


@principal.route("/digitalizarDocumentos/subir", methods=["POST"])
@login_requerido
def subir_documento():
    tipo         = request.form.get('tipoDocumento')
    archivo      = request.files.get('archivo')
    id_persona   = request.form.get('id_persona')
    tipo_persona = request.form.get('tipo_persona', 'jugador')

    if not tipo or not archivo or not id_persona:
        return jsonify({'ok': False, 'mensaje': 'Datos incompletos'}), 400

    nombre_seguro = secure_filename(archivo.filename)
    ext = nombre_seguro.rsplit('.', 1)[-1].lower()
    if ext not in ('png', 'pdf', 'jpg', 'jpeg'):
        return jsonify({'ok': False, 'mensaje': 'Solo PNG, JPG y PDF'}), 400

    archivo.seek(0, 2)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano > 5 * 1024 * 1024:
        return jsonify({'ok': False, 'mensaje': 'Máximo 5 MB'}), 400

    carpeta = os.path.join('static', 'uploads', f'{tipo_persona}_{id_persona}')
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre_seguro)
    archivo.save(ruta)

    cur = mysql.connection.cursor()

    if tipo_persona == 'entrenador':
        cur.execute("""
            SELECT CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) AS nombre
            FROM entrenador WHERE id_entrenador = %s
        """, (id_persona,))
    elif tipo_persona == 'arbitro':
        cur.execute("""
            SELECT CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) AS nombre
            FROM arbitro WHERE id_arbitro = %s
        """, (id_persona,))
    else:
        cur.execute("""
            SELECT CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) AS nombre
            FROM jugador WHERE id_jugador = %s
        """, (id_persona,))

    persona = cur.fetchone()
    nombre_persona = persona['nombre'] if persona else '—'

    id_jugador_ref = id_persona

    cur.execute("""
        INSERT INTO formato_digital (id_jugador, nombre_archivo, ruta, tipo, fecha_subida)
        VALUES (%s, %s, %s, %s, NOW())
    """, (id_jugador_ref, nombre_seguro, ruta, tipo))
    mysql.connection.commit()
    nuevo_id = cur.lastrowid
    notificar(cur, session['id_usuario'],
              f"Documento '{nombre_seguro}' ({tipo}) digitalizado para {nombre_persona}.")
    mysql.connection.commit()
    cur.close()

    return jsonify({
        'ok': True, 'id': nuevo_id, 'nombre': nombre_seguro,
        'tamano': _formatear_tamano(tamano), 'tipo': tipo,
        'fecha': datetime.now().strftime('%d/%m/%Y'), 'persona': nombre_persona
    })


@principal.route("/digitalizarDocumentos/eliminar/<int:id_doc>", methods=["POST"])
@login_requerido
def eliminar_documento(id_doc):
    cur = mysql.connection.cursor()
    cur.execute("SELECT ruta FROM formato_digital WHERE id_formato = %s", (id_doc,))
    fila = cur.fetchone()
    if not fila:
        cur.close()
        return jsonify({'ok': False, 'mensaje': 'No encontrado'}), 404
    if os.path.exists(fila['ruta']):
        os.remove(fila['ruta'])
    cur.execute("DELETE FROM formato_digital WHERE id_formato = %s", (id_doc,))
    mysql.connection.commit()
    notificar(cur, session['id_usuario'], f"Documento #{id_doc} eliminado del sistema.")
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════════
# EXPEDIENTE SIRED
# ══════════════════════════════════════════════════

@principal.route("/expedientes")
@login_requerido
def expedientes():
    return render_template("paginaInicio/expedientes.html")


@principal.route("/expedientes/buscar")
@login_requerido
def buscar_expediente():
    """
    Busca por nombre o número de registro en las tres tablas:
    jugador (con expediente), entrenador y arbitro.
    Acepta un parámetro opcional 'tipo' para filtrar por:
    jugador, arbitro, entrenador.
    """
    termino = request.args.get('termino', '').strip()
    tipo_filtro = request.args.get('tipo', '').strip()

    if not termino:
        return jsonify({'ok': False, 'mensaje': 'Ingrese un nombre o número'}), 400

    cur = mysql.connection.cursor()
    resultados = []

    # ── Jugadores (con o sin expediente) ─────────
    if not tipo_filtro or tipo_filtro == 'jugador':
        try:
            cur.execute("""
                SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                       j.id_jugador AS id_persona,
                       CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) AS nombre_completo,
                       j.numero_registro, j.categoria, 'jugador' AS tipo
                FROM jugador j
                LEFT JOIN expediente e ON e.id_jugador = j.id_jugador
                WHERE CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) LIKE %s
                   OR COALESCE(j.numero_registro,'') LIKE %s
                   OR CAST(j.id_jugador AS CHAR) LIKE %s
            """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
        except Exception:
            cur.execute("""
                SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                       j.id_jugador AS id_persona,
                       CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) AS nombre_completo,
                       NULL AS numero_registro, NULL AS categoria, 'jugador' AS tipo
                FROM jugador j
                LEFT JOIN expediente e ON e.id_jugador = j.id_jugador
                WHERE CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) LIKE %s
                   OR CAST(j.id_jugador AS CHAR) LIKE %s
            """, (f'%{termino}%', f'%{termino}%'))
        resultados += cur.fetchall()

    # ── Entrenadores ──────────────────────────────
    if not tipo_filtro or tipo_filtro == 'entrenador':
        try:
            cur.execute("""
                SELECT NULL AS id_expediente, 'activo' AS estatus, fecha_registro AS fecha_creacion,
                       id_entrenador AS id_persona,
                       CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) AS nombre_completo,
                       numero_registro, categoria, 'entrenador' AS tipo
                FROM entrenador
                WHERE CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) LIKE %s
                   OR COALESCE(numero_registro,'') LIKE %s
                   OR CAST(id_entrenador AS CHAR) LIKE %s
            """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
            resultados += cur.fetchall()
        except Exception:
            pass

    # ── Árbitros ──────────────────────────────────
    if not tipo_filtro or tipo_filtro == 'arbitro':
        try:
            cur.execute("""
                SELECT NULL AS id_expediente, 'activo' AS estatus, fecha_registro AS fecha_creacion,
                       id_arbitro AS id_persona,
                       CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) AS nombre_completo,
                       numero_registro, categoria, 'arbitro' AS tipo
                FROM arbitro
                WHERE CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) LIKE %s
                   OR COALESCE(numero_registro,'') LIKE %s
                   OR CAST(id_arbitro AS CHAR) LIKE %s
            """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
            resultados += cur.fetchall()
        except Exception:
            pass

    cur.close()

    if not resultados:
        return jsonify({'ok': False, 'mensaje': 'No se encontraron coincidencias'}), 404

    data = [
        {
            'id_expediente':   r['id_expediente'],
            'estatus':         r['estatus'],
            'fecha_creacion':  r['fecha_creacion'].strftime('%d/%m/%Y') if r['fecha_creacion'] else '—',
            'id_persona':      r['id_persona'],
            'nombre':          r['nombre_completo'],
            'numero_registro': r['numero_registro'] or '—',
            'categoria':       r['categoria'] or '—',
            'tipo':            r['tipo']
        }
        for r in resultados
    ]
    return jsonify({'ok': True, 'resultados': data})


@principal.route("/expedientes/reporte")
@login_requerido
def generar_reporte_expedientes():
    fecha_inicio_texto = request.args.get('fecha_inicio', '').strip()
    fecha_fin_texto = request.args.get('fecha_fin', '').strip()
    try:
        fecha_inicio = date.fromisoformat(fecha_inicio_texto)
        fecha_fin = date.fromisoformat(fecha_fin_texto)
    except ValueError:
        return jsonify({
            'ok': False,
            'mensaje': 'Selecciona un rango de fechas válido.'
        }), 400

    if fecha_inicio > fecha_fin:
        return jsonify({
            'ok': False,
            'mensaje': 'La fecha inicial no puede ser posterior a la fecha final.'
        }), 400

    cur = mysql.connection.cursor()
    parametros = (fecha_inicio, fecha_fin)
    try:
        try:
            cur.execute("""
                SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                       j.id_jugador, j.numero_registro,
                       j.apellido_paterno, j.apellido_materno, j.nombres,
                       j.curp, j.fecha_nacimiento, j.lugar_nacimiento, j.nacionalidad,
                       j.vigencia, j.peso, j.estatura, j.tipo_sangre,
                       j.ocupacion, j.escolaridad, j.escuela,
                       j.enfermedades_cronicas, j.medicamentos,
                       j.telefono, j.celular, j.correo_electronico,
                       j.club, j.categoria, j.rama, j.ligas_participa,
                       d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                       m.nombre AS nombre_municipio, ce.nombre AS nombre_estado,
                       (SELECT tp.nombre_completo FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS nombre_tutor,
                       (SELECT tp.celular FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS celular_tutor,
                       (SELECT tp.correo_electronico FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS correo_tutor,
                       (SELECT tp.curp_tutor FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS curp_tutor,
                       eq.nombre_equipo, l.nombre_liga
                FROM expediente e
                JOIN jugador j ON j.id_jugador = e.id_jugador
                LEFT JOIN direccion d ON d.id_jugador = j.id_jugador
                LEFT JOIN cat_municipio m ON m.id_municipio = d.id_municipio
                LEFT JOIN cat_estado ce ON ce.id_estado = m.id_estado
                LEFT JOIN equipo eq ON eq.id_equipo = j.id_equipo
                LEFT JOIN liga l ON l.id_liga = eq.id_liga
                WHERE e.estatus = 'activo'
                  AND e.fecha_creacion BETWEEN %s AND %s
                ORDER BY e.fecha_creacion, j.apellido_paterno,
                         j.apellido_materno, j.nombres
            """, parametros)
        except Exception:
            cur.execute("""
                SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                       j.id_jugador, NULL AS numero_registro,
                       j.apellido_paterno, j.apellido_materno, j.nombres,
                       j.curp, j.fecha_nacimiento, j.lugar_nacimiento, j.nacionalidad,
                       NULL AS vigencia, j.peso, j.estatura, NULL AS tipo_sangre,
                       j.ocupacion, j.escolaridad, j.escuela,
                       j.enfermedades_cronicas, j.medicamentos,
                       j.telefono, j.celular, j.correo_electronico,
                       NULL AS club, NULL AS categoria, NULL AS rama,
                       NULL AS ligas_participa,
                       d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                       m.nombre AS nombre_municipio, ce.nombre AS nombre_estado,
                       (SELECT tp.nombre_completo FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS nombre_tutor,
                       (SELECT tp.celular FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS celular_tutor,
                       (SELECT tp.correo_electronico FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS correo_tutor,
                       (SELECT tp.curp_tutor FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS curp_tutor,
                       NULL AS nombre_equipo, NULL AS nombre_liga
                FROM expediente e
                JOIN jugador j ON j.id_jugador = e.id_jugador
                LEFT JOIN direccion d ON d.id_jugador = j.id_jugador
                LEFT JOIN cat_municipio m ON m.id_municipio = d.id_municipio
                LEFT JOIN cat_estado ce ON ce.id_estado = m.id_estado
                WHERE e.estatus = 'activo'
                  AND e.fecha_creacion BETWEEN %s AND %s
                ORDER BY e.fecha_creacion, j.apellido_paterno,
                         j.apellido_materno, j.nombres
            """, parametros)
        filas = cur.fetchall()
    except Exception:
        cur.close()
        return jsonify({
            'ok': False,
            'mensaje': 'No fue posible consultar los expedientes para el reporte.'
        }), 500
    cur.close()

    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill

    columnas = [
        ('id_expediente', 'ID expediente', 14),
        ('fecha_creacion', 'Fecha de creación', 18),
        ('estatus', 'Estatus', 14),
        ('id_jugador', 'ID jugador', 14),
        ('numero_registro', 'No. registro', 18),
        ('apellido_paterno', 'Apellido paterno', 22),
        ('apellido_materno', 'Apellido materno', 22),
        ('nombres', 'Nombre(s)', 24),
        ('curp', 'CURP', 22),
        ('fecha_nacimiento', 'Fecha de nacimiento', 20),
        ('lugar_nacimiento', 'Lugar de nacimiento', 22),
        ('nacionalidad', 'Nacionalidad', 18),
        ('vigencia', 'Vigencia', 18),
        ('peso', 'Peso (kg)', 12),
        ('estatura', 'Estatura (m)', 14),
        ('tipo_sangre', 'Tipo de sangre', 14),
        ('ocupacion', 'Ocupación', 22),
        ('escolaridad', 'Escolaridad', 22),
        ('escuela', 'Escuela', 28),
        ('enfermedades_cronicas', 'Enfermedades crónicas', 28),
        ('medicamentos', 'Medicamentos', 28),
        ('nombre_estado', 'Estado', 20),
        ('nombre_municipio', 'Municipio', 22),
        ('calle', 'Calle', 30),
        ('numero_exterior', 'No. exterior', 15),
        ('colonia', 'Colonia', 24),
        ('codigo_postal', 'C.P.', 12),
        ('telefono', 'Teléfono', 18),
        ('celular', 'Celular', 18),
        ('correo_electronico', 'Correo electrónico', 32),
        ('club', 'Club', 24),
        ('nombre_equipo', 'Equipo', 24),
        ('categoria', 'Categoría', 18),
        ('rama', 'Rama', 16),
        ('nombre_liga', 'Liga del equipo', 24),
        ('ligas_participa', 'Ligas en las que participa', 32),
        ('nombre_tutor', 'Nombre del tutor', 28),
        ('celular_tutor', 'Celular del tutor', 20),
        ('correo_tutor', 'Correo del tutor', 32),
        ('curp_tutor', 'CURP del tutor', 22),
    ]

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expedientes activos"
    ws.append([columna[1] for columna in columnas])
    for celda in ws[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor="7A0C0C")
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for fila in filas:
        ws.append([fila.get(clave) for clave, _, _ in columnas])
    for indice, (_, _, ancho) in enumerate(columnas, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(indice)].width = ancho
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    ws.sheet_view.showGridLines = False

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=(
            f"expedientes_activos_sin_fotos_"
            f"{fecha_inicio:%Y%m%d}_{fecha_fin:%Y%m%d}.xlsx"
        )
    )


@principal.route("/expedientes/generar", methods=["POST"])
@login_requerido
def generar_expediente():
    # CAMBIO: se recibe id_persona en lugar de id_expediente
    id_persona = request.json.get('id_persona')
    tipo       = request.json.get('tipo', 'jugador')

    if not id_persona:
        return jsonify({'ok': False, 'mensaje': 'Datos requeridos'}), 400

    cur = mysql.connection.cursor()

    if tipo == 'jugador':
        try:
            cur.execute("""
                SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                       j.id_jugador, j.apellido_paterno, j.apellido_materno, j.nombres,
                       j.curp, j.fecha_nacimiento, j.lugar_nacimiento, j.nacionalidad,
                       j.peso, j.estatura,
                       j.ocupacion, j.escolaridad, j.escuela,
                       j.telefono, j.celular, j.correo_electronico,
                       j.fotografia, j.firma_base64,
                       j.medicamentos,
                       j.numero_registro, j.categoria, j.tipo_sangre,
                       j.club, j.ligas_participa, j.vigencia, j.rama,
                       j.enfermedades_cronicas,
                       d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                       COALESCE(d.nombre_municipio, m.nombre) AS nombre_municipio,
                       ce.nombre AS nombre_estado,
                       (SELECT tp.nombre_completo FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS nombre_tutor,
                       (SELECT tp.celular FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS celular_tutor,
                       (SELECT tp.correo_electronico FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS correo_tutor,
                       (SELECT tp.curp_tutor FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS curp_tutor,
                       eq.nombre_equipo, l.nombre_liga
                FROM jugador j
                LEFT JOIN expediente e ON e.id_jugador = j.id_jugador
                LEFT JOIN direccion d     ON d.id_jugador  = j.id_jugador
                LEFT JOIN cat_municipio m ON m.id_municipio = d.id_municipio
                LEFT JOIN cat_estado ce   ON ce.id_estado = m.id_estado
                LEFT JOIN equipo eq       ON eq.id_equipo   = j.id_equipo
                LEFT JOIN liga l          ON l.id_liga       = eq.id_liga
                WHERE j.id_jugador = %s
            """, (id_persona,))
        except Exception:
            cur.execute("""
                SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                       j.id_jugador, j.apellido_paterno, j.apellido_materno, j.nombres,
                       j.curp, j.fecha_nacimiento, j.lugar_nacimiento, j.nacionalidad,
                       j.peso, j.estatura,
                       j.ocupacion, j.escolaridad, j.escuela,
                       j.telefono, j.celular, j.correo_electronico,
                       j.fotografia, j.firma_base64, j.medicamentos,
                       j.numero_registro, j.categoria, j.tipo_sangre, j.club,
                       j.ligas_participa, j.vigencia, j.rama,
                       j.enfermedades_cronicas,
                       d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                       COALESCE(d.nombre_municipio, m.nombre) AS nombre_municipio,
                       ce.nombre AS nombre_estado,
                       (SELECT tp.nombre_completo FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS nombre_tutor,
                       (SELECT tp.celular FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS celular_tutor,
                       (SELECT tp.correo_electronico FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS correo_tutor,
                       (SELECT tp.curp_tutor FROM tutor_padre tp
                        WHERE tp.id_jugador = j.id_jugador ORDER BY tp.id_tutor LIMIT 1) AS curp_tutor,
                       NULL AS nombre_equipo, NULL AS nombre_liga
                FROM jugador j
                LEFT JOIN expediente e ON e.id_jugador = j.id_jugador
                LEFT JOIN direccion d     ON d.id_jugador  = j.id_jugador
                LEFT JOIN cat_municipio m ON m.id_municipio = d.id_municipio
                LEFT JOIN cat_estado ce   ON ce.id_estado = m.id_estado
                WHERE j.id_jugador = %s
            """, (id_persona,))

    elif tipo == 'entrenador':
        cur.execute("""
            SELECT id_entrenador AS id_expediente, 'activo' AS estatus,
                   fecha_registro AS fecha_creacion,
                   id_entrenador, apellido_paterno, apellido_materno, nombres,
                   curp, fecha_nacimiento, lugar_nacimiento, nacionalidad,
                   numero_registro, categoria,
                   tipo_sangre, peso, estatura,
                   club, ligas_participa, vigencia, rama,
                   enfermedades_cronicas, medicamentos,
                   ocupacion, escolaridad, escuela,
                   telefono, celular, correo_electronico, fotografia,
                   firma_base64,
                   d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                   COALESCE(d.nombre_municipio, m.nombre) AS nombre_municipio,
                   ce.nombre AS nombre_estado,
                   eq.nombre_equipo, l.nombre_liga,
                   cedula, especialidad
            FROM entrenador
            LEFT JOIN direccion d ON d.id_direccion = entrenador.id_direccion
            LEFT JOIN cat_municipio m ON m.id_municipio = d.id_municipio
            LEFT JOIN cat_estado ce ON ce.id_estado = m.id_estado
            LEFT JOIN equipo eq ON eq.id_equipo = entrenador.id_equipo
            LEFT JOIN liga l ON l.id_liga = eq.id_liga
            WHERE id_entrenador = %s
        """, (id_persona,))

    elif tipo == 'arbitro':
        cur.execute("""
            SELECT id_arbitro AS id_expediente, 'activo' AS estatus,
                   fecha_registro AS fecha_creacion,
                   id_arbitro, apellido_paterno, apellido_materno, nombres,
                   curp, fecha_nacimiento, lugar_nacimiento, nacionalidad,
                   numero_registro, categoria,
                   tipo_sangre, peso, estatura,
                   club, ligas_participa, vigencia, rama,
                   enfermedades_cronicas, medicamentos,
                   ocupacion, escolaridad, escuela,
                   telefono, celular, correo_electronico, fotografia,
                   firma_base64,
                   d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                   COALESCE(d.nombre_municipio, m.nombre) AS nombre_municipio,
                   ce.nombre AS nombre_estado,
                   eq.nombre_equipo, l.nombre_liga,
                   zona, licencia
            FROM arbitro
            LEFT JOIN direccion d ON d.id_direccion = arbitro.id_direccion
            LEFT JOIN cat_municipio m ON m.id_municipio = d.id_municipio
            LEFT JOIN cat_estado ce ON ce.id_estado = m.id_estado
            LEFT JOIN equipo eq ON eq.id_equipo = arbitro.id_equipo
            LEFT JOIN liga l ON l.id_liga = eq.id_liga
            WHERE id_arbitro = %s
        """, (id_persona,))
    else:
        cur.close()
        return jsonify({'ok': False, 'mensaje': 'Tipo inválido'}), 400

    fila = cur.fetchone()

    sanciones = []
    if tipo == 'jugador' and fila:
        try:
            cur.execute("""
                SELECT s.tipo_sancion, s.fecha_sancion, s.fecha_fin_sancion,
                       s.motivo, s.estatus, l.nombre_liga
                FROM sanciones s
                LEFT JOIN liga l ON l.id_liga = s.id_liga
                WHERE s.id_jugador = %s
                ORDER BY s.fecha_sancion DESC
            """, (fila['id_jugador'],))
            sanciones = cur.fetchall()
        except Exception:
            pass

    cur.close()

    if not fila:
        return jsonify({'ok': False, 'mensaje': 'Sin datos'}), 404

    import base64
    import binascii
    import openpyxl
    from openpyxl.drawing.image import Image as ExcelImage
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.worksheet.page import PageMargins

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cédula SIRED"

    vino = "7A0C0C"
    vino_claro = "F4E7E7"
    blanco = "FFFFFF"
    gris = "555555"
    borde = Side(style="thin", color="B7A2A2")
    borde_celda = Border(left=borde, right=borde, top=borde, bottom=borde)
    titulo_font = Font(bold=True, size=15, color=blanco)
    subtitulo_font = Font(bold=True, size=12, color=vino)
    etiqueta_font = Font(bold=True, size=9, color=vino)
    valor_font = Font(size=10, color=gris)
    relleno_titulo = PatternFill("solid", fgColor=vino)
    relleno_seccion = PatternFill("solid", fgColor=vino_claro)
    centrado = Alignment(horizontal="center", vertical="center", wrap_text=True)
    alineado = Alignment(vertical="center", wrap_text=True)
    imagenes = []

    for columna, ancho in zip("ABCDEF", (20, 15, 15, 20, 15, 15)):
        ws.column_dimensions[columna].width = ancho

    def fusionar(fila_excel, columna_inicio, columna_fin, texto, estilo):
        if columna_inicio != columna_fin:
            ws.merge_cells(start_row=fila_excel, start_column=columna_inicio,
                           end_row=fila_excel, end_column=columna_fin)
        celda = ws.cell(fila_excel, columna_inicio, texto)
        celda.alignment = centrado if estilo == "titulo" else alineado
        celda.border = borde_celda
        if estilo == "titulo":
            celda.font = titulo_font
            celda.fill = relleno_titulo
        elif estilo == "subtitulo":
            celda.font = subtitulo_font
        elif estilo == "seccion":
            celda.font = Font(bold=True, color=vino, size=10)
            celda.fill = relleno_seccion
        elif estilo == "etiqueta":
            celda.font = etiqueta_font
            celda.fill = relleno_seccion
        else:
            celda.font = valor_font

    def seccion(fila_excel, texto):
        fusionar(fila_excel, 1, 6, texto, "seccion")
        ws.row_dimensions[fila_excel].height = 21

    def campo(fila_excel, etiqueta, valor, lado="izquierdo"):
        columna = 1 if lado == "izquierdo" else 4
        fusionar(fila_excel, columna, columna, etiqueta, "etiqueta")
        fusionar(fila_excel, columna + 1, columna + 2, valor or "—", "valor")
        ws.row_dimensions[fila_excel].height = 25

    def campo_completo(fila_excel, etiqueta, valor):
        fusionar(fila_excel, 1, 2, etiqueta, "etiqueta")
        fusionar(fila_excel, 3, 6, valor or "—", "valor")
        ws.row_dimensions[fila_excel].height = 30

    def valor_texto(valor):
        return str(valor) if valor is not None and valor != "" else "—"

    tipo_label = {"jugador": "JUGADOR", "entrenador": "ENTRENADOR", "arbitro": "ÁRBITRO"}
    fusionar(1, 1, 6, "REGISTRO DE AFILIACIÓN A LA A.V.T.", "titulo")
    fusionar(2, 1, 6, f"CÉDULA RED FMVB — {tipo_label.get(tipo, tipo.upper())}", "subtitulo")
    campo(3, "No. expediente", valor_texto(fila.get("id_expediente")))
    campo(3, "Estatus", valor_texto(fila.get("estatus")), "derecho")

    for numero, etiqueta, clave in (
        (4, "Apellido paterno", "apellido_paterno"),
        (5, "Apellido materno", "apellido_materno"),
        (6, "Nombre(s)", "nombres"),
        (7, "No. registro", "numero_registro"),
        (8, "CURP", "curp"),
        (9, "Fecha nacimiento", "fecha_nacimiento"),
        (10, "Lugar nacimiento", "lugar_nacimiento"),
        (11, "Nacionalidad", "nacionalidad"),
    ):
        fusionar(numero, 1, 1, etiqueta, "etiqueta")
        fusionar(numero, 2, 4, valor_texto(fila.get(clave)), "valor")
        ws.row_dimensions[numero].height = 25

    fusionar(4, 5, 6, "FOTOGRAFÍA", "etiqueta")
    foto = fila.get("fotografia")
    foto_insertada = False
    if foto:
        raiz_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        raiz_uploads = os.path.abspath(os.path.join(raiz_proyecto, "static", "uploads"))
        ruta_foto = os.path.abspath(foto if os.path.isabs(foto)
                                    else os.path.join(raiz_proyecto, foto))
        try:
            foto_en_uploads = os.path.commonpath((raiz_uploads, ruta_foto)) == raiz_uploads
        except ValueError:
            foto_en_uploads = False
        if foto_en_uploads and os.path.isfile(ruta_foto):
            imagen = ExcelImage(ruta_foto)
            escala = min(130 / imagen.width, 155 / imagen.height, 1)
            imagen.width = int(imagen.width * escala)
            imagen.height = int(imagen.height * escala)
            imagen.anchor = "E5"
            ws.add_image(imagen)
            imagenes.append(imagen)
            foto_insertada = True
    ws.merge_cells("E5:F11")
    if not foto_insertada:
        celda_foto = ws["E5"]
        celda_foto.value = "Fotografía no disponible"
        celda_foto.font = valor_font
        celda_foto.alignment = centrado
        celda_foto.border = borde_celda
    for numero in range(5, 12):
        ws.row_dimensions[numero].height = 25

    campo_completo(12, "Fecha de registro", valor_texto(fila.get("fecha_creacion")))
    seccion(13, "DATOS PERSONALES")
    campo(14, "Vigencia", valor_texto(fila.get("vigencia")))
    campo(14, "Peso (kg)", valor_texto(fila.get("peso")), "derecho")
    campo(15, "Estatura (m)", valor_texto(fila.get("estatura")))
    campo(15, "Tipo de sangre", valor_texto(fila.get("tipo_sangre")), "derecho")
    campo(16, "Ocupación", valor_texto(fila.get("ocupacion")))
    campo(16, "Escolaridad", valor_texto(fila.get("escolaridad")), "derecho")
    campo_completo(17, "Escuela", valor_texto(fila.get("escuela")))

    seccion(19, "SALUD")
    enfermedades = fila.get("enfermedades_cronicas")
    if enfermedades in (None, 0, "0", ""):
        enfermedades = "NINGUNA"
    elif enfermedades == 1:
        enfermedades = "SÍ (ver expediente físico)"
    campo_completo(20, "Enfermedades crónicas", valor_texto(enfermedades))
    campo_completo(21, "Medicamentos", valor_texto(fila.get("medicamentos") or "NINGUNA"))

    seccion(23, "DOMICILIO Y CONTACTO")
    campo(24, "Estado de residencia", valor_texto(fila.get("nombre_estado")))
    campo(24, "Municipio", valor_texto(fila.get("nombre_municipio")), "derecho")
    campo(25, "Dirección", valor_texto(
        " ".join(filter(None, (fila.get("calle"), fila.get("numero_exterior"))))))
    campo(25, "Colonia", valor_texto(fila.get("colonia")), "derecho")
    campo(26, "C.P.", valor_texto(fila.get("codigo_postal")))
    campo(26, "Teléfono", valor_texto(fila.get("telefono")), "derecho")
    campo(27, "Celular", valor_texto(fila.get("celular")))
    campo(27, "Correo electrónico", valor_texto(fila.get("correo_electronico")), "derecho")

    seccion(29, "INFORMACIÓN DEPORTIVA")
    campo(30, "Club y/o escuela", valor_texto(fila.get("club")))
    campo(30, "Equipo", valor_texto(fila.get("nombre_equipo")), "derecho")
    campo(31, "Categoría", valor_texto(fila.get("categoria")))
    campo(31, "Rama", valor_texto(fila.get("rama")), "derecho")
    campo(32, "Liga", valor_texto(fila.get("nombre_liga")))
    campo_completo(33, "Ligas en las que participa", valor_texto(fila.get("ligas_participa")))

    if tipo == "entrenador":
        seccion(35, "DATOS DEL ENTRENADOR")
        campo(36, "Cédula", valor_texto(fila.get("cedula")))
        campo(36, "Especialidad", valor_texto(fila.get("especialidad")), "derecho")
    elif tipo == "arbitro":
        seccion(35, "DATOS DEL ÁRBITRO")
        campo(36, "Licencia", valor_texto(fila.get("licencia")))
        campo(36, "Zona", valor_texto(fila.get("zona")), "derecho")

    fila_tutor = 38
    if tipo == "jugador":
        seccion(fila_tutor, "PADRE O TUTOR (en caso de minoría de edad)")
        campo_completo(fila_tutor + 1, "Nombre completo", valor_texto(fila.get("nombre_tutor")))
        campo(fila_tutor + 2, "Celular", valor_texto(fila.get("celular_tutor")))
        campo(fila_tutor + 2, "Correo electrónico", valor_texto(fila.get("correo_tutor")), "derecho")
        campo_completo(fila_tutor + 3, "CURP del tutor", valor_texto(fila.get("curp_tutor")))
        fila_firmas = fila_tutor + 5
    else:
        fila_firmas = fila_tutor

    seccion(fila_firmas, "FIRMAS")
    campo_completo(fila_firmas + 1, "Firma del afiliado", "____________________________")
    firma = fila.get("firma_base64")
    prefijo_firma = "data:image/png;base64,"
    if isinstance(firma, str) and firma.startswith(prefijo_firma):
        try:
            contenido_firma = base64.b64decode(firma[len(prefijo_firma):], validate=True)
            firma_imagen = ExcelImage(io.BytesIO(contenido_firma))
            escala_firma = min(150 / firma_imagen.width, 45 / firma_imagen.height, 1)
            firma_imagen.width = int(firma_imagen.width * escala_firma)
            firma_imagen.height = int(firma_imagen.height * escala_firma)
            firma_imagen.anchor = f"C{fila_firmas + 1}"
            ws.add_image(firma_imagen)
            imagenes.append(firma_imagen)
            ws.cell(fila_firmas + 1, 3).value = "Firma digital adjunta"
        except (binascii.Error, OSError, ValueError):
            ws.cell(fila_firmas + 1, 3).value = "Firma no disponible: imagen inválida"
    campo(fila_firmas + 2, "Nombre y firma del representante",
          "____________________________", "izquierdo")
    if tipo == "jugador":
        campo(fila_firmas + 2, "Firma del padre o tutor",
              "____________________________", "derecho")
    fusionar(fila_firmas + 4, 1, 6,
             "De conformidad con los reglamentos de la AVT.", "subtitulo")

    ws.freeze_panes = "A4"
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.25, right=0.25, top=0.35, bottom=0.35,
                                  header=0.15, footer=0.15)
    ws.print_area = f"A1:F{fila_firmas + 4}"

    if sanciones:
        hoja_sanciones = wb.create_sheet("Sanciones")
        hoja_sanciones.append(["Tipo", "Liga", "Fecha", "Fecha fin", "Motivo", "Estatus"])
        for celda in hoja_sanciones[1]:
            celda.font = Font(bold=True, color=blanco)
            celda.fill = relleno_titulo
        for sancion in sanciones:
            hoja_sanciones.append([
                sancion.get("tipo_sancion") or "—",
                sancion.get("nombre_liga") or "—",
                valor_texto(sancion.get("fecha_sancion")),
                valor_texto(sancion.get("fecha_fin_sancion")),
                sancion.get("motivo") or "—",
                sancion.get("estatus") or "—",
            ])
        for columna, ancho in zip("ABCDEF", (20, 24, 16, 16, 45, 16)):
            hoja_sanciones.column_dimensions[columna].width = ancho
        hoja_sanciones.freeze_panes = "A2"

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return send_file(output,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name=f"expediente_{id_persona}.xlsx")


# ── Utilidad ──────────────────────────────────────
def _formatear_tamano(bytes):
    if not bytes:
        return '0 Bytes'
    for unidad in ['Bytes', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unidad}"
        bytes /= 1024
    return f"{bytes:.1f} GB"