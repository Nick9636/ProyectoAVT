from flask import Flask, render_template, request, session, redirect, url_for, flash
from config import Config
from extensiones import mysql, bcrypt, mail
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar extensiones
mysql.init_app(app)
bcrypt.init_app(app)
mail.init_app(app)

# IMPORTAR TODOS LOS BLUEPRINTS
from auth.rutas import auth
from autorizar.rutas import autorizar
from consulta.rutas import consulta
from registro.rutas import registro
from reportes.rutas import reportes
from paginaInicio.rutas import principal

# REGISTRAR BLUEPRINTS
app.register_blueprint(auth)
app.register_blueprint(autorizar)
app.register_blueprint(consulta)
app.register_blueprint(registro)
app.register_blueprint(reportes)
app.register_blueprint(principal)

# ── DECORADOR PROTECCIÓN ──────────────────────────
def solo_internos(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if session.get('esExterno'):
            return redirect(url_for("accesoExterno"))
        if 'id_usuario' not in session:
            return redirect(url_for("auth.iniciarSesion"))
        return f(*args, **kwargs)
    return decorador

# ── PANTALLA 1: datos básicos ──────────────────────
@app.route("/registro", methods=["GET", "POST"])
def accesoExterno():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]

        if not nombre or not email:
            flash("Por favor completa todos los campos", "error")
            return redirect(url_for("accesoExterno"))

        session['registro_nombre'] = nombre
        session['registro_email'] = email
        session['registro_activo'] = True
        session['esExterno'] = True
        return redirect(url_for("registroExterno"))

    return render_template("auth/accesoExterno.html")

# ── PANTALLA 2: formulario completo ───────────────
@app.route("/registro/formulario", methods=["GET", "POST"])
def registroExterno():
    if not session.get('registro_activo'):
        return redirect(url_for("accesoExterno"))

    nombre = session.get('registro_nombre')
    email = session.get('registro_email')

    if request.method == "POST":
        # Obtener datos del formulario
        nombre_form = request.form["nombre"]
        email_form = request.form["email"]

        # Validación básica
        if not nombre_form or not email_form:
            flash("Todos los campos son obligatorios", "error")
            return redirect(url_for("registroExterno"))

        try:
            # Guardar en base de datos (ajusta nombres según tu tabla)
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO usuario (nombre, correo, activo)
                VALUES (%s, %s, %s, 1)
            """, (nombre_form, email_form))
            mysql.connection.commit()
            cur.close()

            # Limpiar sesión externa
            session.pop('registro_activo', None)
            session.pop('registro_nombre', None)
            session.pop('registro_email', None)

            flash("Registro exitoso", "success")
            return redirect(url_for("registroExitoso"))

        except Exception as e:
            print("Error:", e)
            flash("Error al registrar usuario", "error")
            return redirect(url_for("registroExterno"))

    return render_template("auth/registroExterno.html", nombre=nombre, email=email)

# ── REGISTRO EXITOSO ──────────────────────────────
@app.route("/registroExitoso")
def registroExitoso():
    return render_template("auth/registroExitoso.html")

if __name__ == "__main__":
    app.run(debug=True)