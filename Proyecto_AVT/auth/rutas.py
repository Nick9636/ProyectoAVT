# auth/rutas.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mail import Mail, Message
from extensiones import mysql, bcrypt, mail
import secrets
from datetime import datetime, timedelta

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
        session['id_usuario'] = usuario['id_usuario']
        session['nombre_usuario'] = usuario['nombre_usuario']
        session['nombre_completo'] = usuario['nombre_completo']
        session['rol'] = usuario['rol']
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
            cur.close()
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for("auth.iniciarSesion"))
        except Exception as e:
            flash("El nombre de usuario o email ya está registrado", "error")
            return redirect(url_for("auth.nuevoUsuario"))

    return render_template("auth/nuevoUsuario.html")
# ── RECORDAR CONTRASEÑA (VISTA PRINCIPAL) ─────────
@auth.route("/recordarContrasena", methods=["GET"])
def recordarContrasena():
    return render_template("auth/recordarContrasena.html")

# ── SOLICITAR CÓDIGO DE VERIFICACIÓN ──────────────
@auth.route("/solicitarCodigo", methods=["POST"])
def solicitarCodigo():
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': 'Email requerido'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario, email FROM usuario WHERE email = %s AND activo = 1", (email,))
        usuario = cur.fetchone()
        
        if not usuario:
            return jsonify({'success': True, 'message': 'Si el email existe, recibirás un código'})
        
        # Para desarrollo, usamos un código fijo
        if app.debug:
            token = "123456"  # Código fijo para pruebas
        else:
            token = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
        expiracion = datetime.now() + timedelta(minutes=15)
        
        cur.execute("""
            UPDATE usuario 
            SET reset_token = %s, reset_token_expira = %s 
            WHERE id_usuario = %s
        """, (token, expiracion, usuario['id_usuario']))
        mysql.connection.commit()
        cur.close()
        
        # En desarrollo, devolvemos el código en la respuesta
        return jsonify({
            'success': True, 
            'message': 'Código enviado',
            'debug_token': token if app.debug else None
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'}), 500

# ── VERIFICAR CÓDIGO ──────────────────────────────
@auth.route("/verificarCodigo", methods=["POST"])
def verificarCodigo():
    try:
        data = request.get_json()
        email = data.get('email')
        token = data.get('token')
        
        if not email or not token:
            return jsonify({'success': False, 'message': 'Email y código requeridos'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_usuario, reset_token_expira 
            FROM usuario 
            WHERE email = %s AND reset_token = %s AND activo = 1
        """, (email, token))
        
        usuario = cur.fetchone()
        cur.close()
        
        if not usuario:
            return jsonify({'success': False, 'message': 'Código inválido'}), 400
        
        if datetime.now() > usuario['reset_token_expira']:
            return jsonify({'success': False, 'message': 'El código ha expirado'}), 400
        
        return jsonify({'success': True, 'message': 'Código verificado correctamente'})
        
    except Exception as e:
        print(f"Error al verificar código: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'}), 500

# ── CAMBIAR CONTRASEÑA ────────────────────────────
@auth.route("/cambiarPassword", methods=["POST"])
def cambiarPassword():
    try:
        data = request.get_json()
        email = data.get('email')
        token = data.get('token')
        nueva_password = data.get('password')
        
        if not all([email, token, nueva_password]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400
        
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id_usuario, reset_token_expira 
            FROM usuario 
            WHERE email = %s AND reset_token = %s AND activo = 1
        """, (email, token))
        
        usuario = cur.fetchone()
        
        if not usuario:
            cur.close()
            return jsonify({'success': False, 'message': 'Código inválido'}), 400
        
        if datetime.now() > usuario['reset_token_expira']:
            cur.close()
            return jsonify({'success': False, 'message': 'El código ha expirado'}), 400
        
        # Hash de la nueva contraseña
        hashed = bcrypt.generate_password_hash(nueva_password).decode('utf-8')
        
        # Actualizar contraseña y limpiar token
        cur.execute("""
            UPDATE usuario 
            SET password = %s, reset_token = NULL, reset_token_expira = NULL 
            WHERE id_usuario = %s
        """, (hashed, usuario['id_usuario']))
        
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'success': True, 'message': 'Contraseña actualizada exitosamente'})
        
    except Exception as e:
        print(f"Error al cambiar contraseña: {e}")
        return jsonify({'success': False, 'message': 'Error en el servidor'}), 500

# ── CERRAR SESIÓN ─────────────────────────────────
@auth.route("/cerrarSesion")
def cerrarSesion():
    session.clear()
    return redirect(url_for("auth.iniciarSesion"))