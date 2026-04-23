# Autor: Adriana Nicole Guzman Ahuatzi
#23/03/2026
# Descripción: Punto de entrada principal de la aplicación Flask. Inicializa extensiones,
#              registra los blueprints de cada módulo y define el decorador de protección de rutas.
from flask import Flask, render_template, session, redirect, url_for
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
        if 'id_usuario' not in session:
            return redirect(url_for("auth.iniciarSesion"))
        return f(*args, **kwargs)
    return decorador

if __name__ == "__main__":
    app.run(debug=True)