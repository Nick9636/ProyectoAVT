from flask import Flask, render_template, request, session, redirect, url_for, flash
from config import Config
from extensiones import mysql, bcrypt
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

mysql.init_app(app)
bcrypt.init_app(app)

# IMPORTAR TODOS LOS BLUEPRINTS
from auth.rutas import auth
from consulta.rutas import consulta
from registro.rutas import registro
from reportes.rutas import reportes
from paginaInicio.rutas import principal

# REGISTRAR BLUEPRINTS
app.register_blueprint(auth)
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


# ── ACCESO EXTERNO ────────────────────────────────
@app.route("/accesoExterno", methods=["GET", "POST"])
def accesoExterno():
    if request.method == "POST":
        tipo = request.form["tipo"]
        session['tipo_externo'] = tipo
        session['esExterno'] = True
        return redirect(url_for("registroPersona"))

    return render_template("auth/accesoExterno.html")


# ── REGISTRO EXITOSO ──────────────────────────────
@app.route("/registroExitoso")
def registroExitoso():
    return render_template("auth/registroExitoso.html")


# ── AUTORIZAR REGISTRO (solo internos) ────────────
@app.route("/autorizarRegistro")
@solo_internos
def autorizarRegistro():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM registro_externo ORDER BY fecha_registro DESC")
    registros = cur.fetchall()
    cur.close()
    return render_template("autorizar/autorizarRegistro.html", registros=registros)


if __name__ == "__main__":
    app.run(debug=True)