from flask import Flask

# IMPORTAR TODOS LOS BLUEPRINTS
from auth.rutas import auth
from consulta.rutas import consulta
from registro.rutas import registro
from reportes.rutas import reportes
from paginaInicio.rutas import principal

app = Flask(__name__)

# REGISTRAR BLUEPRINTS
app.register_blueprint(auth)
app.register_blueprint(consulta)
app.register_blueprint(registro)
app.register_blueprint(reportes)
app.register_blueprint(principal)

if __name__ == "__main__":
    app.run(debug=True)