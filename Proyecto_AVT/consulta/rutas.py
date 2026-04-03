from flask import Blueprint, render_template

consulta = Blueprint('consulta', __name__, url_prefix="/consulta")

@consulta.route("/")
def consultaGeneral():
    return render_template("consulta/consultaGeneral.html")

@consulta.route("/afiliado")
def consultarAfiliado():
    return render_template("consulta/consultarAfiliado.html")

@consulta.route("/ligas")
def consultarLigas():
    return render_template("consulta/consultarLigas.html")

@consulta.route("/pagos")
def consultarPagos():
    return render_template("consulta/consultarPagos.html")

@consulta.route("/registro")
def consultarRegistro():
    return render_template("consulta/consultarRegistro.html")

@consulta.route("/tutor")
def consultarTutor():
    return render_template("consulta/consultarTutor.html")