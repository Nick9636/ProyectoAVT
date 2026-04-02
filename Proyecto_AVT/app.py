from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("iniciarSesion.html")


#ESTA ES LA RUTA QUE TE FALTA
@app.route("/iniciarSesion", methods=["POST"])
def iniciarSesion():
    email = request.form["email"]
    password = request.form["password"]

    # Validación temporal
    if email == "admin@avt.com" and password == "1234":
        return redirect(url_for("paginaInicio"))

    return "Credenciales incorrectas"


@app.route("/paginaInicio")
def paginaInicio():
    return render_template("paginaInicio.html")


@app.route("/recordarContrasena", methods=["GET", "POST"])
def recordarContrasena():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Aquí después conectarás base de datos
        print("Correo:", email)
        print("Nueva contraseña:", password)

        return redirect(url_for("iniciarSesion"))

    return render_template("recordarContrasena.html")

@app.route("/nuevoUsuario")
def nuevoUsuario():
    return render_template("nuevoUsuario.html")


@app.route("/registro")
def registro():
    return render_template("registro.html")


@app.route("/consultar")
def consultar():
    return render_template("consultar.html")

@app.route("/reportes")
def reportes():
    return render_template("reportes.html")

@app.route("/reporteSistema")
def reporteSistema():
    return render_template("reporteSistema.html")

@app.route("/autorizarRegistro")
def autorizarRegistro():
    return render_template("autorizarRegistro.html")

@app.route("/consultarAfiliado")
def consultarAfiliado():
    return render_template("consultarAfiliado.html")

@app.route("/consultarLigas")
def consultarLigas():
    return render_template("consultarLigas.html")

@app.route("/consultarPagos")
def consultarPagos():
    return render_template("consultarPagos.html")

@app.route("/consultarRegistro")
def consultarRegistro():
    return render_template("consultarRegistro.html")

@app.route("/consultarTutor")
def consultarTutor():
    return render_template("consultarTutor.html")

@app.route("/digitalizar")
def digitalizar():
    return render_template("digitalizar.html")

@app.route("/expedientes")
def expedientes():
    return render_template("expedientes.html")

@app.route("/notificaciones")
def notificaciones():
    return render_template("notificaciones.html")

@app.route("/registroEquipo")
def registroEquipo():
    return render_template("registroEquipo.html")

@app.route("/registroLiga")
def registroLiga():
    return render_template("registroLiga.html")

@app.route("/registroPago")
def registroPago():
    return render_template("registroPago.html")

@app.route("/registroPersona")
def registroPersona():
    return render_template("registroPersona.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)