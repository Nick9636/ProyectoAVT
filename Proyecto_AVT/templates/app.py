from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("login.html")


#ESTA ES LA RUTA QUE TE FALTA
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    # Validación temporal
    if email == "admin@avt.com" and password == "1234":
        return redirect(url_for("home"))

    return "Credenciales incorrectas"


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/recordar_contrasena", methods=["GET", "POST"])
def recordar_contraseña():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Aquí después conectarás base de datos
        print("Correo:", email)
        print("Nueva contraseña:", password)

        return redirect(url_for("login"))

    return render_template("recordar_contrasena.html")

@app.route("/nuevo_usuario")
def nuevo_usuario():
    return render_template("nuevo_usuario.html")


@app.route("/registro")
def registro():
    return render_template("registro.html")


@app.route("/consultar")
def consultar():
    return render_template("consultar.html")


if __name__ == "__main__":
    app.run(debug=True)