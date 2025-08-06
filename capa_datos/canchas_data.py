import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict

# ==================== TIPOS DE CANCHA ====================

def insert_tipo_cancha_db(conn, nombre, descripcion, precio_por_hora):
    """
    Inserta un nuevo tipo de cancha en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        nombre (str): Nombre del tipo de cancha
        descripcion (str): Descripción del tipo de cancha
        precio_por_hora (decimal): Precio por hora
    
    Returns:
        int: ID del tipo de cancha insertado o None si hay error
    """
    sql = """
    INSERT INTO tipos_cancha (nombre, descripcion, precio_por_hora)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, descripcion, precio_por_hora))
            tipo_id = cur.fetchone()[0]
            conn.commit()
            return tipo_id
    except psycopg2.Error as e:
        st.error(f"Error al insertar tipo de cancha: {e}")
        conn.rollback()
        return None

def get_tipos_cancha_db(conn):
    """
    Obtiene todos los tipos de cancha de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de tipos de cancha
    """
    sql = """
    SELECT id, nombre, descripcion, precio_por_hora, estado, fecha_creacion, fecha_actualizacion
    FROM tipos_cancha 
    ORDER BY nombre;
    """
    return execute_query_dict(conn, sql)

def get_tipo_cancha_by_id_db(conn, tipo_id):
    """
    Obtiene un tipo de cancha específico por su ID.
    
    Args:
        conn: Conexión a la base de datos
        tipo_id (int): ID del tipo de cancha
    
    Returns:
        dict: Datos del tipo de cancha o None si no existe
    """
    sql = """
    SELECT id, nombre, descripcion, precio_por_hora, estado, fecha_creacion, fecha_actualizacion
    FROM tipos_cancha 
    WHERE id = %s;
    """
    result = execute_query_dict(conn, sql, (tipo_id,))
    return result[0] if result else None

def update_tipo_cancha_db(conn, tipo_id, nombre, descripcion, precio_por_hora, activo):
    """
    Actualiza los datos de un tipo de cancha.
    
    Args:
        conn: Conexión a la base de datos
        tipo_id (int): ID del tipo de cancha a actualizar
        nombre (str): Nuevo nombre
        descripcion (str): Nueva descripción
        precio_por_hora (decimal): Nuevo precio por hora
        activo (bool): Estado activo/inactivo
    
    Returns:
        bool: True si la actualización fue exitosa
    """
    sql = """
    UPDATE tipos_cancha 
    SET nombre = %s, descripcion = %s, precio_por_hora = %s, estado = %s, fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = %s;
    """
    return execute_query(conn, sql, (nombre, descripcion, precio_por_hora, activo, tipo_id), fetch=False) is not None

def delete_tipo_cancha_db(conn, tipo_id):
    """
    Elimina un tipo de cancha de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        tipo_id (int): ID del tipo de cancha a eliminar
    
    Returns:
        bool: True si la eliminación fue exitosa
    """
    sql = "DELETE FROM tipos_cancha WHERE id = %s;"
    return execute_query(conn, sql, (tipo_id,), fetch=False) is not None

def get_tipos_cancha_activos_db(conn):
    """
    Obtiene solo los tipos de cancha activos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de tipos de cancha activos
    """
    sql = """
    SELECT id, nombre, descripcion, precio_por_hora, estado, fecha_creacion, fecha_actualizacion
    FROM tipos_cancha 
    WHERE estado = 'Activo'
    ORDER BY nombre;
    """
    return execute_query_dict(conn, sql)

# ==================== CANCHAS ====================

def get_all_canchas_db(conn):
    """
    Obtiene todas las canchas de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de canchas
    """
    sql = """
        SELECT id, nombre, tipo_deporte, capacidad, precio_hora, estado, 
               horario_apertura, horario_cierre, descripcion, 
               fecha_creacion, fecha_actualizacion
        FROM canchas
        ORDER BY nombre
    """
    return execute_query_dict(conn, sql)

def get_cancha_by_id_db(conn, cancha_id):
    """
    Obtiene una cancha específica por su ID.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha
    
    Returns:
        dict: Datos de la cancha o None si no se encuentra
    """
    sql = """
        SELECT id, nombre, tipo_deporte, capacidad, precio_hora, estado, 
               horario_apertura, horario_cierre, descripcion, 
               fecha_creacion, fecha_actualizacion
        FROM canchas
        WHERE id = %s
    """
    result = execute_query_dict(conn, sql, (cancha_id,))
    return result[0] if result else None

def update_cancha_db(conn, cancha_id, nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion):
    """
    Actualiza una cancha existente.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha
        nombre (str): Nuevo nombre
        tipo_deporte (str): Nuevo tipo de deporte
        capacidad (int): Nueva capacidad
        precio_hora (float): Nuevo precio por hora
        estado (str): Nuevo estado
        horario_apertura (str): Nuevo horario de apertura
        horario_cierre (str): Nuevo horario de cierre
        descripcion (str): Nueva descripción
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    sql = """
        UPDATE canchas 
        SET nombre = %s, tipo_deporte = %s, capacidad = %s, precio_hora = %s, estado = %s, 
            horario_apertura = %s, horario_cierre = %s, descripcion = %s, fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    return execute_query_dict(conn, sql, (nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion, cancha_id))

def insert_cancha_db(conn, nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion):
    """
    Inserta una nueva cancha en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        nombre (str): Nombre de la cancha
        tipo_deporte (str): Tipo de deporte
        capacidad (int): Capacidad
        precio_hora (float): Precio por hora
        estado (str): Estado de la cancha
        horario_apertura (str): Horario de apertura
        horario_cierre (str): Horario de cierre
        descripcion (str): Descripción
    
    Returns:
        int: ID de la cancha insertada o None si hay error
    """
    sql = """
        INSERT INTO canchas (nombre, tipo_deporte, capacidad, precio_hora, estado, 
                           horario_apertura, horario_cierre, descripcion, 
                           fecha_creacion, fecha_actualizacion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id
    """
    result = execute_query_dict(conn, sql, (nombre, tipo_deporte, capacidad, precio_hora, estado, horario_apertura, horario_cierre, descripcion))
    return result[0]['id'] if result else None

def delete_cancha_db(conn, cancha_id):
    """
    Elimina una cancha de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha a eliminar
    
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    sql = "DELETE FROM canchas WHERE id = %s"
    return execute_query_dict(conn, sql, (cancha_id,))

def search_canchas_db(conn, search_term):
    """
    Busca canchas por término de búsqueda.
    
    Args:
        conn: Conexión a la base de datos
        search_term (str): Término de búsqueda
    
    Returns:
        list: Lista de canchas que coinciden con la búsqueda
    """
    sql = """
        SELECT id, nombre, tipo_deporte, capacidad, precio_hora, estado, 
               horario_apertura, horario_cierre, descripcion, 
               fecha_creacion, fecha_actualizacion
        FROM canchas
        WHERE nombre ILIKE %s OR tipo_deporte ILIKE %s OR descripcion ILIKE %s
        ORDER BY nombre
    """
    search_pattern = f"%{search_term}%"
    return execute_query_dict(conn, sql, (search_pattern, search_pattern, search_pattern))

def get_canchas_activas_db(conn):
    """
    Obtiene todas las canchas activas.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de canchas activas
    """
    sql = """
        SELECT id, nombre, tipo_deporte, capacidad, precio_hora, estado, 
               horario_apertura, horario_cierre, descripcion, 
               fecha_creacion, fecha_actualizacion
        FROM canchas
        WHERE estado = 'Activa'
        ORDER BY nombre
    """
    return execute_query_dict(conn, sql)

def get_canchas_por_tipo_db(conn, tipo_deporte):
    """
    Obtiene canchas por tipo de deporte.
    
    Args:
        conn: Conexión a la base de datos
        tipo_deporte (str): Tipo de deporte
    
    Returns:
        list: Lista de canchas del tipo especificado
    """
    sql = """
        SELECT id, nombre, tipo_deporte, capacidad, precio_hora, estado, 
               horario_apertura, horario_cierre, descripcion, 
               fecha_creacion, fecha_actualizacion
        FROM canchas
        WHERE tipo_deporte = %s AND estado = 'Activa'
        ORDER BY nombre
    """
    return execute_query_dict(conn, sql, (tipo_deporte,))

def get_canchas_disponibles_db(conn, fecha, hora_inicio, hora_fin):
    """
    Obtiene canchas disponibles para una fecha y horario específicos.
    
    Args:
        conn: Conexión a la base de datos
        fecha (str): Fecha de la reserva (YYYY-MM-DD)
        hora_inicio (str): Hora de inicio (HH:MM)
        hora_fin (str): Hora de fin (HH:MM)
    
    Returns:
        list: Lista de canchas disponibles
    """
    sql = """
        SELECT c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora, 
               c.estado, c.horario_apertura, c.horario_cierre, c.descripcion,
               c.fecha_creacion, c.fecha_actualizacion
        FROM canchas c
        WHERE c.estado = 'Activa'
        AND c.horario_apertura <= %s
        AND c.horario_cierre >= %s
        AND c.id NOT IN (
            SELECT DISTINCT r.cancha_id
            FROM reservas r
            WHERE r.fecha_reserva = %s
            AND r.estado IN ('Confirmada', 'Pendiente')
            AND (
                (r.hora_inicio < %s AND r.hora_fin > %s) OR
                (r.hora_inicio < %s AND r.hora_fin > %s) OR
                (r.hora_inicio >= %s AND r.hora_inicio < %s)
            )
        )
        ORDER BY c.nombre
    """
    return execute_query_dict(conn, sql, (hora_inicio, hora_fin, fecha, hora_fin, hora_inicio, hora_fin, hora_inicio, hora_inicio, hora_fin))

def update_cancha_estado_db(conn, cancha_id, estado):
    """
    Actualiza el estado de una cancha.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha
        estado (str): Nuevo estado
    
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    sql = """
        UPDATE canchas 
        SET estado = %s, fecha_actualizacion = CURRENT_TIMESTAMP
        WHERE id = %s
    """
    return execute_query_dict(conn, sql, (estado, cancha_id))

def get_estadisticas_canchas_db(conn):
    """
    Obtiene estadísticas de las canchas.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        dict: Estadísticas de canchas
    """
    sql = """
        SELECT 
            COUNT(*) as total_canchas,
            COUNT(CASE WHEN estado = 'Activa' THEN 1 END) as canchas_activas,
            COUNT(CASE WHEN estado = 'Inactiva' THEN 1 END) as canchas_inactivas,
            COUNT(CASE WHEN estado = 'Mantenimiento' THEN 1 END) as canchas_mantenimiento,
            COUNT(DISTINCT tipo_deporte) as tipos_deporte_unicos,
            AVG(precio_hora) as precio_promedio
        FROM canchas
    """
    result = execute_query_dict(conn, sql)
    return result[0] if result else {}

def get_canchas_por_precio_db(conn, precio_min=None, precio_max=None):
    """
    Obtiene canchas filtradas por rango de precio.
    
    Args:
        conn: Conexión a la base de datos
        precio_min (float): Precio mínimo (opcional)
        precio_max (float): Precio máximo (opcional)
    
    Returns:
        list: Lista de canchas en el rango de precio
    """
    where_clause = "WHERE estado = 'Activa'"
    params = []
    
    if precio_min is not None:
        where_clause += " AND precio_hora >= %s"
        params.append(precio_min)
    
    if precio_max is not None:
        where_clause += " AND precio_hora <= %s"
        params.append(precio_max)
    
    sql = f"""
        SELECT id, nombre, tipo_deporte, capacidad, precio_hora, estado, 
               horario_apertura, horario_cierre, descripcion, 
               fecha_creacion, fecha_actualizacion
        FROM canchas
        {where_clause}
        ORDER BY precio_hora, nombre
    """
    return execute_query_dict(conn, sql, params) 

def get_canchas_con_tipos_db(conn):
    """
    Obtiene todas las canchas con información de sus tipos usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        list: Lista de canchas con información de tipos
    """
    sql = """
        SELECT 
            c.id,
            c.nombre as nombre_cancha,
            c.descripcion as descripcion_cancha,
            c.capacidad,
            c.precio_hora,
            c.estado,
            c.tipo_deporte as tipo_cancha_nombre,
            c.descripcion as tipo_cancha_descripcion
        FROM canchas c
        ORDER BY c.nombre
    """
    
    try:
        return execute_query_dict(conn, sql)
    except Exception as e:
        st.error(f"Error al obtener canchas con tipos: {e}")
        return []

def get_canchas_db(conn):
    """
    Obtiene todas las canchas usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        list: Lista de canchas
    """
    sql = """
        SELECT c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora,
               c.estado, c.horario_apertura, c.horario_cierre, c.descripcion,
               c.fecha_creacion, c.fecha_actualizacion, c.tipo_cancha_id
        FROM canchas c
        ORDER BY c.nombre
    """
    
    try:
        return execute_query_dict(conn, sql)
    except Exception as e:
        st.error(f"Error al obtener canchas: {e}")
        return []

def get_tipos_cancha_db(conn):
    """
    Obtiene todos los tipos de cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        
    Returns:
        list: Lista de tipos de cancha
    """
    sql = """
        SELECT tc.id, tc.nombre, tc.descripcion, tc.precio_por_hora, 
               tc.estado, tc.fecha_creacion, tc.fecha_actualizacion
        FROM tipos_cancha tc
        ORDER BY tc.nombre
    """
    
    try:
        return execute_query_dict(conn, sql)
    except Exception as e:
        st.error(f"Error al obtener tipos de cancha: {e}")
        return []

def crear_cancha_db(conn, nombre, tipo_deporte, capacidad, precio_hora, estado, 
                   horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
    """
    Crea una nueva cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        nombre (str): Nombre de la cancha
        tipo_deporte (str): Tipo de deporte
        capacidad (int): Capacidad
        precio_hora (float): Precio por hora
        estado (str): Estado de la cancha
        horario_apertura (str): Horario de apertura
        horario_cierre (str): Horario de cierre
        descripcion (str): Descripción
        tipo_cancha_id (int): ID del tipo de cancha
        
    Returns:
        int: ID de la cancha creada o None si hay error
    """
    sql = """
    SELECT crear_cancha(%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, tipo_deporte, capacidad, precio_hora, estado,
                             horario_apertura, horario_cierre, descripcion, tipo_cancha_id))
            result = cur.fetchone()
            if result and result[0] is not None:
                nuevo_id = result[0]
                conn.commit()
                return nuevo_id
            else:
                st.error("Error: La función crear_cancha no retornó un ID válido")
                conn.rollback()
                return None
    except Exception as e:
        st.error(f"Error al crear cancha: {e}")
        conn.rollback()
        return None

def crear_tipo_cancha_db(conn, nombre, descripcion, precio_por_hora):
    """
    Crea un nuevo tipo de cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        nombre (str): Nombre del tipo de cancha
        descripcion (str): Descripción del tipo de cancha
        precio_por_hora (float): Precio por hora
        
    Returns:
        int: ID del tipo de cancha creado o None si hay error
    """
    sql = """
    SELECT crear_tipo_cancha(%s, %s, %s);
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, descripcion, precio_por_hora))
            result = cur.fetchone()
            if result and result[0] is not None:
                nuevo_id = result[0]
                conn.commit()
                return nuevo_id
            else:
                st.error("Error: La función crear_tipo_cancha no retornó un ID válido")
                conn.rollback()
                return None
    except Exception as e:
        st.error(f"Error al crear tipo de cancha: {e}")
        conn.rollback()
        return None

def actualizar_tipo_cancha_db(conn, tipo_id, nombre, descripcion, precio_por_hora, activo):
    """
    Actualiza un tipo de cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        tipo_id (int): ID del tipo de cancha
        nombre (str): Nuevo nombre
        descripcion (str): Nueva descripción
        precio_por_hora (float): Nuevo precio por hora
        activo (bool): Estado activo/inactivo
        
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    sql = "SELECT actualizar_tipo_cancha(%s, %s, %s, %s, %s);"
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (tipo_id, nombre, descripcion, precio_por_hora, activo))
            resultado = cur.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        st.error(f"Error al actualizar tipo de cancha: {e}")
        conn.rollback()
        return False

def actualizar_cancha_db(conn, cancha_id, nombre, tipo_deporte, capacidad, precio_hora, 
                        estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
    """
    Actualiza una cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha
        nombre (str): Nuevo nombre
        tipo_deporte (str): Nuevo tipo de deporte
        capacidad (int): Nueva capacidad
        precio_hora (float): Nuevo precio por hora
        estado (str): Nuevo estado
        horario_apertura (str): Nuevo horario de apertura
        horario_cierre (str): Nuevo horario de cierre
        descripcion (str): Nueva descripción
        tipo_cancha_id (int): ID del tipo de cancha
        
    Returns:
        bool: True si se actualizó correctamente, False en caso contrario
    """
    sql = """
    SELECT actualizar_cancha(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (cancha_id, nombre, tipo_deporte, capacidad, precio_hora,
                             estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id))
            resultado = cur.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        st.error(f"Error al actualizar cancha: {e}")
        conn.rollback()
        return False

def eliminar_tipo_cancha_db(conn, tipo_id):
    """
    Elimina un tipo de cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        tipo_id (int): ID del tipo de cancha a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    sql = "SELECT eliminar_tipo_cancha(%s);"
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (tipo_id,))
            resultado = cur.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        st.error(f"Error al eliminar tipo de cancha: {e}")
        conn.rollback()
        return False

def eliminar_cancha_db(conn, cancha_id):
    """
    Elimina una cancha usando la función SQL.
    
    Args:
        conn: Conexión a la base de datos
        cancha_id (int): ID de la cancha a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    sql = "SELECT eliminar_cancha(%s);"
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (cancha_id,))
            resultado = cur.fetchone()[0]
            conn.commit()
            return resultado
    except Exception as e:
        st.error(f"Error al eliminar cancha: {e}")
        conn.rollback()
        return False 