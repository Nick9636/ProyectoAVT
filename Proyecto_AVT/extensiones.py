# Autor: Adriana Nicole Guzman Ahuatzi
#23/03/2026
# Descripción: Inicialización de extensiones compartidas (MySQL, Bcrypt, Mail) y función
#              auxiliar para insertar notificaciones en la base de datos.
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_mail import Mail

mysql = MySQL()
bcrypt = Bcrypt()
mail = Mail()


def notificar(cur, id_usuario, mensaje):
    """Inserta una notificación para el usuario dado usando el cursor activo."""
    cur.execute("""
        INSERT INTO notificacion (id_usuario, mensaje, fecha, leida)
        VALUES (%s, %s, NOW(), 0)
    """, (id_usuario, mensaje))