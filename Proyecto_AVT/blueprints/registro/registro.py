# Adriana Nicole Guzman Ahuatzi
#01/04/2026
# Rutas para el módulo de registro: ligas, equipos, personas (jugadores, entrenadores, árbitros) y pagos
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from extensiones import mysql, notificar, anios_vigencia
from datetime import date
import os
import uuid
from werkzeug.utils import secure_filename

registro = Blueprint('registro', __name__, url_prefix="/registro")


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.iniciarSesion'))
        return f(*args, **kwargs)
    return decorador


# ── Menú general ──────────────────────────────────
@registro.route("/")
@login_requerido
def registroGeneral():
    return render_template("registro/registroGeneral.html")


# ══════════════════════════════════════════════════
# LIGA
# ══════════════════════════════════════════════════

@registro.route("/liga")
@login_requerido
def registroLiga():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_liga, nombre_liga, categoria FROM liga ORDER BY nombre_liga")
    ligas = cur.fetchall()
    cur.close()
    return render_template("registro/registroLiga.html", ligas=ligas)


@registro.route("/liga/guardar", methods=["POST"])
@login_requerido
def guardarLiga():
    nombre    = request.form.get('nombre_liga', '').strip().upper()
    categoria = request.form.get('categoria', '').strip().upper()
    if not nombre:
        return jsonify({'ok': False, 'mensaje': 'El nombre de la liga es obligatorio'}), 400
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id_liga FROM liga WHERE nombre_liga = %s", (nombre,))
        if cur.fetchone():
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Ya existe una liga con ese nombre'}), 400
        cur.execute("INSERT INTO liga (nombre_liga, categoria) VALUES (%s, %s)", (nombre, categoria))
        mysql.connection.commit()
        nuevo_id = cur.lastrowid
        notificar(cur, session['id_usuario'], f"Liga '{nombre}' registrada.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True, 'mensaje': f'Liga "{nombre}" registrada correctamente.',
                        'id': nuevo_id, 'nombre': nombre, 'categoria': categoria})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


@registro.route("/liga/eliminar/<int:id_liga>", methods=["POST"])
@login_requerido
def eliminarLiga(id_liga):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM liga WHERE id_liga = %s", (id_liga,))
        mysql.connection.commit()
        notificar(cur, session['id_usuario'], f"Liga #{id_liga} eliminada.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# EQUIPO
# ══════════════════════════════════════════════════

@registro.route("/equipo")
@login_requerido
def registroEquipo():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_liga, nombre_liga, categoria FROM liga ORDER BY nombre_liga")
    ligas = cur.fetchall()
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria, l.nombre_liga, l.id_liga
        FROM equipo e JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.close()
    return render_template("registro/registroEquipo.html", ligas=ligas, equipos=equipos)


@registro.route("/equipo/guardar", methods=["POST"])
@login_requerido
def guardarEquipo():
    nombre    = request.form.get('nombre_equipo', '').strip().upper()
    id_liga   = request.form.get('id_liga')
    categoria = request.form.get('categoria', '').strip().upper()
    if not nombre or not id_liga:
        return jsonify({'ok': False, 'mensaje': 'Nombre y liga son obligatorios'}), 400
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT id_equipo FROM equipo WHERE nombre_equipo = %s AND id_liga = %s",
                    (nombre, id_liga))
        if cur.fetchone():
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Ya existe ese equipo en esta liga'}), 400
        cur.execute("INSERT INTO equipo (id_liga, nombre_equipo, categoria) VALUES (%s, %s, %s)",
                    (id_liga, nombre, categoria))
        mysql.connection.commit()
        nuevo_id = cur.lastrowid
        cur.execute("SELECT nombre_liga FROM liga WHERE id_liga = %s", (id_liga,))
        liga = cur.fetchone()
        notificar(cur, session['id_usuario'],
                  f"Equipo '{nombre}' registrado en liga '{liga['nombre_liga'] if liga else id_liga}'.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True, 'mensaje': f'Equipo "{nombre}" registrado correctamente.',
                        'id': nuevo_id, 'nombre': nombre, 'categoria': categoria,
                        'nombre_liga': liga['nombre_liga'] if liga else ''})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


@registro.route("/equipo/eliminar/<int:id_equipo>", methods=["POST"])
@login_requerido
def eliminarEquipo(id_equipo):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM equipo WHERE id_equipo = %s", (id_equipo,))
        mysql.connection.commit()
        notificar(cur, session['id_usuario'], f"Equipo #{id_equipo} eliminado.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# ASIGNAR JUGADOR A EQUIPO
# ══════════════════════════════════════════════════

@registro.route("/asignar")
@login_requerido
def registroAsignar():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id_jugador, curp,
               CONCAT_WS(' ', apellido_paterno, apellido_materno, nombres) AS nombre
        FROM jugador
        ORDER BY apellido_paterno, apellido_materno, nombres
    """)
    jugadores = cur.fetchall()
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria, l.nombre_liga
        FROM equipo e JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.execute("""
        SELECT j.id_jugador, e.id_equipo, e.nombre_equipo, l.nombre_liga,
               CONCAT_WS(' ', j.apellido_paterno, j.apellido_materno, j.nombres) AS nombre
        FROM jugador j
        JOIN equipo e ON e.id_equipo = j.id_equipo
        JOIN liga l   ON l.id_liga   = e.id_liga
        ORDER BY e.nombre_equipo, j.apellido_paterno
    """)
    asignados = cur.fetchall()
    cur.close()
    return render_template("registro/asignarJugador.html",
                           jugadores=jugadores, equipos=equipos, asignados=asignados)


@registro.route("/asignar/guardar", methods=["POST"])
@login_requerido
def guardarAsignacion():
    id_jugador = request.form.get('id_jugador')
    id_equipo  = request.form.get('id_equipo')
    if not id_jugador or not id_equipo:
        return jsonify({'ok': False, 'mensaje': 'Jugador y equipo son obligatorios'}), 400
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT CONCAT_WS(' ', apellido_paterno, apellido_materno, nombres) AS nombre
            FROM jugador WHERE id_jugador = %s
        """, (id_jugador,))
        jugador = cur.fetchone()
        if not jugador:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'El jugador no existe'}), 404

        cur.execute("SELECT nombre_equipo FROM equipo WHERE id_equipo = %s", (id_equipo,))
        equipo = cur.fetchone()
        if not equipo:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'El equipo no existe'}), 404

        cur.execute("UPDATE jugador SET id_equipo = %s WHERE id_jugador = %s",
                    (id_equipo, id_jugador))
        mysql.connection.commit()
        notificar(cur, session['id_usuario'],
                  f"Jugador '{jugador['nombre']}' asignado al equipo '{equipo['nombre_equipo']}'.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True,
                        'mensaje': f"{jugador['nombre']} fue asignado a {equipo['nombre_equipo']}."})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


@registro.route("/asignar/quitar/<int:id_jugador>", methods=["POST"])
@login_requerido
def quitarAsignacion(id_jugador):
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE jugador SET id_equipo = NULL WHERE id_jugador = %s", (id_jugador,))
        mysql.connection.commit()
        notificar(cur, session['id_usuario'], f"Jugador #{id_jugador} quitado de su equipo.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# PAGO
# ══════════════════════════════════════════════════

@registro.route("/pago")
@login_requerido
def registroPago():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT p.id_pago, p.folio_pago, p.fecha_pago, p.estatus,
               p.metodo_pago, p.referencia,
               'jugador' AS tipo_persona,
               CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) AS nombre_persona
        FROM pago p
        JOIN afiliacion a ON a.id_afiliacion = p.id_afiliacion
        JOIN jugador    j ON j.id_jugador    = a.id_jugador
        ORDER BY p.fecha_pago DESC
    """)
    pagos = cur.fetchall()
    cur.close()
    return render_template("registro/registroPago.html", pagos=pagos)


@registro.route("/pago/guardar", methods=["POST"])
@login_requerido
def guardarPago():
    id_jugador  = request.form.get('id_persona') or request.form.get('id_jugador')
    fecha_pago  = request.form.get('fecha_pago')
    estatus     = request.form.get('estatus', 'Pendiente')
    metodo_pago = request.form.get('metodo_pago', '').strip()
    referencia  = request.form.get('referencia', '').strip()
    if not id_jugador or not fecha_pago:
        return jsonify({'ok': False, 'mensaje': 'Jugador y fecha son obligatorios'}), 400
    if not metodo_pago:
        return jsonify({'ok': False, 'mensaje': 'El método de pago es obligatorio'}), 400
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT id_afiliacion FROM afiliacion
            WHERE id_jugador = %s ORDER BY fecha_afiliacion DESC LIMIT 1
        """, (id_jugador,))
        afil = cur.fetchone()
        if not afil:
            cur.execute("""
                INSERT INTO afiliacion
                    (id_jugador, id_club, id_vigencia, numero_registro,
                     ano_vigencia, fecha_afiliacion, fecha_vencimiento, estatus)
                VALUES (%s, 1, 1, %s, YEAR(NOW()), NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 'Activa')
            """, (id_jugador, f'REG-{id_jugador}-{fecha_pago}'))
            id_afiliacion = cur.lastrowid
        else:
            id_afiliacion = afil['id_afiliacion']

        # ── NUEVO: Verificar si ya existe un pago para esta afiliación y fecha ──
        cur.execute("""
            SELECT id_pago, folio_pago FROM pago
            WHERE id_afiliacion = %s AND fecha_pago = %s
        """, (id_afiliacion, fecha_pago))
        pago_existente = cur.fetchone()

        if pago_existente:
            # Actualizar el pago existente (no generar duplicado)
            nuevo_id = pago_existente['id_pago']
            folio_pago = pago_existente.get('folio_pago') or f"PAG-{nuevo_id:06d}"
            cur.execute("""
                UPDATE pago
                SET estatus = %s, metodo_pago = %s, referencia = %s,
                    folio_pago = %s
                WHERE id_pago = %s
            """, (
                estatus, metodo_pago or None, referencia or None,
                folio_pago, nuevo_id
            ))
            mensaje = 'Pago actualizado correctamente.'
        else:
            # Insertar nuevo pago
            cur.execute("""
                INSERT INTO pago (id_afiliacion, fecha_pago, estatus, metodo_pago, referencia)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_afiliacion, fecha_pago, estatus, metodo_pago or None, referencia or None))
            nuevo_id = cur.lastrowid
            folio_pago = f"PAG-{nuevo_id:06d}"
            cur.execute(
                "UPDATE pago SET folio_pago = %s WHERE id_pago = %s",
                (folio_pago, nuevo_id)
            )
            mensaje = 'Pago registrado correctamente.'

        notificar(cur, session['id_usuario'],
                  f"Pago #{nuevo_id} registrado para jugador #{id_jugador} — estatus: {estatus}.")
        mysql.connection.commit()
        cur.close()
        return jsonify({
            'ok': True, 'mensaje': mensaje, 'id': nuevo_id, 'folio': folio_pago
        })
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


@registro.route("/pago/actualizar/<int:id_pago>", methods=["POST"])
@login_requerido
def actualizarPago(id_pago):
    estatus = request.form.get('estatus')
    if estatus not in ('Pendiente', 'Completado', 'Cancelado'):
        return jsonify({'ok': False, 'mensaje': 'Estatus inválido'}), 400
    cur = mysql.connection.cursor()
    try:
        cur.execute("UPDATE pago SET estatus = %s WHERE id_pago = %s", (estatus, id_pago))
        mysql.connection.commit()
        notificar(cur, session['id_usuario'], f"Pago #{id_pago} actualizado a '{estatus}'.")
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# PERSONA (jugador / entrenador / árbitro)
# ══════════════════════════════════════════════════

@registro.route("/persona")
@login_requerido
def registroPersona():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria, l.nombre_liga
        FROM equipo e JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.execute("SELECT id_municipio, nombre FROM cat_municipio ORDER BY nombre")
    municipios = cur.fetchall()
    cur.execute("SELECT id_liga, nombre_liga FROM liga ORDER BY nombre_liga")
    ligas = cur.fetchall()

    sig_jugador = generar_numero_registro(cur, 'jugador')

    sig_entrenador = generar_numero_registro(cur, 'entrenador')
    sig_arbitro = generar_numero_registro(cur, 'arbitro')

    cur.close()
    return render_template(
        "registro/registroPersona.html",
        equipos=equipos,
        municipios=municipios,
        ligas=ligas,
        anios_vigencia=anios_vigencia(),
        sig_jugador=sig_jugador,
        sig_entrenador=sig_entrenador,
        sig_arbitro=sig_arbitro,
    )


@registro.route("/persona/siguiente_registro")
@login_requerido
def siguienteRegistro():
    tipo = request.args.get('tipo', '').strip()
    cur = mysql.connection.cursor()
    try:
        if tipo not in ('jugador', 'entrenador', 'arbitro'):
            cur.close()
            return jsonify({'ok': False}), 400
        numero = generar_numero_registro(cur, tipo)
        cur.close()
        return jsonify({'ok': True, 'numero': numero})
    except Exception as e:
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


def generar_numero_registro(cur, tipo):
    """
    Genera el siguiente número de registro para jugador, arbitro o entrenador.
    Usa MAX sobre el campo numero_registro para evitar colisiones aunque haya
    huecos o inserciones fallidas previas.
    """
    if tipo == 'jugador':
        tabla, prefijo = 'jugador', 'JUG'
    elif tipo == 'entrenador':
        tabla, prefijo = 'entrenador', 'ENT'
    elif tipo == 'arbitro':
        tabla, prefijo = 'arbitro', 'ARB'
    else:
        raise ValueError(f"Tipo inválido: {tipo}")
 
    cur.execute(
        f"SELECT MAX(CAST(SUBSTRING(numero_registro, 5) AS UNSIGNED)) AS ultimo "
        f"FROM {tabla} WHERE numero_registro LIKE %s",
        (f"{prefijo}-%",)
    )
    row    = cur.fetchone()
    ultimo = row['ultimo'] if row and row['ultimo'] else 0
    return f"{prefijo}-{ultimo + 1:03d}"
 

@registro.route("/persona/guardar", methods=["POST"])
@login_requerido
def guardarPersona():
    data = request.form
    tipo = data.get('tipo_persona', '').strip()
    foto = request.files.get('fotoPersona')
    liga_ids_enviados = request.form.getlist('ligas_participa')

    if tipo not in ('jugador', 'arbitro', 'entrenador'):
        return jsonify({'ok': False, 'mensaje': 'Tipo de persona inválido'}), 400

    # Firma obligatoria (se valida antes de guardar la foto)
    firma_b64 = data.get('firma_base64', '').strip()
    if not firma_b64.startswith('data:image/png;base64,'):
        return jsonify({'ok': False, 'mensaje': 'La firma es obligatoria'}), 400

    if not liga_ids_enviados:
        return jsonify({'ok': False, 'mensaje': 'Selecciona al menos una liga'}), 400
    try:
        liga_ids = list(dict.fromkeys(int(id_liga) for id_liga in liga_ids_enviados))
    except ValueError:
        return jsonify({'ok': False, 'mensaje': 'La selección de ligas no es válida'}), 400
    if any(id_liga <= 0 for id_liga in liga_ids):
        return jsonify({'ok': False, 'mensaje': 'La selección de ligas no es válida'}), 400

    fecha_nacimiento = data.get('fecha_nacimiento', '').strip()
    requiere_tutor = False
    nombre_padre = data.get('nombre_padre', '').strip()
    ine_tutor = request.files.get('ineTutor')
    if tipo == 'jugador':
        try:
            nacimiento = date.fromisoformat(fecha_nacimiento)
        except ValueError:
            return jsonify({'ok': False, 'mensaje': 'La fecha de nacimiento no es válida'}), 400

        hoy = date.today()
        edad = hoy.year - nacimiento.year - (
            (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day)
        )
        requiere_tutor = edad < 18
        if requiere_tutor and not nombre_padre:
            return jsonify({'ok': False, 'mensaje': 'El nombre del padre o tutor es obligatorio'}), 400
        if requiere_tutor and (not ine_tutor or not ine_tutor.filename):
            return jsonify({'ok': False, 'mensaje': 'La INE del padre o tutor es obligatoria'}), 400

    ruta_ine_tutor = None
    if requiere_tutor:
        extension_ine = os.path.splitext(secure_filename(ine_tutor.filename))[1].lower()
        if extension_ine not in ('.png', '.jpg', '.jpeg', '.pdf'):
            return jsonify({
                'ok': False,
                'mensaje': 'La INE debe ser un archivo PNG, JPG o PDF'
            }), 400

        carpeta_ine = os.path.join('static', 'uploads', 'ine_tutor')
        nombre_ine = f"ine_tutor_{uuid.uuid4().hex}{extension_ine}"
        ruta_ine_tutor = os.path.join(carpeta_ine, nombre_ine).replace(os.sep, '/')

    vigencia = ','.join(request.form.getlist('vigencia'))

    ruta_foto = None
    if foto and foto.filename:
        nombre_foto  = secure_filename(foto.filename)
        carpeta_foto = os.path.join('static', 'uploads', 'fotos', tipo)
        ruta_foto    = os.path.join(carpeta_foto, nombre_foto)

    firma_base64_guardar = firma_b64

    cur = mysql.connection.cursor()
    try:
        placeholders = ','.join(['%s'] * len(liga_ids))
        cur.execute(
            f"SELECT id_liga, nombre_liga FROM liga WHERE id_liga IN ({placeholders})",
            tuple(liga_ids)
        )
        ligas_seleccionadas = {
            int(liga['id_liga']): liga['nombre_liga'] for liga in cur.fetchall()
        }
        if set(ligas_seleccionadas) != set(liga_ids):
            cur.close()
            return jsonify({
                'ok': False,
                'mensaje': 'Una o más ligas seleccionadas ya no están registradas'
            }), 400
        ligas_participa = ', '.join(
            ligas_seleccionadas[id_liga] for id_liga in liga_ids
        )
        if len(ligas_participa) > 255:
            cur.close()
            return jsonify({
                'ok': False,
                'mensaje': 'La selección de ligas excede el límite permitido'
            }), 400

        if ruta_ine_tutor:
            os.makedirs(carpeta_ine, exist_ok=True)
            ine_tutor.save(ruta_ine_tutor)
        if ruta_foto:
            os.makedirs(carpeta_foto, exist_ok=True)
            foto.save(ruta_foto)

        numero_registro = generar_numero_registro(cur, tipo)

        nombre_municipio = data.get('municipio', '').strip().upper()
        id_municipio = 1
        if nombre_municipio:
            cur.execute("SELECT id_municipio FROM cat_municipio WHERE UPPER(nombre) = %s",
                        (nombre_municipio,))
            mun = cur.fetchone()
            if mun:
                id_municipio = mun['id_municipio']
            else:
                cur.execute("INSERT INTO cat_municipio (id_estado, nombre) VALUES (1, %s)",
                            (nombre_municipio,))
                id_municipio = cur.lastrowid

        id_equipo = data.get('id_equipo') or None

        apellido_paterno    = data.get('apellido_paterno', '').upper()
        apellido_materno    = data.get('apellido_materno', '').upper()
        nombres             = data.get('nombres', '').upper()
        curp                = data.get('curp', '').upper()
        fecha_nacimiento    = data.get('fecha_nacimiento')
        lugar_nacimiento    = data.get('lugar_nacimiento', '').upper() or None
        nacionalidad        = data.get('nacionalidad', 'MEXICANA').upper()
        peso                = data.get('peso') or None
        estatura            = data.get('estatura') or None
        tipo_sangre         = data.get('tipo_sangre') or None
        ocupacion           = data.get('ocupacion', '').upper() or None
        escolaridad         = data.get('escolaridad', '').upper() or None
        escuela             = data.get('escuela', '').upper() or None
        telefono            = data.get('telefono') or None
        celular             = data.get('celular') or None
        correo              = data.get('email') or data.get('correo_electronico') or None
        enfermedades        = data.get('enfermedades_cronicas', 'NINGUNA').upper() or 'NINGUNA'
        medicamentos        = data.get('medicamentos', 'NINGUNA').upper() or 'NINGUNA'
        club                = data.get('club', '').upper() or None
        categoria           = data.get('categoria') or None
        rama                = data.get('rama') or None
        ligas_participa     = ligas_participa or None

        if tipo == 'jugador':
            try:
                cur.execute("""
                    INSERT INTO jugador (
                        apellido_paterno, apellido_materno, nombres,
                        numero_registro, curp, vigencia,
                        fecha_nacimiento, lugar_nacimiento, nacionalidad,
                        peso, estatura, tipo_sangre,
                        ocupacion, escolaridad, escuela,
                        telefono, celular, correo_electronico,
                        enfermedades_cronicas, medicamentos,
                        club, categoria, rama, ligas_participa, fotografia, firma_base64
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia or None,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    telefono, celular, correo,
                    enfermedades, medicamentos,
                    club, categoria, rama, ligas_participa, ruta_foto, firma_base64_guardar,
                ))
            except Exception:
                mysql.connection.rollback()
                cur.execute("""
                    INSERT INTO jugador (
                        apellido_paterno, apellido_materno, nombres,
                        curp, fecha_nacimiento, lugar_nacimiento, nacionalidad,
                        peso, estatura,
                        ocupacion, escolaridad, escuela,
                        telefono, celular, correo_electronico,
                        medicamentos, fotografia, firma_base64
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (
                    apellido_paterno, apellido_materno, nombres,
                    curp, fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura,
                    ocupacion, escolaridad, escuela,
                    telefono, celular, correo,
                    medicamentos, ruta_foto, firma_base64_guardar,
                ))

            id_persona = cur.lastrowid

            try:
                cur.execute("""
                    INSERT INTO direccion
                        (id_jugador, id_municipio, nombre_municipio,
                         calle, numero_exterior, colonia, codigo_postal)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_persona, id_municipio, nombre_municipio,
                    data.get('calle', '').upper(),
                    data.get('numero_exterior', '') or None,
                    data.get('colonia', '').upper(),
                    data.get('codigo_postal', '')
                ))
            except Exception:
                cur.execute("""
                    INSERT INTO direccion
                        (id_jugador, id_municipio,
                         calle, numero_exterior, colonia, codigo_postal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_persona, id_municipio,
                    data.get('calle', '').upper(),
                    data.get('numero_exterior', '') or None,
                    data.get('colonia', '').upper(),
                    data.get('codigo_postal', '')
                ))

            cur.execute("""
                INSERT INTO expediente (id_jugador, estatus, fecha_creacion)
                VALUES (%s, 'activo', NOW())
            """, (id_persona,))

            if nombre_padre:
                cur.execute("""
                    INSERT INTO tutor_padre
                        (id_jugador, nombre_completo, celular, correo_electronico,
                         curp_tutor, fotografia_ine)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    id_persona,
                    nombre_padre.upper(),
                    data.get('celular_padre') or None,
                    data.get('email_padre') or None,
                    data.get('curp_tutor', '').upper() or None,
                    ruta_ine_tutor
                ))

        elif tipo == 'entrenador':
            cur.execute("""
                INSERT INTO entrenador (
                    id_equipo,
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    telefono, celular, correo_electronico,
                    enfermedades_cronicas, medicamentos,
                    club, categoria, rama, ligas_participa, fotografia,
                    cedula, especialidad, firma_base64
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                id_equipo,
                apellido_paterno, apellido_materno, nombres,
                numero_registro, curp, vigencia or None,
                fecha_nacimiento, lugar_nacimiento, nacionalidad,
                peso, estatura, tipo_sangre,
                ocupacion, escolaridad, escuela,
                telefono, celular, correo,
                enfermedades, medicamentos,
                club, categoria, rama, ligas_participa, ruta_foto,
                data.get('cedula') or None,
                data.get('especialidad') or None, firma_base64_guardar,
            ))
            id_persona = cur.lastrowid

        elif tipo == 'arbitro':
            cur.execute("""
                INSERT INTO arbitro (
                    id_equipo,
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    telefono, celular, correo_electronico,
                    enfermedades_cronicas, medicamentos,
                    club, categoria, rama, ligas_participa, fotografia,
                    zona, licencia, firma_base64
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                id_equipo,
                apellido_paterno, apellido_materno, nombres,
                numero_registro, curp, vigencia or None,
                fecha_nacimiento, lugar_nacimiento, nacionalidad,
                peso, estatura, tipo_sangre,
                ocupacion, escolaridad, escuela,
                telefono, celular, correo,
                enfermedades, medicamentos,
                club, categoria, rama, ligas_participa, ruta_foto,
                data.get('zona') or None,
                data.get('licencia') or None,
                firma_base64_guardar,
            ))
            id_persona = cur.lastrowid

        cur.execute("""
            INSERT INTO autorizacion_pendiente
                (tipo_solicitud, id_referencia, fecha_solicitud, estatus)
            VALUES (%s, %s, NOW(), 'Pendiente')
        """, (tipo, id_persona))

        nombre_completo = f"{apellido_paterno} {nombres}".strip()
        notificar(cur, session['id_usuario'],
                  f"Nuevo registro de {tipo}: {nombre_completo} ({numero_registro}). "
                  f"Solicitud de autorización creada.")

        mysql.connection.commit()
        cur.close()
        return jsonify({
            'ok':              True,
            'mensaje':         f'{tipo.capitalize()} registrado correctamente.',
            'id':              id_persona,
            'numero_registro': numero_registro,
        })

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500