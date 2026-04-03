from flask import Blueprint, render_template, request, redirect, url_for

auth = Blueprint('auth', __name__, url_prefix="/auth")

@auth.route("/", methods=["GET"])
def index():
    return render_template("auth/iniciarSesion.html")

@auth.route("/iniciarSesion", methods=["GET", "POST"])
def iniciarSesion():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email == "admin@avt.com" and password == "1234":
            return redirect(url_for("principal.paginaInicio"))

        return "Credenciales incorrectas"

    return render_template("auth/iniciarSesion.html")

@auth.route("/recordarContrasena", methods=["GET", "POST"])
def recordarContrasena():
    if request.method == "POST":
        return redirect(url_for("auth.iniciarSesion"))
    return render_template("auth/recordarContrasena.html")

@auth.route("/nuevoUsuario")
def nuevoUsuario():
    return render_template("auth/nuevoUsuario.html")