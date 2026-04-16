from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from extensiones import mysql
import os
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


# ── Vistas ────────────────────────────────────────
@registro.route("/")
@login_requerido
def registroGeneral():
    return render_template("registro/registroGeneral.html")

##Liga
@registro.route("/liga")
@login_requerido
def registroLiga():
    # Traer todas las ligas existentes para mostrarlas
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_liga, nombre_liga, categoria FROM liga ORDER BY nombre_liga")
    ligas = cur.fetchall()
    cur.close()
    return render_template("registro/registroLiga.html", ligas=ligas)


@registro.route("/liga/guardar", methods=["POST"])
@login_requerido
def guardarLiga():
    nombre   = request.form.get('nombre_liga', '').strip().upper()
    categoria = request.form.get('categoria', '').strip().upper()

    if not nombre:
        return jsonify({'ok': False, 'mensaje': 'El nombre de la liga es obligatorio'}), 400

    cur = mysql.connection.cursor()
    try:
        # Verificar que no exista ya
        cur.execute("SELECT id_liga FROM liga WHERE nombre_liga = %s", (nombre,))
        if cur.fetchone():
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Ya existe una liga con ese nombre'}), 400

        cur.execute("""
            INSERT INTO liga (nombre_liga, categoria)
            VALUES (%s, %s)
        """, (nombre, categoria))
        mysql.connection.commit()
        nuevo_id = cur.lastrowid
        cur.close()

        return jsonify({
            'ok':      True,
            'mensaje': f'Liga "{nombre}" registrada correctamente.',
            'id':      nuevo_id,
            'nombre':  nombre,
            'categoria': categoria
        })

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
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500



# EQUIPO

@registro.route("/equipo")
@login_requerido
def registroEquipo():
    cur = mysql.connection.cursor()

    # Ligas para el select
    cur.execute("SELECT id_liga, nombre_liga, categoria FROM liga ORDER BY nombre_liga")
    ligas = cur.fetchall()

    # Equipos existentes con su liga
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria,
               l.nombre_liga, l.id_liga
        FROM equipo e
        JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.close()

    return render_template("registro/registroEquipo.html",
                           ligas=ligas, equipos=equipos)


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
        # Verificar duplicado en la misma liga
        cur.execute("""
            SELECT id_equipo FROM equipo
            WHERE nombre_equipo = %s AND id_liga = %s
        """, (nombre, id_liga))
        if cur.fetchone():
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Ya existe ese equipo en esta liga'}), 400

        cur.execute("""
            INSERT INTO equipo (id_liga, nombre_equipo, categoria)
            VALUES (%s, %s, %s)
        """, (id_liga, nombre, categoria))
        mysql.connection.commit()
        nuevo_id = cur.lastrowid

        # Traer nombre de liga para devolverlo al frontend
        cur.execute("SELECT nombre_liga FROM liga WHERE id_liga = %s", (id_liga,))
        liga = cur.fetchone()
        cur.close()

        return jsonify({
            'ok':           True,
            'mensaje':      f'Equipo "{nombre}" registrado correctamente.',
            'id':           nuevo_id,
            'nombre':       nombre,
            'categoria':    categoria,
            'nombre_liga':  liga['nombre_liga'] if liga else ''
        })

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
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500



# PAGO
@registro.route("/pago")
@login_requerido
def registroPago():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT p.id_pago, p.fecha_pago, p.estatus,
               p.metodo_pago, p.referencia, p.tipo_persona,
               COALESCE(
                   CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres),
                   CONCAT(e.apellido_paterno,' ',e.apellido_materno,' ',e.nombres),
                   CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres)
               ) AS nombre_persona
        FROM pago p
        LEFT JOIN jugador    j ON j.id_jugador    = p.id_jugador
        LEFT JOIN entrenador e ON e.id_entrenador = p.id_entrenador
        LEFT JOIN arbitro    a ON a.id_arbitro    = p.id_arbitro
        ORDER BY p.fecha_pago DESC
    """)
    pagos = cur.fetchall()
    cur.close()

    return render_template("registro/registroPago.html", pagos=pagos)


@registro.route("/pago/guardar", methods=["POST"])
@login_requerido
def guardarPago():
    id_persona   = request.form.get('id_persona')
    tipo_persona = request.form.get('tipo_persona')
    fecha_pago   = request.form.get('fecha_pago')
    estatus      = request.form.get('estatus', 'Pendiente')
    metodo_pago  = request.form.get('metodo_pago', '').strip()
    referencia   = request.form.get('referencia', '').strip()

    if not id_persona or not tipo_persona or not fecha_pago:
        return jsonify({'ok': False, 'mensaje': 'Datos incompletos'}), 400

    if tipo_persona not in ('jugador', 'entrenador', 'arbitro'):
        return jsonify({'ok': False, 'mensaje': 'Tipo de persona inválido'}), 400

    # Columna correcta según tipo
    col = {
        'jugador':    'id_jugador',
        'entrenador': 'id_entrenador',
        'arbitro':    'id_arbitro'
    }

    # Los otros dos van NULL
    id_jugador    = id_persona if tipo_persona == 'jugador'    else None
    id_entrenador = id_persona if tipo_persona == 'entrenador' else None
    id_arbitro    = id_persona if tipo_persona == 'arbitro'    else None

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO pago
                (id_jugador, id_entrenador, id_arbitro, tipo_persona,
                 fecha_pago, estatus, metodo_pago, referencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            id_jugador, id_entrenador, id_arbitro, tipo_persona,
            fecha_pago, estatus, metodo_pago, referencia
        ))
        mysql.connection.commit()
        nuevo_id = cur.lastrowid
        cur.close()

        return jsonify({
            'ok':      True,
            'mensaje': 'Pago registrado correctamente.',
            'id':      nuevo_id
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
        cur.execute("""
            UPDATE pago SET estatus = %s WHERE id_pago = %s
        """, (estatus, id_pago))
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500
    

#registro persona (jugador, entrenador, arbitro)
@registro.route("/persona")
@login_requerido
def registroPersona():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria, l.nombre_liga
        FROM equipo e
        JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.close()
    return render_template("registro/registroPersona.html", equipos=equipos)



# ── Guardar persona ───────────────────────────────
@registro.route("/persona/guardar", methods=["POST"])
@login_requerido
def guardarPersona():
    data = request.form
    tipo = data.get('tipo_persona')
    foto = request.files.get('fotoPersona')

    if tipo not in ('jugador', 'arbitro', 'entrenador'):
        return jsonify({'ok': False, 'mensaje': 'Tipo de persona inválido'}), 400

    vigencias = request.form.getlist('vigencia')
    vigencia  = ','.join(vigencias) if vigencias else ''

    ruta_foto = None
    if foto and foto.filename:
        nombre_foto  = secure_filename(foto.filename)
        carpeta_foto = os.path.join('static', 'uploads', 'fotos', tipo)
        os.makedirs(carpeta_foto, exist_ok=True)
        ruta_foto    = os.path.join(carpeta_foto, nombre_foto)
        foto.save(ruta_foto)

    cur = mysql.connection.cursor()

    try:
        # Insertar dirección
        cur.execute("""
            INSERT INTO direccion
                (id_municipio, calle, numero_exterior, colonia, codigo_postal)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data.get('municipio'),
            data.get('calle'),
            data.get('numero_exterior', ''),
            data.get('colonia'),
            data.get('codigo_postal')
        ))
        id_direccion = cur.lastrowid

        # Campos comunes a los tres tipos
        campos_comunes = (
            data.get('apellido_paterno', '').upper(),
            data.get('apellido_materno', '').upper(),
            data.get('nombres', '').upper(),
            data.get('numero_registro'),
            data.get('curp', '').upper(),
            vigencia,
            data.get('fecha_nacimiento'),
            data.get('lugar_nacimiento', '').upper(),
            data.get('nacionalidad', 'MEXICANA').upper(),
            data.get('peso'),
            data.get('estatura'),
            data.get('tipo_sangre'),
            data.get('ocupacion', '').upper(),
            data.get('escolaridad', '').upper(),
            data.get('escuela', '').upper(),
            data.get('enfermedades_cronicas', 'NINGUNA').upper(),
            data.get('medicamentos', 'NINGUNA').upper(),
            data.get('club', '').upper(),
            data.get('id_equipo') or None,
            data.get('categoria'),
            data.get('ligas_participa', '').upper(),
            ruta_foto,
            id_direccion
        )

        if tipo == 'jugador':
            cur.execute("""
                INSERT INTO jugador (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    enfermedades_cronicas, medicamentos,
                    club, id_equipo, categoria, ligas_participa,
                    fotografia, id_direccion,
                    telefono, celular, correo_electronico,
                    fecha_registro
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,NOW()
                )
            """, campos_comunes + (
                data.get('telefono'),
                data.get('celular'),
                data.get('email')
            ))

        elif tipo == 'entrenador':
            cur.execute("""
                INSERT INTO entrenador (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    enfermedades_cronicas, medicamentos,
                    club, id_equipo, categoria, ligas_participa,
                    fotografia, id_direccion,
                    cedula, especialidad,
                    fecha_registro
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,NOW()
                )
            """, campos_comunes + (
                data.get('cedula'),
                data.get('especialidad')
            ))

        elif tipo == 'arbitro':
            cur.execute("""
                INSERT INTO arbitro (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    enfermedades_cronicas, medicamentos,
                    club, id_equipo, categoria, ligas_participa,
                    fotografia, id_direccion,
                    licencia, zona,
                    fecha_registro
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,NOW()
                )
            """, campos_comunes + (
                data.get('licencia'),
                data.get('zona')
            ))

        id_persona = cur.lastrowid

        # Crear expediente automáticamente
        col_persona = {
            'jugador':    'id_jugador',
            'entrenador': 'id_entrenador',
            'arbitro':    'id_arbitro'
        }
        cur.execute(f"""
            INSERT INTO expediente
                ({col_persona[tipo]}, tipo_persona, estatus, fecha_creacion)
            VALUES (%s, %s, 'activo', NOW())
        """, (id_persona, tipo))

        # Tutor si aplica
        nombre_padre = data.get('nombre_padre', '').strip()
        if nombre_padre and tipo == 'jugador':
            cur.execute("""
                INSERT INTO tutor_padre
                    (id_jugador, nombre_completo, celular,
                     correo_electronico, curp_tutor)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_persona,
                nombre_padre.upper(),
                data.get('celular_padre'),
                data.get('email_padre'),
                data.get('curp_tutor', '').upper()
            ))

        email_solicitante = data.get('email', '')
        nombre_solicitante = f"{data.get('apellido_paterno','')} {data.get('nombres','')}".upper()

        cur.execute("""
            INSERT INTO autorizacion_pendiente
                (tipo_solicitud, id_referencia, fecha_solicitud,
                estatus, email_solicitante, nombre_solicitante)
            VALUES (%s, %s, NOW(), 'Pendiente', %s, %s)
        """, (tipo, id_persona, email_solicitante, nombre_solicitante))

        mysql.connection.commit()
        cur.close()

        return jsonify({
            'ok':      True,
            'mensaje': f'{tipo.capitalize()} registrado correctamente.',
            'id':      id_persona
        })

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500