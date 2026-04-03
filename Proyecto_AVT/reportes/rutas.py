from flask import Blueprint, render_template

reportes = Blueprint('reportes', __name__, url_prefix="/reportes")

@reportes.route("/")
def reporteGeneral():
    return render_template("reportes/reporteGeneral.html")

@reportes.route("/sistema")
def reporteSistema():
    return render_template("reportes/reporteSistema.html")

@reportes.route("/ingresos")
def reporteIngresos():
    return render_template("reportes/reporteIngresos.html")

@reportes.route("/inscripcion")
def reporteInscripcion():
    return render_template("reportes/reporteInscripcion.html")