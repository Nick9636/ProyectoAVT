from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from extensiones import mysql
import os
from werkzeug.utils import secure_filename

registro = Blueprint('registro', __name__, url_prefix="/registro")


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.iniciarSesion'))
        return f(*args, **kwargs)
    return decorador


# ── Vistas ────────────────────────────────────────
@registro.route("/")
@login_requerido
def registroGeneral():
    return render_template("registro/registroGeneral.html")


@registro.route("/equipo")
@login_requerido
def registroEquipo():
    return render_template("registro/registroEquipo.html")


@registro.route("/liga")
@login_requerido
def registroLiga():
    return render_template("registro/registroLiga.html")


@registro.route("/pago")
@login_requerido
def registroPago():
    return render_template("registro/registroPago.html")


@registro.route("/persona")
@login_requerido
def registroPersona():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT e.id_equipo, e.nombre_equipo, e.categoria, l.nombre_liga
        FROM equipo e
        JOIN liga l ON l.id_liga = e.id_liga
        ORDER BY e.nombre_equipo
    """)
    equipos = cur.fetchall()
    cur.close()
    return render_template("registro/registroPersona.html", equipos=equipos)


@registro.route("/afiliado")
@login_requerido
def registroAfiliado():
    return render_template("registro/registroAfiliado.html")


@registro.route("/autorizarRegistro")
@login_requerido
def autorizarRegistro():
    return render_template("autorizar/autorizarRegistro.html")


# ── Guardar persona ───────────────────────────────
@registro.route("/persona/guardar", methods=["POST"])
@login_requerido
def guardarPersona():
    data = request.form
    tipo = data.get('tipo_persona')
    foto = request.files.get('fotoPersona')

    if tipo not in ('jugador', 'arbitro', 'entrenador'):
        return jsonify({'ok': False, 'mensaje': 'Tipo de persona inválido'}), 400

    vigencias = request.form.getlist('vigencia')
    vigencia  = ','.join(vigencias) if vigencias else ''

    ruta_foto = None
    if foto and foto.filename:
        nombre_foto  = secure_filename(foto.filename)
        carpeta_foto = os.path.join('static', 'uploads', 'fotos', tipo)
        os.makedirs(carpeta_foto, exist_ok=True)
        ruta_foto    = os.path.join(carpeta_foto, nombre_foto)
        foto.save(ruta_foto)

    cur = mysql.connection.cursor()

    try:
        # Insertar dirección
        cur.execute("""
            INSERT INTO direccion
                (id_municipio, calle, numero_exterior, colonia, codigo_postal)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data.get('municipio'),
            data.get('calle'),
            data.get('numero_exterior', ''),
            data.get('colonia'),
            data.get('codigo_postal')
        ))
        id_direccion = cur.lastrowid

        # Campos comunes a los tres tipos
        campos_comunes = (
            data.get('apellido_paterno', '').upper(),
            data.get('apellido_materno', '').upper(),
            data.get('nombres', '').upper(),
            data.get('numero_registro'),
            data.get('curp', '').upper(),
            vigencia,
            data.get('fecha_nacimiento'),
            data.get('lugar_nacimiento', '').upper(),
            data.get('nacionalidad', 'MEXICANA').upper(),
            data.get('peso'),
            data.get('estatura'),
            data.get('tipo_sangre'),
            data.get('ocupacion', '').upper(),
            data.get('escolaridad', '').upper(),
            data.get('escuela', '').upper(),
            data.get('enfermedades_cronicas', 'NINGUNA').upper(),
            data.get('medicamentos', 'NINGUNA').upper(),
            data.get('club', '').upper(),
            data.get('id_equipo') or None,
            data.get('categoria'),
            data.get('ligas_participa', '').upper(),
            ruta_foto,
            id_direccion
        )

        if tipo == 'jugador':
            cur.execute("""
                INSERT INTO jugador (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    enfermedades_cronicas, medicamentos,
                    club, id_equipo, categoria, ligas_participa,
                    fotografia, id_direccion,
                    telefono, celular, correo_electronico,
                    fecha_registro
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,NOW()
                )
            """, campos_comunes + (
                data.get('telefono'),
                data.get('celular'),
                data.get('email')
            ))

        elif tipo == 'entrenador':
            cur.execute("""
                INSERT INTO entrenador (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    enfermedades_cronicas, medicamentos,
                    club, id_equipo, categoria, ligas_participa,
                    fotografia, id_direccion,
                    cedula, especialidad,
                    fecha_registro
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,NOW()
                )
            """, campos_comunes + (
                data.get('cedula'),
                data.get('especialidad')
            ))

        elif tipo == 'arbitro':
            cur.execute("""
                INSERT INTO arbitro (
                    apellido_paterno, apellido_materno, nombres,
                    numero_registro, curp, vigencia,
                    fecha_nacimiento, lugar_nacimiento, nacionalidad,
                    peso, estatura, tipo_sangre,
                    ocupacion, escolaridad, escuela,
                    enfermedades_cronicas, medicamentos,
                    club, id_equipo, categoria, ligas_participa,
                    fotografia, id_direccion,
                    licencia, zona,
                    fecha_registro
                ) VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                    %s,%s,NOW()
                )
            """, campos_comunes + (
                data.get('licencia'),
                data.get('zona')
            ))

        id_persona = cur.lastrowid

        # Crear expediente automáticamente
        col_persona = {
            'jugador':    'id_jugador',
            'entrenador': 'id_entrenador',
            'arbitro':    'id_arbitro'
        }
        cur.execute(f"""
            INSERT INTO expediente
                ({col_persona[tipo]}, tipo_persona, estatus, fecha_creacion)
            VALUES (%s, %s, 'activo', NOW())
        """, (id_persona, tipo))

        # Tutor si aplica
        nombre_padre = data.get('nombre_padre', '').strip()
        if nombre_padre and tipo == 'jugador':
            cur.execute("""
                INSERT INTO tutor_padre
                    (id_jugador, nombre_completo, celular,
                     correo_electronico, curp_tutor)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_persona,
                nombre_padre.upper(),
                data.get('celular_padre'),
                data.get('email_padre'),
                data.get('curp_tutor', '').upper()
            ))

        mysql.connection.commit()
        cur.close()

        return jsonify({
            'ok':      True,
            'mensaje': f'{tipo.capitalize()} registrado correctamente.',
            'id':      id_persona
        })

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500