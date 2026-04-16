from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensiones import mysql, mail
from flask_mail import Message
from datetime import datetime

autorizar = Blueprint('autorizar', __name__ )


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.iniciarSesion'))
        return f(*args, **kwargs)
    return decorador


# ══════════════════════════════════════════════════
# VISTA PRINCIPAL
# ══════════════════════════════════════════════════

@autorizar.route("/")
@login_requerido
def autorizarRegistro():
    cur = mysql.connection.cursor()

    # Contadores para el resumen
    cur.execute("""
        SELECT
            SUM(estatus = 'Pendiente')   AS pendientes,
            SUM(estatus = 'Autorizado'
                AND DATE(fecha_solicitud) = CURDATE()) AS hoy,
            SUM(estatus = 'Rechazado')   AS rechazadas
        FROM autorizacion_pendiente
    """)
    contadores = cur.fetchone()

    # Solicitudes pendientes con datos de la persona
    cur.execute("""
        SELECT
            ap.id_autorizacion,
            ap.tipo_solicitud,
            ap.id_referencia,
            ap.fecha_solicitud,
            ap.estatus,
            ap.comentarios,
            ap.email_solicitante,
            ap.nombre_solicitante,
            CASE ap.tipo_solicitud
                WHEN 'jugador'     THEN CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres)
                WHEN 'entrenador'  THEN CONCAT(e.apellido_paterno,' ',e.apellido_materno,' ',e.nombres)
                WHEN 'arbitro'     THEN CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres)
                ELSE 'Trámite'
            END AS nombre_persona,
            CASE ap.tipo_solicitud
                WHEN 'jugador'    THEN j.curp
                WHEN 'entrenador' THEN e.curp
                WHEN 'arbitro'    THEN a.curp
                ELSE NULL
            END AS curp,
            CASE ap.tipo_solicitud
                WHEN 'jugador'    THEN j.categoria
                WHEN 'entrenador' THEN e.categoria
                WHEN 'arbitro'    THEN a.categoria
                ELSE NULL
            END AS categoria
        FROM autorizacion_pendiente ap
        LEFT JOIN jugador    j ON j.id_jugador    = ap.id_referencia AND ap.tipo_solicitud = 'jugador'
        LEFT JOIN entrenador e ON e.id_entrenador = ap.id_referencia AND ap.tipo_solicitud = 'entrenador'
        LEFT JOIN arbitro    a ON a.id_arbitro    = ap.id_referencia AND ap.tipo_solicitud = 'arbitro'
        ORDER BY
            FIELD(ap.estatus, 'Pendiente', 'Autorizado', 'Rechazado'),
            ap.fecha_solicitud DESC
    """)
    solicitudes = cur.fetchall()
    cur.close()

    return render_template(
        "autorizar/autorizarRegistro.html",
        solicitudes=solicitudes,
        contadores=contadores
    )


# ══════════════════════════════════════════════════
# AUTORIZAR
# ══════════════════════════════════════════════════

@autorizar.route("/aprobar/<int:id_autorizacion>", methods=["POST"])
@login_requerido
def aprobar(id_autorizacion):
    cur = mysql.connection.cursor()
    try:
        # Obtener datos de la solicitud
        cur.execute("""
            SELECT tipo_solicitud, id_referencia,
                   email_solicitante, nombre_solicitante
            FROM autorizacion_pendiente
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))
        sol = cur.fetchone()

        if not sol:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Solicitud no encontrada'}), 404

        # Actualizar estatus
        cur.execute("""
            UPDATE autorizacion_pendiente
            SET estatus = 'Autorizado',
                id_usuario_autorizador = %s
            WHERE id_autorizacion = %s
        """, (session['id_usuario'], id_autorizacion))

        # Crear notificación interna
        cur.execute("""
            INSERT INTO notificacion
                (id_usuario, titulo, mensaje, fecha, leida)
            VALUES (%s, %s, %s, NOW(), 0)
        """, (
            session['id_usuario'],
            'Registro Autorizado',
            f"El registro de {sol['nombre_solicitante']} ({sol['tipo_solicitud']}) fue autorizado."
        ))

        mysql.connection.commit()
        cur.close()

        # Enviar correo al solicitante
        if sol['email_solicitante']:
            _enviar_correo_autorizacion(
                destinatario=sol['email_solicitante'],
                nombre=sol['nombre_solicitante'],
                tipo=sol['tipo_solicitud'],
                aprobado=True
            )

        return jsonify({'ok': True, 'mensaje': 'Solicitud autorizada correctamente.'})

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# RECHAZAR
# ══════════════════════════════════════════════════

@autorizar.route("/rechazar/<int:id_autorizacion>", methods=["POST"])
@login_requerido
def rechazar(id_autorizacion):
    comentario = request.form.get('comentario', '').strip()

    if not comentario:
        return jsonify({'ok': False, 'mensaje': 'El comentario es obligatorio'}), 400

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT tipo_solicitud, id_referencia,
                   email_solicitante, nombre_solicitante
            FROM autorizacion_pendiente
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))
        sol = cur.fetchone()

        if not sol:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Solicitud no encontrada'}), 404

        # Actualizar estatus con comentario
        cur.execute("""
            UPDATE autorizacion_pendiente
            SET estatus    = 'Rechazado',
                comentarios = %s,
                id_usuario_autorizador = %s
            WHERE id_autorizacion = %s
        """, (comentario, session['id_usuario'], id_autorizacion))

        # Notificación interna
        cur.execute("""
            INSERT INTO notificacion
                (id_usuario, titulo, mensaje, fecha, leida)
            VALUES (%s, %s, %s, NOW(), 0)
        """, (
            session['id_usuario'],
            'Registro Rechazado',
            f"El registro de {sol['nombre_solicitante']} fue rechazado. Motivo: {comentario}"
        ))

        mysql.connection.commit()
        cur.close()

        # Enviar correo al solicitante
        if sol['email_solicitante']:
            _enviar_correo_autorizacion(
                destinatario=sol['email_solicitante'],
                nombre=sol['nombre_solicitante'],
                tipo=sol['tipo_solicitud'],
                aprobado=False,
                comentario=comentario
            )

        return jsonify({'ok': True, 'mensaje': 'Solicitud rechazada.'})

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# HELPER — enviar correo
# ══════════════════════════════════════════════════

def _enviar_correo_autorizacion(destinatario, nombre, tipo, aprobado, comentario=None):
    try:
        if aprobado:
            asunto = "Tu registro ha sido autorizado — Sistema AVT"
            cuerpo = f"""
Hola {nombre},

Tu solicitud de registro como {tipo} ha sido AUTORIZADA exitosamente.

Ya puedes acercarte a las instalaciones con tu documentación.

Saludos,
Sistema AVT
            """
        else:
            asunto = "Tu registro ha sido rechazado — Sistema AVT"
            cuerpo = f"""
Hola {nombre},

Lamentamos informarte que tu solicitud de registro como {tipo} ha sido RECHAZADA.

Motivo: {comentario}

Si tienes dudas, comunícate con la administración.

Saludos,
Sistema AVT
            """
        msg = Message(
            subject=asunto,
            recipients=[destinatario],
            body=cuerpo
        )
        mail.send(msg)
    except Exception as e:
        print(f"Error enviando correo: {e}")