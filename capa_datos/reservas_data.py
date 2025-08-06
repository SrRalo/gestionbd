import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict, call_function, call_procedure
from capa_datos.auditoria_data import registrar_accion_auditoria
from datetime import datetime, date

def crear_reserva_db(conn, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones=None):
    """
    Crea una nueva reserva usando la función crear_reserva de PostgreSQL.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente
        cancha_id (int): ID de la cancha
        fecha_reserva (date): Fecha de la reserva
        hora_inicio (time): Hora de inicio
        hora_fin (time): Hora de fin
        observaciones (str): Observaciones opcionales
    
    Returns:
        int: ID de la reserva creada o None si hay error
    """
    try:
        with conn.cursor() as cur:
            # Convertir objetos time a strings para PostgreSQL
            hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if hora_inicio else None
            hora_fin_str = hora_fin.strftime('%H:%M:%S') if hora_fin else None
            
            cur.callproc('crear_reserva', (cliente_id, cancha_id, fecha_reserva, hora_inicio_str, hora_fin_str, observaciones))
            result = cur.fetchone()
            reserva_id = result[0] if result else None
            conn.commit()
            
            # Registrar en auditoría manualmente
            if reserva_id:
                registrar_accion_auditoria(
                    usuario_id=st.session_state.get('current_user', {}).get('id'),
                    tipo_accion="INSERT",
                    tabla="reservas",
                    registro_id=reserva_id,
                    detalles=f"Nueva reserva creada: Cliente {cliente_id}, Cancha {cancha_id}, Fecha {fecha_reserva}"
                )
            
            return reserva_id
    except psycopg2.Error as e:
        st.error(f"Error al crear reserva: {e}")
        conn.rollback()
        return None

def get_reservas_db(conn):
    """
    Obtiene todas las reservas con información completa.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de reservas con información completa
    """
    sql = """
    SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           r.fecha_reserva, r.hora_inicio, r.hora_fin, 
           r.duracion,
           r.estado, r.observaciones,
           ca.precio_hora, (ca.precio_hora * r.duracion) as precio_total,
           r.fecha_creacion
    FROM reservas r
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC;
    """
    return execute_query_dict(conn, sql)

def get_reserva_by_id_db(conn, reserva_id):
    """
    Obtiene una reserva específica por su ID.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva
    
    Returns:
        dict: Datos de la reserva o None si no existe
    """
    sql = """
    SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           r.fecha_reserva, r.hora_inicio, r.hora_fin, 
           r.duracion,
           r.estado, r.observaciones,
           ca.precio_hora, (ca.precio_hora * r.duracion) as precio_total,
           r.fecha_creacion
    FROM reservas r
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE r.id = %s;
    """
    result = execute_query_dict(conn, sql, (reserva_id,))
    return result[0] if result else None

def update_reserva_db(conn, reserva_id, estado, observaciones):
    """
    Actualiza el estado y observaciones de una reserva.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva
        estado (str): Nuevo estado
        observaciones (str): Nuevas observaciones
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    try:
        sql = """
        UPDATE reservas 
        SET estado = %s, observaciones = %s
        WHERE id = %s
        """
        result = execute_query(conn, sql, (estado, observaciones, reserva_id), fetch=False)
        
        # Registrar en auditoría manualmente
        if result:
            registrar_accion_auditoria(
                usuario_id=st.session_state.get('current_user', {}).get('id'),
                tipo_accion="UPDATE",
                tabla="reservas",
                registro_id=reserva_id,
                detalles=f"Reserva actualizada: Estado {estado}, Observaciones: {observaciones}"
            )
        
        return result is not None
    except Exception as e:
        st.error(f"Error al actualizar reserva: {e}")
        return False

def cancelar_reserva_db(conn, reserva_id, motivo_cancelacion):
    """
    Cancela una reserva cambiando su estado a 'cancelada'.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva
        motivo_cancelacion (str): Motivo de la cancelación
    
    Returns:
        bool: True si se canceló correctamente, False en caso contrario
    """
    try:
        sql = """
        UPDATE reservas 
        SET estado = 'cancelada', observaciones = %s
        WHERE id = %s
        """
        result = execute_query(conn, sql, (motivo_cancelacion, reserva_id), fetch=False)
        
        # Registrar en auditoría manualmente
        if result:
            registrar_accion_auditoria(
                usuario_id=st.session_state.get('current_user', {}).get('id'),
                tipo_accion="UPDATE",
                tabla="reservas",
                registro_id=reserva_id,
                detalles=f"Reserva cancelada: {motivo_cancelacion}"
            )
        
        return result is not None
    except Exception as e:
        st.error(f"Error al cancelar reserva: {e}")
        return False

def get_reservas_por_fecha_db(conn, fecha):
    """
    Obtiene las reservas para una fecha específica.
    
    Args:
        conn: Conexión a la base de datos
        fecha (date): Fecha para filtrar las reservas
    
    Returns:
        list: Lista de reservas para la fecha especificada
    """
    sql = """
    SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           r.fecha_reserva, r.hora_inicio, r.hora_fin, 
           r.duracion,
           r.estado, r.observaciones,
           ca.precio_hora, (ca.precio_hora * r.duracion) as precio_total,
           r.fecha_creacion
    FROM reservas r
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE r.fecha_reserva = %s
    ORDER BY r.hora_inicio ASC;
    """
    return execute_query_dict(conn, sql, (fecha,))

def get_reservas_por_cliente_db(conn, cliente_id):
    """
    Obtiene todas las reservas de un cliente específico.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente
    
    Returns:
        list: Lista de reservas del cliente
    """
    sql = """
    SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           r.fecha_reserva, r.hora_inicio, r.hora_fin, 
           r.duracion,
           r.estado, r.observaciones,
           ca.precio_hora, (ca.precio_hora * r.duracion) as precio_total,
           r.fecha_creacion
    FROM reservas r
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE r.cliente_id = %s
    ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC;
    """
    return execute_query_dict(conn, sql, (cliente_id,))

def get_reservas_por_cancha_db(conn, cancha_id):
    """
    Obtiene todas las reservas de una cancha específica.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha
    
    Returns:
        list: Lista de reservas de la cancha
    """
    sql = """
    SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           r.fecha_reserva, r.hora_inicio, r.hora_fin, 
           r.duracion,
           r.estado, r.observaciones,
           ca.precio_hora, (ca.precio_hora * r.duracion) as precio_total,
           r.fecha_creacion
    FROM reservas r
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE r.cancha_id = %s
    ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC;
    """
    return execute_query_dict(conn, sql, (cancha_id,))

def get_reservas_activas_db(conn):
    """
    Obtiene todas las reservas activas (no canceladas).
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de reservas activas
    """
    sql = """
    SELECT r.id, r.cliente_id, c.nombre as cliente_nombre, c.apellido as cliente_apellido,
           r.cancha_id, ca.nombre as cancha_nombre, tc.nombre as tipo_cancha,
           r.fecha_reserva, r.hora_inicio, r.hora_fin, 
           r.duracion,
           r.estado, r.observaciones,
           ca.precio_hora, (ca.precio_hora * r.duracion) as precio_total,
           r.fecha_creacion
    FROM reservas r
    JOIN clientes c ON r.cliente_id = c.id
    JOIN canchas ca ON r.cancha_id = ca.id
    JOIN tipos_cancha tc ON ca.tipo_cancha_id = tc.id
    WHERE r.estado != 'cancelada'
    ORDER BY r.fecha_reserva ASC, r.hora_inicio ASC;
    """
    return execute_query_dict(conn, sql)

def limpiar_reservas_antiguas_db(conn, fecha_corte):
    """
    Elimina reservas más antiguas que la fecha especificada.
    
    Args:
        conn: Conexión a la base de datos
        fecha_corte (date): Fecha límite para eliminar reservas
    
    Returns:
        int: Número de reservas eliminadas
    """
    try:
        sql = "DELETE FROM reservas WHERE fecha_reserva < %s"
        result = execute_query(conn, sql, (fecha_corte,), fetch=False)
        return result if result else 0
    except Exception as e:
        st.error(f"Error al limpiar reservas antiguas: {e}")
        return 0

def verificar_disponibilidad_db(conn, cancha_id, fecha, hora_inicio, hora_fin, reserva_id_excluir=None):
    """
    Verifica si una cancha está disponible en un horario específico.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha
        fecha (date): Fecha de la reserva
        hora_inicio (time): Hora de inicio
        hora_fin (time): Hora de fin
        reserva_id_excluir (int): ID de reserva a excluir (para actualizaciones)
    
    Returns:
        bool: True si está disponible, False si no
    """
    try:
        with conn.cursor() as cur:
            # Convertir objetos time a strings para PostgreSQL
            hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if hora_inicio else None
            hora_fin_str = hora_fin.strftime('%H:%M:%S') if hora_fin else None
            
            cur.callproc('verificar_disponibilidad_cancha', (cancha_id, fecha, hora_inicio_str, hora_fin_str, reserva_id_excluir))
            result = cur.fetchone()
            return result[0] if result else False
    except psycopg2.Error as e:
        st.error(f"Error al verificar disponibilidad: {e}")
        return False 