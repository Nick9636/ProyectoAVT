from flask import Blueprint, render_template

registro = Blueprint('registro', __name__, url_prefix="/registro")

@registro.route("/")
def registroGeneral():
    return render_template("registro/registroGeneral.html")

@registro.route("/equipo")
def registroEquipo():
    return render_template("registro/registroEquipo.html")

@registro.route("/liga")
def registroLiga():
    return render_template("registro/registroLiga.html")

@registro.route("/pago")
def registroPago():
    return render_template("registro/registroPago.html")

@registro.route("/persona")
def registroPersona():
    return render_template("registro/registroPersona.html")

@registro.route("/afiliado")
def registroAfiliado():
    return render_template("registro/registroAfiliado.html")