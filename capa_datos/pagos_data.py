import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict, call_procedure
from datetime import datetime

def registrar_pago_db(conn, reserva_id, monto, metodo_pago, observaciones=None):
    """
    Registra un nuevo pago en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva
        monto (float): Monto del pago
        metodo_pago (str): Método de pago utilizado
        observaciones (str): Observaciones del pago (opcional)
    
    Returns:
        bool: True si el pago se registró correctamente, False en caso contrario
    """
    return call_procedure(conn, 'proc_registrar_pago', (reserva_id, monto, metodo_pago, observaciones))

def get_pagos_db(conn):
    """
    Obtiene todos los pagos de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de pagos
    """
    sql = """
        SELECT p.id, p.reserva_id, p.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
               p.monto, p.metodo_pago, p.observaciones,
               p.estado, p.fecha_pago, p.fecha_creacion, p.fecha_actualizacion
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        ORDER BY p.fecha_pago DESC, p.id DESC
    """
    return execute_query_dict(conn, sql)

def get_pago_by_id_db(conn, pago_id):
    """
    Obtiene un pago específico por su ID.
    
    Args:
        conn: Conexión a la base de datos
        pago_id (int): ID del pago
    
    Returns:
        dict: Datos del pago o None si no se encuentra
    """
    sql = """
        SELECT p.id, p.reserva_id, p.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
               p.monto, p.metodo_pago, p.observaciones,
               p.estado, p.fecha_pago, p.fecha_creacion, p.fecha_actualizacion
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.id = %s
    """
    result = execute_query_dict(conn, sql, (pago_id,))
    return result[0] if result else None

def get_pagos_por_reserva_db(conn, reserva_id):
    """
    Obtiene todos los pagos de una reserva específica.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva
    
    Returns:
        list: Lista de pagos de la reserva
    """
    sql = """
        SELECT p.id, p.reserva_id, p.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
               p.monto, p.metodo_pago, p.observaciones,
               p.estado, p.fecha_pago, p.fecha_creacion, p.fecha_actualizacion
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.reserva_id = %s
        ORDER BY p.fecha_pago DESC, p.id DESC
    """
    return execute_query_dict(conn, sql, (reserva_id,))

def get_pagos_por_cliente_db(conn, cliente_id):
    """
    Obtiene todos los pagos de un cliente específico.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente
    
    Returns:
        list: Lista de pagos del cliente
    """
    sql = """
        SELECT p.id, p.reserva_id, p.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
               p.monto, p.metodo_pago, p.observaciones,
               p.estado, p.fecha_pago, p.fecha_creacion, p.fecha_actualizacion
        FROM pagos p
        JOIN clientes c ON p.cliente_id = c.id
        WHERE p.cliente_id = %s
        ORDER BY p.fecha_pago DESC, p.id DESC
    """
    return execute_query_dict(conn, sql, (cliente_id,))

def update_pago_db(conn, pago_id, monto, metodo_pago, estado, observaciones=None):
    """
    Actualiza un pago existente.
    
    Args:
        conn: Conexión a la base de datos
        pago_id (int): ID del pago
        monto (float): Nuevo monto del pago
        metodo_pago (str): Nuevo método de pago
        estado (str): Nuevo estado del pago
        observaciones (str): Nuevas observaciones (opcional)
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    sql = """
        UPDATE pagos 
        SET monto = %s, metodo_pago = %s, estado = %s, observaciones = %s, fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    return execute_query_dict(conn, sql, (monto, metodo_pago, estado, observaciones, pago_id))

def delete_pago_db(conn, pago_id):
    """
    Elimina un pago de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        pago_id (int): ID del pago a eliminar
    
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    sql = "DELETE FROM pagos WHERE id = %s"
    return execute_query_dict(conn, sql, (pago_id,))

def get_pagos_por_fecha_db(conn, fecha_inicio, fecha_fin):
    """
    Obtiene los pagos en un rango de fechas.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (date): Fecha de inicio
        fecha_fin (date): Fecha de fin
    
    Returns:
        list: Lista de pagos en el rango de fechas
    """
    sql = """
    SELECT p.id, p.reserva_id, r.fecha_reserva, r.hora_inicio, r.hora_fin,
           c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           p.monto, p.metodo_pago, p.observaciones,
           p.estado, p.fecha_pago, p.fecha_creacion, p.fecha_actualizacion
    FROM pagos p
    JOIN reservas r ON p.reserva_id = r.id
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE p.fecha_pago BETWEEN %s AND %s
    ORDER BY p.fecha_pago DESC;
    """
    return execute_query_dict(conn, sql, (fecha_inicio, fecha_fin))

def get_pagos_por_metodo_db(conn, metodo_pago):
    """
    Obtiene los pagos por método de pago.
    
    Args:
        conn: Conexión a la base de datos
        metodo_pago (str): Método de pago
    
    Returns:
        list: Lista de pagos por método
    """
    sql = """
    SELECT p.id, p.reserva_id, r.fecha_reserva, r.hora_inicio, r.hora_fin,
           c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           p.monto, p.metodo_pago, p.observaciones,
           p.estado, p.fecha_pago, p.fecha_creacion, p.fecha_actualizacion
    FROM pagos p
    JOIN reservas r ON p.reserva_id = r.id
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE p.metodo_pago = %s
    ORDER BY p.fecha_pago DESC;
    """
    return execute_query_dict(conn, sql, (metodo_pago,))

def get_estadisticas_pagos_db(conn, fecha_inicio=None, fecha_fin=None):
    """
    Obtiene estadísticas de pagos en un rango de fechas.
    
    Args:
        conn: Conexión a la base de datos
        fecha_inicio (str): Fecha de inicio (YYYY-MM-DD)
        fecha_fin (str): Fecha de fin (YYYY-MM-DD)
    
    Returns:
        dict: Estadísticas de pagos
    """
    where_clause = ""
    params = []
    
    if fecha_inicio and fecha_fin:
        where_clause = "WHERE p.fecha_pago BETWEEN %s AND %s"
        params = [fecha_inicio, fecha_fin]
    
    sql = f"""
        SELECT 
            COUNT(*) as total_pagos,
            COALESCE(SUM(p.monto), 0) as monto_total,
            COALESCE(AVG(p.monto), 0) as monto_promedio,
            COUNT(DISTINCT p.cliente_id) as clientes_unicos,
            COUNT(DISTINCT p.reserva_id) as reservas_pagadas
        FROM pagos p
        {where_clause}
    """
    
    result = execute_query_dict(conn, sql, params)
    return result[0] if result else {}

def get_reservas_sin_pago_db(conn):
    """
    Obtiene las reservas que no tienen pagos registrados.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de reservas sin pagos
    """
    sql = """
        SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
               r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
               r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion, r.estado, r.observaciones,
               ca.precio_hora, (r.duracion * ca.precio_hora) as precio_total,
               r.fecha_creacion, r.fecha_actualizacion
        FROM reservas r
        JOIN clientes c ON r.cliente_id = c.id
        JOIN canchas ca ON r.cancha_id = ca.id
        LEFT JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
        WHERE r.id NOT IN (SELECT DISTINCT reserva_id FROM pagos WHERE estado = 'Completado')
        AND r.estado = 'Confirmada'
        ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC
    """
    return execute_query_dict(conn, sql) 