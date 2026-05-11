# Autor: Adriana Nicole Guzman Ahuatzi
#23/03/2026
# Descripción: Configuración general de la aplicación: conexión a la base de datos MySQL,
#              clave secreta y parámetros del servidor de correo SMTP.
import os
class Config:
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'           # tu usuario
    MYSQL_PASSWORD = '12ingreso34'    # tu contraseña de Workbench
    MYSQL_DB = 'base_datos_amivd'  # nombre de la base de datos (base_mod.sql)
    MYSQL_CURSORCLASS = 'DictCursor'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'voleibol_avt_tlaxcala_2026'

    # Mail config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'avt@gmail.com'
    MAIL_PASSWORD = '1234'
    MAIL_DEFAULT_SENDER = 'avt@gmail.com'