import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict, call_function, call_procedure
from capa_datos.auditoria_data import registrar_accion_auditoria
from datetime import datetime, date

def crear_reserva_db(conn, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones=None):
    """
    Crea una nueva reserva usando el procedimiento proc_gestionar_reserva.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente
        cancha_id (int): ID de la cancha
        fecha_reserva (date): Fecha de la reserva
        hora_inicio (time): Hora de inicio
        hora_fin (time): Hora de fin
        observaciones (str): Observaciones opcionales
    
    Returns:
        bool: True si la reserva se creó correctamente, False en caso contrario
    """
    try:
        # Convertir objetos time a strings para PostgreSQL
        hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if hora_inicio else None
        hora_fin_str = hora_fin.strftime('%H:%M:%S') if hora_fin else None
        
        # Llamar al procedimiento almacenado
        success = call_procedure(conn, 'proc_gestionar_reserva', 
                               ('CREATE', None, cliente_id, cancha_id, fecha_reserva, 
                                hora_inicio_str, hora_fin_str, observaciones, 'pendiente'))
        
        if success:
            # Obtener el ID de la reserva creada para auditoría
            sql = """
            SELECT id FROM reservas 
            WHERE cliente_id = %s AND cancha_id = %s AND fecha_reserva = %s 
            AND hora_inicio = %s AND hora_fin = %s
            ORDER BY fecha_creacion DESC LIMIT 1
            """
            result = execute_query(conn, sql, (cliente_id, cancha_id, fecha_reserva, hora_inicio_str, hora_fin_str))
            
            if result:
                reserva_id = result[0][0]
                # Registrar en auditoría
                registrar_accion_auditoria(conn, 'reservas', 'INSERT', reserva_id, 
                                         f'Reserva creada: Cliente {cliente_id}, Cancha {cancha_id}, Fecha {fecha_reserva}')
            
            conn.commit()
            st.success("✅ Reserva creada correctamente")
            return True
        else:
            conn.rollback()
            st.error("❌ Error al crear la reserva")
            return False
            
    except Exception as e:
        conn.rollback()
        st.error(f"Error al crear reserva: {e}")
        return False

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

def actualizar_reserva_db(conn, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones=None, estado='pendiente'):
    """
    Actualiza una reserva existente usando el procedimiento proc_gestionar_reserva.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva a actualizar
        cliente_id (int): ID del cliente
        cancha_id (int): ID de la cancha
        fecha_reserva (date): Fecha de la reserva
        hora_inicio (time): Hora de inicio
        hora_fin (time): Hora de fin
        observaciones (str): Observaciones opcionales
        estado (str): Estado de la reserva
    
    Returns:
        bool: True si la reserva se actualizó correctamente, False en caso contrario
    """
    try:
        # Convertir objetos time a strings para PostgreSQL
        hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if hora_inicio else None
        hora_fin_str = hora_fin.strftime('%H:%M:%S') if hora_fin else None
        
        # Llamar al procedimiento almacenado
        success = call_procedure(conn, 'proc_gestionar_reserva', 
                               ('UPDATE', reserva_id, cliente_id, cancha_id, fecha_reserva, 
                                hora_inicio_str, hora_fin_str, observaciones, estado))
        
        if success:
            # Registrar en auditoría
            registrar_accion_auditoria(conn, 'reservas', 'UPDATE', reserva_id, 
                                     f'Reserva actualizada: ID {reserva_id}, Cliente {cliente_id}, Cancha {cancha_id}')
            
            conn.commit()
            st.success("✅ Reserva actualizada correctamente")
            return True
        else:
            conn.rollback()
            st.error("❌ Error al actualizar la reserva")
            return False
            
    except Exception as e:
        conn.rollback()
        st.error(f"Error al actualizar reserva: {e}")
        return False

def cancelar_reserva_db(conn, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin):
    """
    Cancela una reserva usando el procedimiento proc_gestionar_reserva.
    
    Args:
        conn: Conexión a la base de datos
        reserva_id (int): ID de la reserva a cancelar
        cliente_id (int): ID del cliente
        cancha_id (int): ID de la cancha
        fecha_reserva (date): Fecha de la reserva
        hora_inicio (time): Hora de inicio
        hora_fin (time): Hora de fin
    
    Returns:
        bool: True si la reserva se canceló correctamente, False en caso contrario
    """
    try:
        # Convertir objetos time a strings para PostgreSQL
        hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if hora_inicio else None
        hora_fin_str = hora_fin.strftime('%H:%M:%S') if hora_fin else None
        
        # Llamar al procedimiento almacenado
        success = call_procedure(conn, 'proc_gestionar_reserva', 
                               ('CANCEL', reserva_id, cliente_id, cancha_id, fecha_reserva, 
                                hora_inicio_str, hora_fin_str))
        
        if success:
            # Registrar en auditoría
            registrar_accion_auditoria(conn, 'reservas', 'UPDATE', reserva_id, 
                                     f'Reserva cancelada: ID {reserva_id}')
            
            conn.commit()
            st.success("✅ Reserva cancelada correctamente")
            return True
        else:
            conn.rollback()
            st.error("❌ Error al cancelar la reserva")
            return False
            
    except Exception as e:
        conn.rollback()
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
        reserva_id_excluir (int): ID de reserva a excluir (para actualizaciones) - NO USADO
    
    Returns:
        bool: True si está disponible, False si no
    """
    try:
        # Convertir objetos time a strings para PostgreSQL
        hora_inicio_str = hora_inicio.strftime('%H:%M:%S') if hora_inicio else None
        hora_fin_str = hora_fin.strftime('%H:%M:%S') if hora_fin else None
        
        # Intentar usar la función PostgreSQL primero
        try:
            result = call_function(conn, 'verificar_disponibilidad_cancha', 
                                 (cancha_id, fecha, hora_inicio_str, hora_fin_str))
            
            if result is not None:
                return result[0] if isinstance(result, tuple) else result
                
        except Exception as func_error:
            st.warning(f"⚠️ No se pudo usar la función PostgreSQL: {func_error}")
        
        # Fallback: usar consulta SQL directa
        sql = """
        SELECT NOT EXISTS (
            SELECT 1 FROM reservas 
            WHERE cancha_id = %s 
            AND fecha_reserva = %s
            AND estado IN ('confirmada', 'pendiente')
            AND (
                (hora_inicio < %s AND hora_fin > %s) OR
                (hora_inicio >= %s AND hora_inicio < %s)
            )
        ) as disponible
        """
        
        result = execute_query(conn, sql, (cancha_id, fecha, hora_fin_str, hora_inicio_str, hora_inicio_str, hora_fin_str))
        
        if result and len(result) > 0:
            return result[0][0] if isinstance(result[0], tuple) else result[0]
        
        return False
        
    except Exception as e:
        st.error(f"Error al verificar disponibilidad: {e}")
        return False 