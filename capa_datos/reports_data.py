import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict
from datetime import datetime, date

def get_vista_reservas_completas_db(conn, fecha_inicio=None, fecha_fin=None, cliente_id=None, cancha_id=None):
    """
    Obtiene datos de la vista vista_reservas_completas con filtros opcionales.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio para filtrar
        fecha_fin (date): Fecha de fin para filtrar
        cliente_id (int): ID del cliente para filtrar
        cancha_id (int): ID de la cancha para filtrar
    
    Returns:
        list: Lista de reservas completas
    """
    sql = "SELECT * FROM vista_reporte_reservas WHERE 1=1"
    params = []
    
    if fecha_inicio:
        sql += " AND fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND fecha_reserva <= %s"
        params.append(fecha_fin)
    
    if cliente_id:
        sql += " AND cliente_id = %s"
        params.append(cliente_id)
    
    if cancha_id:
        sql += " AND cancha_id = %s"
        params.append(cancha_id)
    
    sql += " ORDER BY fecha_reserva DESC, hora_inicio DESC"
    
    return execute_query_dict(conn, sql, params)

def get_vista_estadisticas_canchas_db(conn, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene datos de la vista vista_estadisticas_canchas con filtros opcionales.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio para filtrar
        fecha_fin (date): Fecha de fin para filtrar
    
    Returns:
        list: Lista de estadísticas de canchas
    """
    sql = "SELECT * FROM vista_canchas_mas_usadas WHERE 1=1"
    params = []
    
    if fecha_inicio:
        sql += " AND fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND fecha_reserva <= %s"
        params.append(fecha_fin)
    
    sql += " ORDER BY total_reservas DESC, ingresos_totales DESC"
    
    return execute_query_dict(conn, sql, params)

def get_estadisticas_generales_db(conn, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene estadísticas generales del sistema.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio para filtrar
        fecha_fin (date): Fecha de fin para filtrar
    
    Returns:
        dict: Estadísticas generales
    """
    # Total de reservas
    sql_reservas = "SELECT COUNT(*) as total_reservas FROM reservas"
    params = []
    
    if fecha_inicio and fecha_fin:
        sql_reservas += " WHERE fecha_reserva BETWEEN %s AND %s"
        params = [fecha_inicio, fecha_fin]
    
    result_reservas = execute_query_dict(conn, sql_reservas, params)
    total_reservas = result_reservas[0]['total_reservas'] if result_reservas else 0
    
    # Total de clientes
    sql_clientes = "SELECT COUNT(*) as total_clientes FROM clientes WHERE activo = true"
    result_clientes = execute_query_dict(conn, sql_clientes)
    total_clientes = result_clientes[0]['total_clientes'] if result_clientes else 0
    
    # Total de canchas
    sql_canchas = "SELECT COUNT(*) as total_canchas FROM canchas WHERE activo = true"
    result_canchas = execute_query_dict(conn, sql_canchas)
    total_canchas = result_canchas[0]['total_canchas'] if result_canchas else 0
    
    # Ingresos totales
    sql_ingresos = "SELECT COALESCE(SUM(monto), 0) as ingresos_totales FROM pagos"
    if fecha_inicio and fecha_fin:
        sql_ingresos += " WHERE fecha_pago BETWEEN %s AND %s"
    
    result_ingresos = execute_query_dict(conn, sql_ingresos, params)
    ingresos_totales = result_ingresos[0]['ingresos_totales'] if result_ingresos else 0
    
    # Reservas por estado
    sql_estados = """
    SELECT estado, COUNT(*) as cantidad
    FROM reservas
    """
    if fecha_inicio and fecha_fin:
        sql_estados += " WHERE fecha_reserva BETWEEN %s AND %s"
    sql_estados += " GROUP BY estado ORDER BY cantidad DESC"
    
    reservas_por_estado = execute_query_dict(conn, sql_estados, params)
    
    return {
        'total_reservas': total_reservas,
        'total_clientes': total_clientes,
        'total_canchas': total_canchas,
        'ingresos_totales': ingresos_totales,
        'reservas_por_estado': reservas_por_estado
    }

def get_estadisticas_mensuales_db(conn, año=None):
    """
    Obtiene estadísticas mensuales.
    
    Args:
        conn: Conexión a la base de datos
        año (int): Año para filtrar (opcional)
    
    Returns:
        list: Estadísticas mensuales
    """
    sql = """
    SELECT 
        EXTRACT(YEAR FROM r.fecha_reserva) as año,
        EXTRACT(MONTH FROM r.fecha_reserva) as mes,
        COUNT(*) as total_reservas,
        COALESCE(SUM(r.duracion * ca.precio_hora), 0) as ingresos_totales,
        COUNT(DISTINCT r.cliente_id) as clientes_unicos,
        COUNT(DISTINCT r.cancha_id) as canchas_utilizadas
    FROM reservas r
    JOIN canchas ca ON r.cancha_id = ca.id
    """
    
    params = []
    if año:
        sql += " WHERE EXTRACT(YEAR FROM fecha_reserva) = %s"
        params.append(año)
    
    sql += """
    GROUP BY EXTRACT(YEAR FROM fecha_reserva), EXTRACT(MONTH FROM fecha_reserva)
    ORDER BY año DESC, mes DESC
    """
    
    return execute_query_dict(conn, sql, params)

def get_estadisticas_semanales_db(conn, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene estadísticas semanales.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio
        fecha_fin (date): Fecha de fin
    
    Returns:
        list: Estadísticas semanales
    """
    sql = """
    SELECT 
        DATE_TRUNC('week', r.fecha_reserva) as semana_inicio,
        COUNT(*) as total_reservas,
        COALESCE(SUM(r.duracion * ca.precio_hora), 0) as ingresos_totales,
        COUNT(DISTINCT r.cliente_id) as clientes_unicos,
        COUNT(DISTINCT r.cancha_id) as canchas_utilizadas
    FROM reservas r
    JOIN canchas ca ON r.cancha_id = ca.id
    WHERE 1=1
    """
    
    params = []
    if fecha_inicio:
        sql += " AND fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND fecha_reserva <= %s"
        params.append(fecha_fin)
    
    sql += """
    GROUP BY DATE_TRUNC('week', fecha_reserva)
    ORDER BY semana_inicio DESC
    """
    
    return execute_query_dict(conn, sql, params)

def get_top_clientes_db(conn, fecha_inicio=None, fecha_fin=None, limit=10):
    """
    Obtiene los clientes con más reservas.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio
        fecha_fin (date): Fecha de fin
        limit (int): Límite de clientes a retornar
    
    Returns:
        list: Top clientes
    """
    sql = """
    SELECT 
        c.id, c.nombre, c.apellido, c.email,
        COUNT(r.id) as total_reservas,
        COALESCE(SUM(r.duracion * ca.precio_hora), 0) as total_gastado,
        AVG(r.duracion * ca.precio_hora) as promedio_por_reserva
    FROM clientes c
    LEFT JOIN reservas r ON c.id = r.cliente_id
    LEFT JOIN canchas ca ON r.cancha_id = ca.id
    WHERE c.estado = 'Activo'
    """
    
    params = []
    if fecha_inicio and fecha_fin:
        sql += " AND r.fecha_reserva BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    
    sql += """
    GROUP BY c.id, c.nombre, c.apellido, c.email
    ORDER BY total_reservas DESC, total_gastado DESC
    LIMIT %s
    """
    params.append(limit)
    
    return execute_query_dict(conn, sql, params)

def get_top_canchas_db(conn, fecha_inicio=None, fecha_fin=None, limit=10):
    """
    Obtiene las canchas más utilizadas.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio
        fecha_fin (date): Fecha de fin
        limit (int): Límite de canchas a retornar
    
    Returns:
        list: Top canchas
    """
    sql = """
    SELECT 
        ca.id, ca.nombre, tc.nombre as tipo_cancha,
        COUNT(r.id) as total_reservas,
        COALESCE(SUM(r.duracion * ca.precio_hora), 0) as ingresos_totales,
        AVG(r.duracion * ca.precio_hora) as promedio_por_reserva
    FROM canchas ca
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    LEFT JOIN reservas r ON ca.id = r.cancha_id
    WHERE ca.estado != 'Inactiva'
    """
    
    params = []
    if fecha_inicio and fecha_fin:
        sql += " AND r.fecha_reserva BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    
    sql += """
    GROUP BY ca.id, ca.nombre, tc.nombre
    ORDER BY total_reservas DESC, ingresos_totales DESC
    LIMIT %s
    """
    params.append(limit)
    
    return execute_query_dict(conn, sql, params)

def get_estadisticas_horarios_db(conn, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene estadísticas por horarios.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio
        fecha_fin (date): Fecha de fin
    
    Returns:
        list: Estadísticas por horarios
    """
    sql = """
    SELECT 
        EXTRACT(HOUR FROM r.hora_inicio) as hora,
        COUNT(*) as total_reservas,
        COALESCE(SUM(r.duracion * ca.precio_hora), 0) as ingresos_totales,
        AVG(r.duracion * ca.precio_hora) as promedio_por_reserva
    FROM reservas r
    JOIN canchas ca ON r.cancha_id = ca.id
    WHERE 1=1
    """
    
    params = []
    if fecha_inicio:
        sql += " AND fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND fecha_reserva <= %s"
        params.append(fecha_fin)
    
    sql += """
    GROUP BY EXTRACT(HOUR FROM hora_inicio)
    ORDER BY hora
    """
    
    return execute_query_dict(conn, sql, params)

def get_estadisticas_dias_semana_db(conn, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene estadísticas por días de la semana.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio
        fecha_fin (date): Fecha de fin
    
    Returns:
        list: Estadísticas por días de la semana
    """
    sql = """
    SELECT 
        EXTRACT(DOW FROM r.fecha_reserva) as dia_semana,
        COUNT(*) as total_reservas,
        COALESCE(SUM(r.duracion * ca.precio_hora), 0) as ingresos_totales,
        AVG(r.duracion * ca.precio_hora) as promedio_por_reserva
    FROM reservas r
    JOIN canchas ca ON r.cancha_id = ca.id
    WHERE 1=1
    """
    
    params = []
    if fecha_inicio:
        sql += " AND fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND fecha_reserva <= %s"
        params.append(fecha_fin)
    
    sql += """
    GROUP BY EXTRACT(DOW FROM fecha_reserva)
    ORDER BY dia_semana
    """
    
    return execute_query_dict(conn, sql, params)

def get_canchas_mas_usadas_db(conn, fecha_inicio=None, fecha_fin=None, limit=10):
    """
    Obtiene las canchas más utilizadas ordenadas de forma descendente.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio para filtrar
        fecha_fin (date): Fecha de fin para filtrar
        limit (int): Límite de canchas a retornar
    
    Returns:
        list: Lista de canchas más utilizadas
    """
    sql = """
    SELECT 
        c.id,
        c.nombre,
        c.tipo_deporte,
        c.precio_hora,
        COUNT(r.id) as total_reservas,
        COALESCE(SUM(r.duracion * c.precio_hora), 0) as ingresos_totales,
        ROUND(AVG(r.duracion * c.precio_hora), 2) as promedio_por_reserva
    FROM canchas c
    LEFT JOIN reservas r ON c.id = r.cancha_id 
        AND r.estado IN ('Confirmada', 'Completada')
    WHERE c.estado = 'Activa'
    """
    
    params = []
    if fecha_inicio:
        sql += " AND r.fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND r.fecha_reserva <= %s"
        params.append(fecha_fin)
    
    sql += """
    GROUP BY c.id, c.nombre, c.tipo_deporte, c.precio_hora
    ORDER BY total_reservas DESC, ingresos_totales DESC
    LIMIT %s
    """
    params.append(limit)
    
    return execute_query_dict(conn, sql, params)

def get_canchas_mas_recaudan_db(conn, fecha_inicio=None, fecha_fin=None, limit=10):
    """
    Obtiene las canchas que más dinero recaudan ordenadas de forma descendente.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio para filtrar
        fecha_fin (date): Fecha de fin para filtrar
        limit (int): Límite de canchas a retornar
    
    Returns:
        list: Lista de canchas que más recaudan
    """
    sql = """
    SELECT 
        c.id,
        c.nombre,
        c.tipo_deporte,
        c.precio_hora,
        COUNT(r.id) as total_reservas,
        COALESCE(SUM(r.duracion * c.precio_hora), 0) as ingresos_totales,
        ROUND(AVG(r.duracion * c.precio_hora), 2) as promedio_por_reserva,
        ROUND(COALESCE(SUM(r.duracion * c.precio_hora), 0) / NULLIF(COUNT(r.id), 0), 2) as ingreso_promedio_por_reserva
    FROM canchas c
    LEFT JOIN reservas r ON c.id = r.cancha_id 
        AND r.estado IN ('Confirmada', 'Completada')
    WHERE c.estado = 'Activa'
    """
    
    params = []
    if fecha_inicio:
        sql += " AND r.fecha_reserva >= %s"
        params.append(fecha_inicio)
    
    if fecha_fin:
        sql += " AND r.fecha_reserva <= %s"
        params.append(fecha_fin)
    
    sql += """
    GROUP BY c.id, c.nombre, c.tipo_deporte, c.precio_hora
    ORDER BY ingresos_totales DESC, total_reservas DESC
    LIMIT %s
    """
    params.append(limit)
    
    return execute_query_dict(conn, sql, params) 