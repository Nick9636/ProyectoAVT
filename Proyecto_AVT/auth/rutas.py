from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from extensiones import mysql, bcrypt

auth = Blueprint('auth', __name__)


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
        session['id_usuario']       = usuario['id_usuario']
        session['nombre_usuario']   = usuario['nombre_usuario']
        session['nombre_completo']  = usuario['nombre_completo']
        session['rol']              = usuario['rol']
        return redirect(url_for("principal.paginaInicio"))
    else:
        flash("Usuario o contraseña incorrectos", "error")
        return redirect(url_for("auth.iniciarSesion"))


# ── NUEVO USUARIO ─────────────────────────────────
@auth.route("/nuevoUsuario", methods=["GET", "POST"])
def nuevoUsuario():
    if request.method == "POST":
        nombre_usuario   = request.form["nombre_usuario"]
        nombre_completo  = request.form["nombre_completo"]
        email            = request.form["email"]
        password         = request.form["password"]
        rol              = request.form["rol"]  # 'Presidente' o 'Secretaria'

        hashed = bcrypt.generate_password_hash(password).decode('utf-8')

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO usuario (nombre_usuario, password, rol, nombre_completo, email, activo)
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (nombre_usuario, hashed, rol, nombre_completo, email))
            mysql.connection.commit()
            cur.close()
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for("auth.iniciarSesion"))
        except Exception:
            flash("El nombre de usuario o email ya está registrado", "error")
            return redirect(url_for("auth.nuevoUsuario"))

    return render_template("auth/nuevoUsuario.html")


# ── RECORDAR CONTRASEÑA ───────────────────────────
@auth.route("/recordarContrasena", methods=["GET", "POST"])
def recordarContrasena():
    if request.method == "POST":
        email            = request.form["email"]
        nueva_password   = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s AND activo = 1", (email,))
        usuario = cur.fetchone()

        if usuario:
            hashed = bcrypt.generate_password_hash(nueva_password).decode('utf-8')
            cur.execute("""
                UPDATE usuario SET password = %s WHERE email = %s
            """, (hashed, email))
            mysql.connection.commit()
            flash("Contraseña actualizada correctamente", "success")
        else:
            flash("No existe una cuenta activa con ese correo", "error")

        cur.close()
        return redirect(url_for("auth.iniciarSesion"))

    return render_template("auth/recordarContrasena.html")


# ── CERRAR SESIÓN ─────────────────────────────────
@auth.route("/cerrarSesion")
def cerrarSesion():
    session.clear()
    return redirect(url_for("auth.iniciarSesion"))