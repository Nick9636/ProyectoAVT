# Adriana Nicole Guzman Ahuatzi
#01/04/2026
# Rutas para la página de inicio: notificaciones, digitalización de documentos, expediente SIRED
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensiones import mysql, notificar
from datetime import datetime
import os
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
            WHERE id_usuario = %s
              AND DATE(fecha) = %s
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

    return render_template(
        "paginaInicio/notificaciones.html",
        notificaciones=notifs,
        fecha_filtro=fecha_filtro,
        sin_nuevas=sin_nuevas
    )


@principal.route("/notificaciones/marcar_todas", methods=["POST"])
@login_requerido
def marcar_todas_leidas():
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE notificacion SET leida = 1
        WHERE id_usuario = %s
    """, (session['id_usuario'],))
    mysql.connection.commit()
    cur.close()
    return jsonify({'ok': True})


@principal.route("/notificaciones/marcar/<int:id_notif>", methods=["POST"])
@login_requerido
def marcar_leida(id_notif):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE notificacion SET leida = 1
        WHERE id_notificacion = %s AND id_usuario = %s
    """, (id_notif, session['id_usuario']))
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
        SELECT id_formato, nombre_archivo, tipo, fecha_subida, ruta
        FROM formato_digital
        WHERE id_jugador = %s
        ORDER BY fecha_subida DESC
    """, (session['id_usuario'],))
    filas = cur.fetchall()
    cur.close()

    documentos = [
        {
            'id':     f['id_formato'],
            'nombre': f['nombre_archivo'],
            'tipo':   f['tipo'],
            'fecha':  f['fecha_subida'].strftime('%d/%m/%Y') if f['fecha_subida'] else '',
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
    tipo_persona = request.form.get('tipo_persona')  # jugador, entrenador, arbitro

    if not tipo or not archivo or not id_persona or not tipo_persona:
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

    # ── Carpeta por tipo y id de persona ─────────
    # Ej: static/uploads/jugador_45/
    carpeta = os.path.join('static', 'uploads', f'{tipo_persona}_{id_persona}')
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, nombre_seguro)
    archivo.save(ruta)

    # Buscar nombre de la persona para devolverlo al frontend
    cur = mysql.connection.cursor()
    tabla = {'jugador': 'jugador', 'entrenador': 'entrenador', 'arbitro': 'arbitro'}
    pk    = {'jugador': 'id_jugador', 'entrenador': 'id_entrenador', 'arbitro': 'id_arbitro'}
    cur.execute(f"""
        SELECT CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) AS nombre
        FROM {tabla[tipo_persona]}
        WHERE {pk[tipo_persona]} = %s
    """, (id_persona,))
    persona = cur.fetchone()
    nombre_persona = persona['nombre'] if persona else '—'

    # Insertar en formato_digital
    cur.execute("""
        INSERT INTO formato_digital
            (id_jugador, nombre_archivo, ruta, tipo, fecha_subida)
        VALUES (%s, %s, %s, %s, NOW())
    """, (id_persona, nombre_seguro, ruta, tipo))
    mysql.connection.commit()
    nuevo_id = cur.lastrowid
    notificar(cur, session['id_usuario'],
              f"Documento '{nombre_seguro}' ({tipo}) digitalizado para {nombre_persona}.")
    mysql.connection.commit()
    cur.close()

    return jsonify({
        'ok':      True,
        'id':      nuevo_id,
        'nombre':  nombre_seguro,
        'tamano':  _formatear_tamano(tamano),
        'tipo':    tipo,
        'fecha':   datetime.now().strftime('%d/%m/%Y'),
        'persona': nombre_persona
    })

@principal.route("/digitalizarDocumentos/eliminar/<int:id_doc>", methods=["POST"])
@login_requerido
def eliminar_documento(id_doc):
    cur = mysql.connection.cursor()

    # Columnas correctas: id_formato y ruta
    cur.execute("""
        SELECT ruta FROM formato_digital
        WHERE id_formato = %s AND id_jugador = %s
    """, (id_doc, session['id_usuario']))
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
    termino = request.args.get('termino', '').strip()

    if not termino:
        return jsonify({'ok': False, 'mensaje': 'Ingrese un nombre o número'}), 400

    cur = mysql.connection.cursor()
    resultados = []

    # ── Buscar en jugadores ───────────────────────
    cur.execute("""
        SELECT e.id_expediente, e.estatus, e.fecha_creacion,
               j.id_jugador AS id_persona,
               CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) AS nombre_completo,
               j.numero_registro, j.categoria,
               'jugador' AS tipo
        FROM expediente e
        JOIN jugador j ON j.id_jugador = e.id_jugador
        WHERE e.tipo_persona = 'jugador'
          AND (
              CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) LIKE %s
              OR j.numero_registro LIKE %s
              OR CAST(j.id_jugador AS CHAR) LIKE %s
          )
    """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
    resultados += cur.fetchall()

    # ── Buscar en entrenadores ────────────────────
    cur.execute("""
        SELECT e.id_expediente, e.estatus, e.fecha_creacion,
               en.id_entrenador AS id_persona,
               CONCAT(en.apellido_paterno,' ',en.apellido_materno,' ',en.nombres) AS nombre_completo,
               en.numero_registro, en.categoria,
               'entrenador' AS tipo
        FROM expediente e
        JOIN entrenador en ON en.id_entrenador = e.id_entrenador
        WHERE e.tipo_persona = 'entrenador'
          AND (
              CONCAT(en.apellido_paterno,' ',en.apellido_materno,' ',en.nombres) LIKE %s
              OR en.numero_registro LIKE %s
              OR CAST(en.id_entrenador AS CHAR) LIKE %s
          )
    """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
    resultados += cur.fetchall()

    # ── Buscar en árbitros ────────────────────────
    cur.execute("""
        SELECT e.id_expediente, e.estatus, e.fecha_creacion,
               a.id_arbitro AS id_persona,
               CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres) AS nombre_completo,
               a.numero_registro, a.categoria,
               'arbitro' AS tipo
        FROM expediente e
        JOIN arbitro a ON a.id_arbitro = e.id_arbitro
        WHERE e.tipo_persona = 'arbitro'
          AND (
              CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres) LIKE %s
              OR a.numero_registro LIKE %s
              OR CAST(a.id_arbitro AS CHAR) LIKE %s
          )
    """, (f'%{termino}%', f'%{termino}%', f'%{termino}%'))
    resultados += cur.fetchall()
    cur.close()

    if not resultados:
        return jsonify({'ok': False, 'mensaje': 'No se encontraron coincidencias'}), 404

    data = [
        {
            'id_expediente':  r['id_expediente'],
            'estatus':        r['estatus'],
            'fecha_creacion': r['fecha_creacion'].strftime('%d/%m/%Y') if r['fecha_creacion'] else '',
            'id_persona':     r['id_persona'],
            'nombre':         r['nombre_completo'],
            'numero_registro': r['numero_registro'] or '—',
            'categoria':      r['categoria'] or '—',
            'tipo':           r['tipo']
        }
        for r in resultados
    ]

    return jsonify({'ok': True, 'resultados': data})


@principal.route("/expedientes/generar", methods=["POST"])
@login_requerido
def generar_expediente():
    import openpyxl, io
    from flask import send_file

    id_expediente = request.json.get('id_expediente')
    tipo          = request.json.get('tipo')

    if not id_expediente or not tipo:
        return jsonify({'ok': False, 'mensaje': 'Datos requeridos'}), 400

    cur = mysql.connection.cursor()

    # Consulta según tipo
    if tipo == 'jugador':
        cur.execute("""
            SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                   j.id_jugador, j.apellido_paterno, j.apellido_materno,
                   j.nombres, j.curp, j.fecha_nacimiento, j.numero_registro,
                   j.categoria, j.tipo_sangre, j.peso, j.estatura,
                   j.club, j.ligas_participa, j.enfermedades_cronicas,
                   j.medicamentos, j.ocupacion, j.escolaridad,
                   d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                   eq.nombre_equipo, l.nombre_liga
            FROM expediente e
            JOIN jugador j    ON j.id_jugador    = e.id_jugador
            LEFT JOIN direccion d  ON d.id_jugador = j.id_jugador
            LEFT JOIN equipo eq   ON eq.id_equipo  = j.id_equipo
            LEFT JOIN liga l      ON l.id_liga     = eq.id_liga
            WHERE e.id_expediente = %s
        """, (id_expediente,))

    elif tipo == 'entrenador':
        cur.execute("""
            SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                   en.id_entrenador, en.apellido_paterno, en.apellido_materno,
                   en.nombres, en.curp, en.fecha_nacimiento, en.numero_registro,
                   en.categoria, en.tipo_sangre, en.peso, en.estatura,
                   en.club, en.ligas_participa, en.cedula, en.especialidad,
                   d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                   eq.nombre_equipo, l.nombre_liga
            FROM expediente e
            JOIN entrenador en ON en.id_entrenador = e.id_entrenador
            LEFT JOIN direccion d  ON d.id_entrenador = en.id_entrenador
            LEFT JOIN equipo eq   ON eq.id_equipo     = en.id_equipo
            LEFT JOIN liga l      ON l.id_liga        = eq.id_liga
            WHERE e.id_expediente = %s
        """, (id_expediente,))

    elif tipo == 'arbitro':
        cur.execute("""
            SELECT e.id_expediente, e.estatus, e.fecha_creacion,
                   a.id_arbitro, a.apellido_paterno, a.apellido_materno,
                   a.nombres, a.curp, a.fecha_nacimiento, a.numero_registro,
                   a.categoria, a.tipo_sangre, a.peso, a.estatura,
                   a.club, a.ligas_participa, a.licencia, a.zona,
                   d.calle, d.numero_exterior, d.colonia, d.codigo_postal,
                   eq.nombre_equipo, l.nombre_liga
            FROM expediente e
            JOIN arbitro a    ON a.id_arbitro    = e.id_arbitro
            LEFT JOIN direccion d  ON d.id_arbitro = a.id_arbitro
            LEFT JOIN equipo eq   ON eq.id_equipo  = a.id_equipo
            LEFT JOIN liga l      ON l.id_liga     = eq.id_liga
            WHERE e.id_expediente = %s
        """, (id_expediente,))

    fila = cur.fetchone()
    cur.close()

    if not fila:
        return jsonify({'ok': False, 'mensaje': 'Sin datos'}), 404

    # ── Generar Excel ─────────────────────────────
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Expediente"

    tipo_label = {'jugador': 'Jugador', 'entrenador': 'Entrenador', 'arbitro': 'Árbitro'}

    ws.append(["EXPEDIENTE SIRED"])
    ws.append([])
    ws.append(["ID Expediente",  fila['id_expediente']])
    ws.append(["Tipo",           tipo_label.get(tipo, tipo)])
    ws.append(["Estatus",        fila['estatus']])
    ws.append(["Fecha Creación", str(fila['fecha_creacion'])])
    ws.append([])
    ws.append(["DATOS PERSONALES"])
    ws.append(["Apellido Paterno", fila['apellido_paterno']])
    ws.append(["Apellido Materno", fila['apellido_materno']])
    ws.append(["Nombres",          fila['nombres']])
    ws.append(["CURP",             fila['curp']])
    ws.append(["Fecha Nacimiento", str(fila['fecha_nacimiento'])])
    ws.append(["Tipo Sangre",      fila['tipo_sangre']])
    ws.append(["Peso",             fila['peso']])
    ws.append(["Estatura",         fila['estatura']])
    ws.append(["No. Registro",     fila['numero_registro']])
    ws.append(["Categoría",        fila['categoria']])
    ws.append([])
    ws.append(["DOMICILIO"])
    ws.append(["Calle",        fila['calle']])
    ws.append(["Num. Exterior",fila['numero_exterior']])
    ws.append(["Colonia",      fila['colonia']])
    ws.append(["C.P.",         fila['codigo_postal']])
    ws.append([])
    ws.append(["INFORMACIÓN DEPORTIVA"])
    ws.append(["Club",          fila['club']])
    ws.append(["Equipo",        fila['nombre_equipo']])
    ws.append(["Liga",          fila['nombre_liga']])
    ws.append(["Ligas Participa", fila['ligas_participa']])

    # Campos específicos por tipo
    if tipo == 'entrenador':
        ws.append(["Cédula",      fila['cedula']])
        ws.append(["Especialidad",fila['especialidad']])
    elif tipo == 'arbitro':
        ws.append(["Licencia", fila['licencia']])
        ws.append(["Zona",     fila['zona']])

    ws.append([])
    ws.append(["SALUD"])
    ws.append(["Enfermedades Crónicas", fila['enfermedades_cronicas']])
    ws.append(["Medicamentos",          fila['medicamentos']])

    # Estilo básico — encabezado en negritas
    from openpyxl.styles import Font
    for row in ws.iter_rows():
        for cell in row:
            if cell.value and isinstance(cell.value, str) and cell.column == 1:
                cell.font = Font(bold=True)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    from flask import send_file
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"expediente_{id_expediente}.xlsx"
    )

# ── Utilidad ──────────────────────────────────────
def _formatear_tamano(bytes):
    if not bytes:
        return '0 Bytes'
    for unidad in ['Bytes', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.1f} {unidad}"
        bytes /= 1024
    return f"{bytes:.1f} GB"