# Autor: Adriana Nicole Guzman Ahuatzi
#23/03/2026
# Descripción: Inicialización de extensiones compartidas (MySQL, Bcrypt, Mail) y función
#              auxiliar para insertar notificaciones en la base de datos.
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from datetime import date

mysql = MySQL()
bcrypt = Bcrypt()
mail = Mail()


def notificar(cur, id_usuario, mensaje):
    """Inserta una notificación para el usuario dado usando el cursor activo."""
    cur.execute("""
        INSERT INTO notificacion (id_usuario, mensaje, fecha, leida)
        VALUES (%s, %s, NOW(), 0)
    """, (id_usuario, mensaje))


def anios_vigencia(cantidad=5):
    """Años disponibles para la vigencia: desde el año actual y los siguientes.
    Cuando pasa un año, el anterior deja de aparecer y se agrega uno nuevo."""
    anio_actual = date.today().year
    return list(range(anio_actual, anio_actual + cantidad))
