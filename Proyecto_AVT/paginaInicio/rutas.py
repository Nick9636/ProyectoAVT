from flask import Blueprint, render_template

principal = Blueprint('principal', __name__)

@principal.route("/")
def iniciarSesion():
    return render_template("auth/iniciarSesion.html")

@principal.route("/paginaInicio")
def paginaInicio():
    return render_template("paginaInicio/paginaInicio.html")

@principal.route("/autorizarRegistro")
def autorizarRegistro():
    return render_template("autorizar/autorizarRegistro.html")

@principal.route("/digitalizarDocumentos")
def digitalizar():
    return render_template("paginaInicio/digitalizarDocumentos.html")

@principal.route("/expedientes")
def expedientes():
    return render_template("paginaInicio/expedientes.html")

@principal.route("/notificaciones")
def notificaciones():
    return render_template("paginaInicio/notificaciones.html")