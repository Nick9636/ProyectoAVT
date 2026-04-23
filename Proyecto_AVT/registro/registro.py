# Adriana Nicole Guzman Ahuatzi
#01/04/2026
# Rutas para el módulo de registro: ligas, equipos, personas (jugadores, entrenadores, árbitros) y pagos
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from extensiones import mysql, notificar
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
        notificar(cur, session['id_usuario'], f"Liga '{nombre}' registrada.")
        mysql.connection.commit()
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
        notificar(cur, session['id_usuario'], f"Liga #{id_liga} eliminada.")
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

        cur.execute("SELECT nombre_liga FROM liga WHERE id_liga = %s", (id_liga,))
        liga = cur.fetchone()
        notificar(cur, session['id_usuario'],
                  f"Equipo '{nombre}' registrado en liga '{liga['nombre_liga'] if liga else id_liga}'.")
        mysql.connection.commit()
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
        notificar(cur, session['id_usuario'], f"Equipo #{id_equipo} eliminado.")
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
    id_jugador   = request.form.get('id_jugador')
    fecha_pago   = request.form.get('fecha_pago')
    estatus      = request.form.get('estatus', 'Pendiente')
    metodo_pago  = request.form.get('metodo_pago', '').strip()
    referencia   = request.form.get('referencia', '').strip()

    if not id_jugador or not fecha_pago:
        return jsonify({'ok': False, 'mensaje': 'Jugador y fecha son obligatorios'}), 400

    cur = mysql.connection.cursor()
    try:
        # Buscar o crear afiliación para este jugador
        cur.execute("""
            SELECT id_afiliacion FROM afiliacion
            WHERE id_jugador = %s
            ORDER BY fecha_afiliacion DESC LIMIT 1
        """, (id_jugador,))
        afil = cur.fetchone()

        if not afil:
            # Crear afiliación básica si no existe
            cur.execute("""
                INSERT INTO afiliacion
                    (id_jugador, id_club, id_vigencia, numero_registro,
                     ano_vigencia, fecha_afiliacion, fecha_vencimiento, estatus)
                VALUES (%s, 1, 1, %s, YEAR(NOW()), NOW(), DATE_ADD(NOW(), INTERVAL 1 YEAR), 'Activa')
            """, (id_jugador, f'REG-{id_jugador}-{fecha_pago}'))
            id_afiliacion = cur.lastrowid
        else:
            id_afiliacion = afil['id_afiliacion']

        cur.execute("""
            INSERT INTO pago (id_afiliacion, fecha_pago, estatus, metodo_pago, referencia)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_afiliacion, fecha_pago, estatus, metodo_pago or None, referencia or None))

        mysql.connection.commit()
        nuevo_id = cur.lastrowid
        notificar(cur, session['id_usuario'],
                  f"Pago registrado para jugador #{id_jugador} — estatus: {estatus}.")
        mysql.connection.commit()
        cur.close()

        return jsonify({'ok': True, 'mensaje': 'Pago registrado correctamente.', 'id': nuevo_id})

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
        # 1. Insertar jugador primero (única tabla que existe en la BD actual)
        cur.execute("""
            INSERT INTO jugador (
                apellido_paterno, apellido_materno, nombres,
                curp, fecha_nacimiento, lugar_nacimiento, nacionalidad,
                peso, estatura, telefono, celular, correo_electronico,
                enfermedades_cronicas, medicamentos, fotografia
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data.get('apellido_paterno', '').upper(),
            data.get('apellido_materno', '').upper(),
            data.get('nombres', '').upper(),
            data.get('curp', '').upper(),
            data.get('fecha_nacimiento'),
            data.get('lugar_nacimiento', '').upper(),
            data.get('nacionalidad', 'MEXICANA').upper(),
            data.get('peso') or None,
            data.get('estatura') or None,
            data.get('telefono') or None,
            data.get('celular') or None,
            data.get('correo_electronico') or data.get('email') or None,
            data.get('enfermedades_cronicas', 'NINGUNA').upper(),
            data.get('medicamentos', 'NINGUNA').upper(),
            ruta_foto,
        ))

        id_persona = cur.lastrowid

        # 2. Insertar dirección con id_jugador ya disponible
        cur.execute("""
            INSERT INTO direccion
                (id_jugador, id_municipio, calle, numero_exterior, colonia, codigo_postal)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_persona,
            1,  # municipio genérico hasta migración
            data.get('calle', '').upper(),
            data.get('numero_exterior', ''),
            data.get('colonia', '').upper(),
            data.get('codigo_postal', '')
        ))

        # 3. Expediente
        cur.execute("""
            INSERT INTO expediente (id_jugador, estatus, fecha_creacion)
            VALUES (%s, 'activo', NOW())
        """, (id_persona,))

        # 4. Tutor si aplica
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

        # 5. Autorización pendiente
        cur.execute("""
            INSERT INTO autorizacion_pendiente
                (tipo_solicitud, id_referencia, fecha_solicitud, estatus)
            VALUES (%s, %s, NOW(), 'Pendiente')
        """, (tipo, id_persona))

        nombre_completo = f"{data.get('apellido_paterno','')} {data.get('nombres','')}".upper().strip()
        notificar(cur, session['id_usuario'],
                  f"Nuevo registro de {tipo}: {nombre_completo}. Solicitud de autorización creada.")

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