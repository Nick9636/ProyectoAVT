# Adriana Nicole Guzman Ahuatzi
#01/04/2026
# Descripción: Rutas relacionadas con la autenticación de usuarios (inicio de sesión, registro, cierre de sesión).
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from extensiones import mysql, bcrypt, mail, notificar
import secrets
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

ALLOWED_TIPOS = ('Jugador', 'Arbitro', 'Entrenador')

# ── INICIO DE SESIÓN ──────────────────────────────
@auth.route("/")
@auth.route("/iniciarSesion", methods=["GET"])
def index():
    return render_template("auth/iniciarSesion.html")

@auth.route("/iniciarSesion", methods=["POST"])
def iniciarSesion():
    nombreUsuario = request.form["nombreUsuario"]
    password = request.form["password"]

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM usuario 
        WHERE nombre_usuario = %s AND activo = 1
    """, (nombreUsuario,))
    usuario = cur.fetchone()
    cur.close()

    if usuario and bcrypt.check_password_hash(usuario['password'], password):
        session['id_usuario'] = usuario['id_usuario']
        session['nombre_usuario'] = usuario['nombre_usuario']
        session['nombre_completo'] = usuario['nombre_completo']
        session['rol'] = usuario['rol']
        # Notificar inicio de sesión
        cur2 = mysql.connection.cursor()
        notificar(cur2, usuario['id_usuario'], f"Inicio de sesión desde el sistema.")
        mysql.connection.commit()
        cur2.close()
        return redirect(url_for("principal.paginaInicio"))
    else:
        flash("Usuario o contraseña incorrectos", "error")
        return redirect(url_for("auth.iniciarSesion"))

# ---USUARIO NUEVO --------
# ── NUEVO USUARIO ─────────────────────────────────
@auth.route("/nuevoUsuario", methods=["GET", "POST"])
def nuevoUsuario():
    if request.method == "POST":
        nombre_usuario = request.form["nombre_usuario"]
        nombre_completo = request.form["nombre_completo"]
        email = request.form["email"]
        password = request.form["password"]
        rol = request.form["rol"]

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO usuario (nombre_usuario, password, rol, nombre_completo, email, activo)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (nombre_usuario, hashed, rol, nombre_completo, email))
            mysql.connection.commit()
            nuevo_id = cur.lastrowid
            notificar(cur, nuevo_id, f"Bienvenido al sistema AVT. Tu cuenta fue creada con rol: {rol}.")
            mysql.connection.commit()
            cur.close()
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for("auth.iniciarSesion"))
        except Exception as e:
            flash("El nombre de usuario o email ya está registrado", "error")
            return redirect(url_for("auth.nuevoUsuario"))

    return render_template("auth/nuevoUsuario.html")


# ── CERRAR SESIÓN ─────────────────────────────────
@auth.route("/cerrarSesion")
def cerrarSesion():
    session.clear()
    return redirect(url_for("auth.iniciarSesion"))


# ── ACCESO EXTERNO ────────────────────────────────
@auth.route("/accesoExterno", methods=["GET"])
def accesoExterno():
    return render_template("auth/accesoExterno.html")


@auth.route("/accesoExterno", methods=["POST"])
def accesoExternoPost():
    nombre_completo = request.form.get('nombre_completo', '').strip()
    email           = request.form.get('email', '').strip()

    if not nombre_completo or not email:
        flash("Nombre y correo son obligatorios.", "error")
        return redirect(url_for("auth.accesoExterno"))

    # Guardar en sesión para pre-llenar el formulario
    session['ext_nombre'] = nombre_completo
    session['ext_email']  = email
    return redirect(url_for("auth.formularioExterno"))


@auth.route("/registroExterno", methods=["GET"])
def formularioExterno():
    # Si no vino por accesoExterno, regresar
    if 'ext_nombre' not in session:
        return redirect(url_for("auth.accesoExterno"))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria, l.nombre_liga
        FROM equipo e
        JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.close()

    return render_template(
        "registro/registroExterno.html",
        equipos=equipos,
        ext_nombre=session['ext_nombre'],
        ext_email=session['ext_email']
    )


@auth.route("/registroExterno/guardar", methods=["POST"])
def guardarRegistroExterno():
    if 'ext_nombre' not in session:
        return redirect(url_for("auth.accesoExterno"))

    data        = request.form
    tipo        = data.get('tipo_persona', '').strip()
    email       = session.get('ext_email', '')
    nombre_sol  = session.get('ext_nombre', '')

    if tipo not in ('jugador', 'arbitro', 'entrenador'):
        return jsonify({'ok': False, 'mensaje': 'Tipo de persona inválido'}), 400

    import os
    from werkzeug.utils import secure_filename

    foto     = request.files.get('fotoPersona')
    ruta_foto = None
    if foto and foto.filename:
        nombre_foto  = secure_filename(foto.filename)
        carpeta_foto = os.path.join('static', 'uploads', 'fotos', tipo)
        os.makedirs(carpeta_foto, exist_ok=True)
        ruta_foto    = os.path.join(carpeta_foto, nombre_foto)
        foto.save(ruta_foto)

    vigencias = request.form.getlist('vigencia')
    vigencia  = ','.join(vigencias) if vigencias else ''

    cur = mysql.connection.cursor()
    try:
        # 1. Insertar persona primero para obtener su ID
        campos_persona = (
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
            email,
            data.get('enfermedades_cronicas', 'NINGUNA').upper(),
            data.get('medicamentos', 'NINGUNA').upper(),
            ruta_foto,
        )

        # Solo jugador existe en la BD actual — entrenador/árbitro se insertan en jugador también
        # hasta que se ejecute la migración
        cur.execute("""
            INSERT INTO jugador (
                apellido_paterno, apellido_materno, nombres,
                curp, fecha_nacimiento, lugar_nacimiento, nacionalidad,
                peso, estatura, telefono, celular, correo_electronico,
                enfermedades_cronicas, medicamentos, fotografia
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, campos_persona)

        id_persona = cur.lastrowid

        # 2. Insertar dirección con el id_jugador ya disponible
        cur.execute("""
            INSERT INTO direccion
                (id_jugador, id_municipio, calle, numero_exterior, colonia, codigo_postal)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            id_persona,
            1,  # municipio genérico hasta migración (cat_municipio)
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

        # Tutor si aplica
        nombre_padre = data.get('nombre_padre', '').strip()
        if nombre_padre and tipo == 'jugador':
            cur.execute("""
                INSERT INTO tutor_padre
                    (id_jugador, nombre_completo, celular, correo_electronico, curp_tutor)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_persona,
                nombre_padre.upper(),
                data.get('celular_padre'),
                data.get('email_padre'),
                data.get('curp_tutor', '').upper()
            ))

        # Autorización pendiente
        cur.execute("""
            INSERT INTO autorizacion_pendiente
                (tipo_solicitud, id_referencia, fecha_solicitud, estatus)
            VALUES (%s, %s, NOW(), 'Pendiente')
        """, (tipo, id_persona))

        # Notificar a todos los administradores activos
        cur.execute("SELECT id_usuario FROM usuario WHERE activo = 1")
        admins = cur.fetchall()
        nombre_reg = f"{data.get('apellido_paterno','')} {data.get('nombres','')}".upper().strip()
        for admin in admins:
            notificar(cur, admin['id_usuario'],
                      f"Nueva solicitud de registro externo: {nombre_reg} ({tipo}). Pendiente de autorización.")

        mysql.connection.commit()
        cur.close()

        # Limpiar sesión externa
        session.pop('ext_nombre', None)
        session.pop('ext_email', None)

        return jsonify({'ok': True, 'mensaje': f'{tipo.capitalize()} registrado correctamente.'})

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


@auth.route("/registroExitoso")
def registroExitoso():
    return render_template("registro/registroExitoso.html")