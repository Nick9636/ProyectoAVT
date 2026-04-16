from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from extensiones import mysql

consulta = Blueprint('consulta', __name__, url_prefix="/consulta")


def login_requerido(f):
    from functools import wraps
    @wraps(f)
    def decorador(*args, **kwargs):
        if 'id_usuario' not in session:
            return redirect(url_for('auth.iniciarSesion'))
        return f(*args, **kwargs)
    return decorador


# ══════════════════════════════════════════════════
# GENERAL
# ══════════════════════════════════════════════════

@consulta.route("/")
@login_requerido
def consultaGeneral():
    return render_template("consulta/consultaGeneral.html")


# ══════════════════════════════════════════════════
# REGISTROS — todos (jugador + entrenador + árbitro)
# ══════════════════════════════════════════════════

@consulta.route("/registro")
@login_requerido
def consultarRegistro():
    nombre = request.args.get('nombre', '').strip()
    curp   = request.args.get('curp',   '').strip()
    rol    = request.args.get('rol',    '').strip()

    cur = mysql.connection.cursor()
    resultados = []

    tablas = {
        'jugador':    ('jugador',    'id_jugador'),
        'entrenador': ('entrenador', 'id_entrenador'),
        'arbitro':    ('arbitro',    'id_arbitro'),
    }

    tipos_buscar = [rol] if rol in tablas else list(tablas.keys())

    for tipo in tipos_buscar:
        tabla, pk = tablas[tipo]
        condiciones = []
        valores     = []

        if nombre:
            condiciones.append("""
                CONCAT(apellido_paterno,' ',apellido_materno,' ',nombres) LIKE %s
            """)
            valores.append(f'%{nombre}%')
        if curp:
            condiciones.append("curp LIKE %s")
            valores.append(f'%{curp}%')

        where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

        cur.execute(f"""
            SELECT {pk} AS id, tipo_tabla,
                   apellido_paterno, apellido_materno, nombres,
                   curp, categoria, fecha_registro, '{tipo}' AS tipo
            FROM (
                SELECT {pk}, '{tipo}' AS tipo_tabla,
                       apellido_paterno, apellido_materno, nombres,
                       curp, categoria, fecha_registro
                FROM {tabla}
                {where}
            ) sub
        """, valores)
        resultados += cur.fetchall()

    # Contadores totales
    cur.execute("SELECT COUNT(*) AS total FROM jugador")
    total_j = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) AS total FROM entrenador")
    total_e = cur.fetchone()['total']
    cur.execute("SELECT COUNT(*) AS total FROM arbitro")
    total_a = cur.fetchone()['total']
    cur.close()

    return render_template(
        "consulta/consultarRegistro.html",
        resultados=resultados,
        total_jugadores=total_j,
        total_entrenadores=total_e,
        total_arbitros=total_a,
        filtro_nombre=nombre,
        filtro_curp=curp,
        filtro_rol=rol
    )


# ══════════════════════════════════════════════════
# AFILIADOS — solo activos (con expediente activo)
# ══════════════════════════════════════════════════

@consulta.route("/afiliado")
@login_requerido
def consultarAfiliado():
    nombre = request.args.get('nombre', '').strip()
    curp   = request.args.get('curp',   '').strip()
    rol    = request.args.get('rol',    '').strip()

    cur = mysql.connection.cursor()
    condiciones_extra = []
    valores           = []

    if nombre:
        condiciones_extra.append("""
            CONCAT(p.apellido_paterno,' ',p.apellido_materno,' ',p.nombres) LIKE %s
        """)
        valores.append(f'%{nombre}%')
    if curp:
        condiciones_extra.append("p.curp LIKE %s")
        valores.append(f'%{curp}%')

    where_extra = f"AND {' AND '.join(condiciones_extra)}" if condiciones_extra else ""

    resultados = []
    tablas = {
        'jugador':    ('jugador',    'id_jugador'),
        'entrenador': ('entrenador', 'id_entrenador'),
        'arbitro':    ('arbitro',    'id_arbitro'),
    }
    tipos_buscar = [rol] if rol in tablas else list(tablas.keys())

    for tipo in tipos_buscar:
        tabla, pk = tablas[tipo]
        cur.execute(f"""
            SELECT p.{pk} AS id,
                   p.apellido_paterno, p.apellido_materno, p.nombres,
                   p.curp, p.categoria, p.fecha_registro,
                   e.id_expediente, e.estatus,
                   '{tipo}' AS tipo
            FROM {tabla} p
            JOIN expediente e ON e.{pk} = p.{pk}
            WHERE e.estatus = 'activo'
            {where_extra}
        """, valores)
        resultados += cur.fetchall()

    # Contadores de activos
    cur.execute("""
        SELECT COUNT(*) AS total FROM jugador j
        JOIN expediente e ON e.id_jugador = j.id_jugador
        WHERE e.estatus = 'activo'
    """)
    activos_j = cur.fetchone()['total']

    cur.execute("""
        SELECT COUNT(*) AS total FROM entrenador en
        JOIN expediente e ON e.id_entrenador = en.id_entrenador
        WHERE e.estatus = 'activo'
    """)
    activos_e = cur.fetchone()['total']

    cur.execute("""
        SELECT COUNT(*) AS total FROM arbitro a
        JOIN expediente e ON e.id_arbitro = a.id_arbitro
        WHERE e.estatus = 'activo'
    """)
    activos_a = cur.fetchone()['total']
    cur.close()

    return render_template(
        "consulta/consultarAfiliado.html",
        resultados=resultados,
        activos_jugadores=activos_j,
        activos_entrenadores=activos_e,
        activos_arbitros=activos_a,
        filtro_nombre=nombre,
        filtro_curp=curp,
        filtro_rol=rol
    )


# ══════════════════════════════════════════════════
# LIGAS
# ══════════════════════════════════════════════════

@consulta.route("/ligas")
@login_requerido
def consultarLigas():
    nombre = request.args.get('nombre', '').strip()
    estado = request.args.get('estado', '').strip()

    cur = mysql.connection.cursor()

    condiciones = []
    valores     = []
    if nombre:
        condiciones.append("l.nombre_liga LIKE %s")
        valores.append(f'%{nombre}%')
    if estado:
        condiciones.append("l.estado = %s")
        valores.append(estado)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    cur.execute(f"""
        SELECT l.id_liga, l.nombre_liga, l.categoria,
               l.estado, l.fecha_inicio,
               COUNT(DISTINCT e.id_equipo) AS total_equipos,
               COUNT(DISTINCT j.id_jugador) AS total_jugadores
        FROM liga l
        LEFT JOIN equipo e ON e.id_liga = l.id_liga
        LEFT JOIN jugador j ON j.id_equipo = e.id_equipo
        {where}
        GROUP BY l.id_liga
        ORDER BY l.nombre_liga
    """, valores)
    ligas = cur.fetchall()

    # Contadores
    cur.execute("SELECT COUNT(*) AS t FROM liga WHERE estado='activo'")
    activas = cur.fetchone()['t']
    cur.execute("SELECT COUNT(*) AS t FROM liga WHERE estado='inactivo'")
    inactivas = cur.fetchone()['t']
    cur.execute("SELECT COUNT(*) AS t FROM equipo")
    total_equipos = cur.fetchone()['t']
    cur.execute("SELECT COUNT(*) AS t FROM jugador")
    total_jugadores = cur.fetchone()['t']
    cur.close()

    return render_template(
        "consulta/consultarLigas.html",
        ligas=ligas,
        activas=activas,
        inactivas=inactivas,
        total_equipos=total_equipos,
        total_jugadores=total_jugadores,
        filtro_nombre=nombre,
        filtro_estado=estado
    )


@consulta.route("/ligas/toggle/<int:id_liga>", methods=["POST"])
@login_requerido
def toggleEstadoLiga(id_liga):
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT estado FROM liga WHERE id_liga = %s", (id_liga,))
        liga = cur.fetchone()
        if not liga:
            cur.close()
            return jsonify({'ok': False, 'mensaje': 'Liga no encontrada'}), 404

        nuevo = 'inactivo' if liga['estado'] == 'activo' else 'activo'
        cur.execute("UPDATE liga SET estado = %s WHERE id_liga = %s", (nuevo, id_liga))
        mysql.connection.commit()
        cur.close()
        return jsonify({'ok': True, 'nuevo_estado': nuevo})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'ok': False, 'mensaje': str(e)}), 500


# ══════════════════════════════════════════════════
# PAGOS
# ══════════════════════════════════════════════════

@consulta.route("/pagos")
@login_requerido
def consultarPagos():
    nombre      = request.args.get('nombre',      '').strip()
    estatus     = request.args.get('estatus',     '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()

    cur = mysql.connection.cursor()

    condiciones = []
    valores     = []

    if nombre:
        condiciones.append("""
            COALESCE(
                CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres),
                CONCAT(e.apellido_paterno,' ',e.apellido_materno,' ',e.nombres),
                CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres)
            ) LIKE %s
        """)
        valores.append(f'%{nombre}%')
    if estatus:
        condiciones.append("p.estatus = %s")
        valores.append(estatus)
    if fecha_desde:
        condiciones.append("p.fecha_pago >= %s")
        valores.append(fecha_desde)
    if fecha_hasta:
        condiciones.append("p.fecha_pago <= %s")
        valores.append(fecha_hasta)

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    cur.execute(f"""
        SELECT p.id_pago, p.fecha_pago, p.estatus,
               p.metodo_pago, p.referencia, p.tipo_persona,
               COALESCE(
                   CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres),
                   CONCAT(e.apellido_paterno,' ',e.apellido_materno,' ',e.nombres),
                   CONCAT(a.apellido_paterno,' ',a.apellido_materno,' ',a.nombres)
               ) AS nombre_persona,
               COALESCE(j.numero_registro,
                        e.numero_registro,
                        a.numero_registro) AS numero_registro
        FROM pago p
        LEFT JOIN jugador    j ON j.id_jugador    = p.id_jugador
        LEFT JOIN entrenador e ON e.id_entrenador = p.id_entrenador
        LEFT JOIN arbitro    a ON a.id_arbitro    = p.id_arbitro
        {where}
        ORDER BY p.fecha_pago DESC
    """, valores)
    pagos = cur.fetchall()

    # Contadores
    cur.execute("SELECT COUNT(*) AS t FROM pago WHERE estatus='Completado'")
    completados = cur.fetchone()['t']
    cur.execute("SELECT COUNT(*) AS t FROM pago WHERE estatus='Pendiente'")
    pendientes = cur.fetchone()['t']
    cur.execute("SELECT COUNT(*) AS t FROM pago WHERE estatus='Cancelado'")
    cancelados = cur.fetchone()['t']
    cur.close()

    return render_template(
        "consulta/consultarPagos.html",
        pagos=pagos,
        completados=completados,
        pendientes=pendientes,
        cancelados=cancelados,
        filtro_nombre=nombre,
        filtro_estatus=estatus,
        filtro_desde=fecha_desde,
        filtro_hasta=fecha_hasta
    )


# ══════════════════════════════════════════════════
# TUTORES
# ══════════════════════════════════════════════════

@consulta.route("/tutor")
@login_requerido
def consultarTutor():
    nombre_tutor = request.args.get('nombre_tutor', '').strip()
    nombre_menor = request.args.get('nombre_menor', '').strip()
    telefono     = request.args.get('telefono',     '').strip()

    cur = mysql.connection.cursor()

    condiciones = []
    valores     = []

    if nombre_tutor:
        condiciones.append("t.nombre_completo LIKE %s")
        valores.append(f'%{nombre_tutor}%')
    if nombre_menor:
        condiciones.append("""
            CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) LIKE %s
        """)
        valores.append(f'%{nombre_menor}%')
    if telefono:
        condiciones.append("t.celular LIKE %s")
        valores.append(f'%{telefono}%')

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    cur.execute(f"""
        SELECT t.id_tutor, t.nombre_completo, t.celular,
               t.correo_electronico, t.curp_tutor,
               CONCAT(j.apellido_paterno,' ',j.apellido_materno,' ',j.nombres) AS nombre_menor,
               TIMESTAMPDIFF(YEAR, j.fecha_nacimiento, CURDATE()) AS edad_menor,
               j.id_jugador
        FROM tutor_padre t
        JOIN jugador j ON j.id_jugador = t.id_jugador
        {where}
        ORDER BY t.nombre_completo
    """, valores)
    tutores_raw = cur.fetchall()

    # Agrupar menores por tutor
    tutores = {}
    for row in tutores_raw:
        tid = row['id_tutor']
        if tid not in tutores:
            tutores[tid] = {
                'id_tutor':           row['id_tutor'],
                'nombre_completo':    row['nombre_completo'],
                'celular':            row['celular'],
                'correo_electronico': row['correo_electronico'],
                'curp_tutor':         row['curp_tutor'],
                'menores':            []
            }
        tutores[tid]['menores'].append({
            'nombre': row['nombre_menor'],
            'edad':   row['edad_menor'],
            'id':     row['id_jugador']
        })

    # Contadores
    cur.execute("SELECT COUNT(DISTINCT id_tutor) AS t FROM tutor_padre")
    total_tutores = cur.fetchone()['t']
    cur.execute("SELECT COUNT(DISTINCT id_jugador) AS t FROM tutor_padre")
    menores_con_tutor = cur.fetchone()['t']
    cur.execute("""
        SELECT COUNT(*) AS t FROM jugador
        WHERE id_jugador NOT IN (SELECT id_jugador FROM tutor_padre)
        AND TIMESTAMPDIFF(YEAR, fecha_nacimiento, CURDATE()) < 18
    """)
    sin_tutor = cur.fetchone()['t']
    cur.close()

    return render_template(
        "consulta/consultarTutor.html",
        tutores=list(tutores.values()),
        total_tutores=total_tutores,
        menores_con_tutor=menores_con_tutor,
        sin_tutor=sin_tutor,
        filtro_nombre_tutor=nombre_tutor,
        filtro_nombre_menor=nombre_menor,
        filtro_telefono=telefono
    )