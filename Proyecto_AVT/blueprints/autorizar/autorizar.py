# Adriana Nicole Guzman Ahuatzi
#01/04/2026
# Descripción: Rutas para la autorización de registros de jugadores, entrenadores, árbitros y registros externos.
import logging
import os

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from extensiones import mysql, notificar
from servicios.whatsapp_servicio import notificar_estado_registro

autorizar = Blueprint('autorizar', __name__, url_prefix="/autorizar")
logger = logging.getLogger(__name__)


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.iniciarSesion'))
        # RNF_06: solo Administrador y Presidente pueden autorizar
        if session.get('rol') not in ('Administrador', 'Presidente'):
            mensaje = 'No tienes los permisos suficientes'
            if request.method == 'GET' and not request.path.endswith('/contadores'):
                flash(mensaje, 'permiso')
                return redirect(url_for('registro.registroGeneral'))
            return jsonify({'ok': False, 'error': mensaje}), 403
        return f(*args, **kwargs)
    return decorador


def _obtener_solicitud(cur, id_autorizacion):
    cur.execute("""
        SELECT ap.tipo_solicitud, ap.id_referencia, ap.estatus,
               COALESCE(
                   CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres),
                   CONCAT(e.apellido_paterno,' ',e.apellido_materno,' ',e.nombres),
                   CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres),
                   ap.nombre_solicitante
               ) AS nombre_solicitante,
               COALESCE(j.correo_electronico, e.correo_electronico,
                        a.correo_electronico, ap.email_solicitante) AS email_solicitante,
               COALESCE(j.celular, e.celular, a.celular) AS telefono_solicitante
        FROM autorizacion_pendiente ap
        LEFT JOIN jugador j ON j.id_jugador = ap.id_referencia
            AND ap.tipo_solicitud = 'jugador'
        LEFT JOIN entrenador e ON e.id_entrenador = ap.id_referencia
            AND ap.tipo_solicitud = 'entrenador'
        LEFT JOIN arbitro a ON a.id_arbitro = ap.id_referencia
            AND ap.tipo_solicitud = 'arbitro'
        WHERE ap.id_autorizacion = %s
        FOR UPDATE
    """, (id_autorizacion,))
    return cur.fetchone()


def _enviar_aviso_whatsapp(solicitud, estado, comentario=None):
    telefono = solicitud.get('telefono_solicitante')
    if not telefono:
        logger.warning(
            "No se notificó por WhatsApp la solicitud %s: no tiene teléfono.",
            solicitud.get('id_referencia')
        )
        return " No se envió el aviso por WhatsApp porque no hay teléfono registrado."

    try:
        resultado = notificar_estado_registro(
            telefono,
            estado,
            solicitud.get('nombre_solicitante') or "solicitante",
            comentario
        )
    except ValueError as error:
        logger.warning("Configuración de WhatsApp incompleta: %s", error)
        return " No se envió el aviso por WhatsApp: falta configurar la plantilla."

    if not resultado['exito']:
        logger.error(
            "Falló el aviso de WhatsApp para la solicitud %s: %s",
            solicitud.get('id_referencia'),
            resultado['error']
        )
        return " El registro se actualizó, pero no se pudo enviar el aviso por WhatsApp."
    return ""


def _eliminar_registro_rechazado(cur, tipo_solicitud, id_referencia):
    rutas_archivos = []
    if tipo_solicitud == 'jugador':
        cur.execute(
            "SELECT fotografia AS ruta FROM jugador "
            "WHERE id_jugador = %s AND fotografia IS NOT NULL",
            (id_referencia,)
        )
        rutas_archivos.extend(row['ruta'] for row in cur.fetchall())
        cur.execute(
            "SELECT fotografia_ine AS ruta FROM tutor_padre "
            "WHERE id_jugador = %s AND fotografia_ine IS NOT NULL",
            (id_referencia,)
        )
        rutas_archivos.extend(row['ruta'] for row in cur.fetchall())
        cur.execute(
            "SELECT ruta FROM formato_digital WHERE id_jugador = %s",
            (id_referencia,)
        )
        rutas_archivos.extend(row['ruta'] for row in cur.fetchall())

        cur.execute("DELETE FROM tutor_padre WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM formato_digital WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM expediente WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM direccion WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM jugador_liga WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM sanciones WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM afiliacion WHERE id_jugador = %s", (id_referencia,))
        cur.execute("DELETE FROM jugador WHERE id_jugador = %s", (id_referencia,))
    elif tipo_solicitud == 'entrenador':
        cur.execute(
            "SELECT fotografia AS ruta FROM entrenador "
            "WHERE id_entrenador = %s AND fotografia IS NOT NULL",
            (id_referencia,)
        )
        rutas_archivos.extend(row['ruta'] for row in cur.fetchall())
        cur.execute(
            "DELETE FROM entrenador WHERE id_entrenador = %s", (id_referencia,)
        )
    elif tipo_solicitud == 'arbitro':
        cur.execute(
            "SELECT fotografia AS ruta FROM arbitro "
            "WHERE id_arbitro = %s AND fotografia IS NOT NULL",
            (id_referencia,)
        )
        rutas_archivos.extend(row['ruta'] for row in cur.fetchall())
        cur.execute("DELETE FROM arbitro WHERE id_arbitro = %s", (id_referencia,))
    else:
        raise ValueError(f"Tipo de solicitud no reconocido: {tipo_solicitud}")

    rutas_eliminables = []
    directorio_proyecto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    directorio_uploads = os.path.abspath(
        os.path.join(directorio_proyecto, 'static', 'uploads')
    )
    consulta_referencia = """
        SELECT COUNT(*) AS total
        FROM (
            SELECT fotografia AS ruta FROM jugador
            UNION ALL SELECT fotografia FROM entrenador
            UNION ALL SELECT fotografia FROM arbitro
            UNION ALL SELECT fotografia_ine FROM tutor_padre
            UNION ALL SELECT ruta FROM formato_digital
        ) archivos
        WHERE ruta = %s
    """
    for ruta in set(rutas_archivos):
        cur.execute(consulta_referencia, (ruta,))
        if cur.fetchone()['total']:
            continue

        ruta_absoluta = os.path.abspath(
            ruta if os.path.isabs(ruta) else os.path.join(directorio_proyecto, ruta)
        )
        try:
            dentro_de_uploads = (
                os.path.commonpath((directorio_uploads, ruta_absoluta))
                == directorio_uploads
            )
        except ValueError:
            dentro_de_uploads = False
        if dentro_de_uploads:
            rutas_eliminables.append(ruta_absoluta)

    return rutas_eliminables


def _eliminar_archivos(rutas):
    hubo_error = False
    for ruta in rutas:
        try:
            os.remove(ruta)
        except FileNotFoundError:
            continue
        except OSError:
            logger.exception("No se pudo eliminar un archivo de un registro rechazado.")
            hubo_error = True
    return hubo_error


# ══════════════════════════════════════════════════
# VISTA PRINCIPAL
# ══════════════════════════════════════════════════

@autorizar.route("/")
@login_requerido
def autorizarRegistro():
    cur = mysql.connection.cursor()

    # Contadores
    cur.execute("""
        SELECT
            SUM(estatus = 'Pendiente')  AS pendientes,
            SUM(estatus = 'Autorizado'
                AND DATE(fecha_solicitud) = CURDATE()) AS hoy,
            SUM(estatus = 'Rechazado')  AS rechazadas
        FROM autorizacion_pendiente
    """)
    contadores = cur.fetchone()

    # Solicitudes con datos de la persona relacionada
    cur.execute("""
        SELECT
            ap.id_autorizacion,
            ap.tipo_solicitud,
            ap.id_referencia,
            ap.fecha_solicitud,
            ap.estatus,
            ap.comentarios,
            COALESCE(
                CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres),
                CONCAT(e.apellido_paterno,' ',e.apellido_materno,' ',e.nombres),
                CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres),
                ap.nombre_solicitante,
                re.nombre_completo
            ) AS nombre_persona,
            COALESCE(j.curp, e.curp, a.curp, re.curp) AS curp,
            NULL AS categoria,
            COALESCE(j.correo_electronico, e.correo_electronico,
                     a.correo_electronico, ap.email_solicitante, re.email) AS email_solicitante,
            COALESCE(
                CONCAT(j.apellido_paterno,' ',j.nombres),
                CONCAT(e.apellido_paterno,' ',e.nombres),
                CONCAT(a.apellido_paterno,' ',a.nombres),
                ap.nombre_solicitante,
                re.nombre_completo
            ) AS nombre_solicitante
        FROM autorizacion_pendiente ap
        LEFT JOIN jugador    j  ON j.id_jugador    = ap.id_referencia AND ap.tipo_solicitud = 'jugador'
        LEFT JOIN entrenador e  ON e.id_entrenador = ap.id_referencia AND ap.tipo_solicitud = 'entrenador'
        LEFT JOIN arbitro    a  ON a.id_arbitro    = ap.id_referencia AND ap.tipo_solicitud = 'arbitro'
        LEFT JOIN registro_externo re ON re.id_registro = ap.id_referencia
            AND j.id_jugador IS NULL AND e.id_entrenador IS NULL AND a.id_arbitro IS NULL
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
# CONTADORES (para actualizar en tiempo real)
# ══════════════════════════════════════════════════

@autorizar.route("/contadores")
@login_requerido
def contadores():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT
            SUM(estatus = 'Pendiente')  AS pendientes,
            SUM(estatus = 'Autorizado'
                AND DATE(fecha_solicitud) = CURDATE()) AS hoy,
            SUM(estatus = 'Rechazado')  AS rechazadas
        FROM autorizacion_pendiente
    """)
    contadores = cur.fetchone()
    cur.close()
    return jsonify(contadores)


# ══════════════════════════════════════════════════
# APROBAR
# ══════════════════════════════════════════════════

@autorizar.route("/aprobar/<int:id_autorizacion>", methods=["POST"])
@login_requerido
def aprobar(id_autorizacion):
    cur = mysql.connection.cursor()
    try:
        sol = _obtener_solicitud(cur, id_autorizacion)

        if not sol:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Solicitud no encontrada'}), 404
        if sol['estatus'] != 'Pendiente':
            cur.close()
            return jsonify({
                'ok': False,
                'mensaje': 'Solo se pueden autorizar solicitudes pendientes.'
            }), 409

        # Actualizar estatus
        cur.execute("""
            UPDATE autorizacion_pendiente
            SET estatus = 'Autorizado'
            WHERE id_autorizacion = %s
        """, (id_autorizacion,))

        notificar(cur, session['id_usuario'],
                  f"Registro de {sol['tipo_solicitud']} (ref: #{sol['id_referencia']}) autorizado correctamente.")

        mysql.connection.commit()
        cur.close()

        detalle_whatsapp = _enviar_aviso_whatsapp(sol, 'aprobado')
        return jsonify({
            'ok': True,
            'mensaje': 'Solicitud autorizada correctamente.' + detalle_whatsapp
        })

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
        sol = _obtener_solicitud(cur, id_autorizacion)

        if not sol:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Solicitud no encontrada'}), 404
        if sol['estatus'] != 'Pendiente':
            cur.close()
            return jsonify({
                'ok': False,
                'mensaje': 'Solo se pueden rechazar solicitudes pendientes.'
            }), 409
        if sol['tipo_solicitud'] not in ('jugador', 'entrenador', 'arbitro'):
            cur.close()
            return jsonify({
                'ok': False,
                'mensaje': 'El tipo de solicitud no permite eliminación automática.'
            }), 400

        if sol['tipo_solicitud'] == 'jugador':
            cur.execute("""
                SELECT COUNT(*) AS total
                FROM pago p
                JOIN afiliacion af ON af.id_afiliacion = p.id_afiliacion
                WHERE af.id_jugador = %s
            """, (sol['id_referencia'],))
            pagos_vinculados = cur.fetchone()['total']
            if pagos_vinculados:
                cur.close()
                return jsonify({
                    'ok': False,
                    'mensaje': (
                        'No se puede eliminar este registro porque tiene pagos '
                        'vinculados. Resuelve el historial de pagos antes de rechazarlo.'
                    )
                }), 409

        cur.execute("""
            UPDATE autorizacion_pendiente
            SET estatus     = 'Rechazado',
                comentarios = %s,
                nombre_solicitante = %s,
                email_solicitante = %s
            WHERE id_autorizacion = %s
        """, (
            comentario, sol['nombre_solicitante'], sol['email_solicitante'],
            id_autorizacion
        ))

        rutas_archivos = _eliminar_registro_rechazado(
            cur, sol['tipo_solicitud'], sol['id_referencia']
        )

        notificar(cur, session['id_usuario'],
                  f"Registro de {sol['tipo_solicitud']} (ref: #{sol['id_referencia']}) rechazado. Motivo: {comentario}")

        mysql.connection.commit()
        error_archivos = _eliminar_archivos(rutas_archivos)
        cur.close()

        detalle_whatsapp = _enviar_aviso_whatsapp(sol, 'rechazado', comentario)
        mensaje = 'Solicitud rechazada y registro eliminado.' + detalle_whatsapp
        if error_archivos:
            mensaje += ' Algunos archivos no pudieron eliminarse; contacta al administrador.'
        return jsonify({'ok': True, 'mensaje': mensaje})

    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500