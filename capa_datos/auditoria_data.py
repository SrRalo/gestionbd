"""
Capa de datos para la tabla auditoria
"""
from capa_datos.data_access import execute_query_dict, execute_query
from capa_datos.database_connection import get_db_connection
import streamlit as st

def registrar_accion_auditoria(usuario_id, tipo_accion, tabla, registro_id, detalles, resultado="SUCCESS"):
    """
    Registra manualmente una acción en la tabla auditoría
    
    Args:
        usuario_id (int): ID del usuario que realiza la acción
        tipo_accion (str): Tipo de acción (INSERT, UPDATE, DELETE, etc.)
        tabla (str): Nombre de la tabla afectada
        registro_id (int): ID del registro afectado
        detalles (str): Descripción de la acción
        resultado (str): Resultado de la acción (SUCCESS, ERROR, etc.)
    
    Returns:
        bool: True si se registró correctamente, False en caso contrario
    """
    try:
        conn = get_db_connection()
        if not conn:
            return False
            
        query = """
        INSERT INTO auditoria (
            usuario_id,
            tipo_accion,
            tabla,
            registro_id,
            detalles,
            resultado,
            ip_address,
            fecha_hora
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        )
        """
        
        # IP address simulado (en producción se obtendría del request)
        ip_address = "127.0.0.1"
        
        result = execute_query(conn, query, (usuario_id, tipo_accion, tabla, registro_id, detalles, resultado, ip_address), fetch=False)
        conn.close()
        
        return result is not None
    except Exception as e:
        st.error(f"Error al registrar acción en auditoría: {e}")
        return False

def get_auditoria_db():
    """
    Obtiene todos los registros de auditoría ordenados por fecha más reciente
    
    Returns:
        list: Lista de diccionarios con los registros de auditoría
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        query = """
        SELECT 
            a.id,
            a.usuario_id,
            u.nombre as usuario_nombre,
            a.tipo_accion,
            a.tabla,
            a.registro_id,
            a.detalles,
            a.resultado,
            a.ip_address,
            a.fecha_hora
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        ORDER BY a.fecha_hora DESC
        """
        result = execute_query_dict(conn, query)
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener auditoría: {e}")
        return []

def get_auditoria_por_fecha_db(fecha_inicio, fecha_fin):
    """
    Obtiene registros de auditoría por rango de fechas
    
    Args:
        fecha_inicio (str): Fecha de inicio en formato YYYY-MM-DD
        fecha_fin (str): Fecha de fin en formato YYYY-MM-DD
    
    Returns:
        list: Lista de diccionarios con los registros filtrados
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        query = """
        SELECT 
            a.id,
            a.usuario_id,
            u.nombre as usuario_nombre,
            a.tipo_accion,
            a.tabla,
            a.registro_id,
            a.detalles,
            a.resultado,
            a.ip_address,
            a.fecha_hora
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        WHERE DATE(a.fecha_hora) BETWEEN %s AND %s
        ORDER BY a.fecha_hora DESC
        """
        result = execute_query_dict(conn, query, (fecha_inicio, fecha_fin))
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener auditoría por fecha: {e}")
        return []

def get_auditoria_por_usuario_db(usuario_id):
    """
    Obtiene registros de auditoría por usuario
    
    Args:
        usuario_id (int): ID del usuario
    
    Returns:
        list: Lista de diccionarios con los registros del usuario
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        query = """
        SELECT 
            a.id,
            a.usuario_id,
            u.nombre as usuario_nombre,
            a.tipo_accion,
            a.tabla,
            a.registro_id,
            a.detalles,
            a.resultado,
            a.ip_address,
            a.fecha_hora
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.usuario_id = %s
        ORDER BY a.fecha_hora DESC
        """
        result = execute_query_dict(conn, query, (usuario_id,))
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener auditoría por usuario: {e}")
        return []

def get_auditoria_por_tabla_db(tabla):
    """
    Obtiene registros de auditoría por tabla
    
    Args:
        tabla (str): Nombre de la tabla
    
    Returns:
        list: Lista de diccionarios con los registros de la tabla
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        query = """
        SELECT 
            a.id,
            a.usuario_id,
            u.nombre as usuario_nombre,
            a.tipo_accion,
            a.tabla,
            a.registro_id,
            a.detalles,
            a.resultado,
            a.ip_address,
            a.fecha_hora
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.tabla = %s
        ORDER BY a.fecha_hora DESC
        """
        result = execute_query_dict(conn, query, (tabla,))
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener auditoría por tabla: {e}")
        return []

def get_auditoria_por_tipo_accion_db(tipo_accion):
    """
    Obtiene registros de auditoría por tipo de acción
    
    Args:
        tipo_accion (str): Tipo de acción (INSERT, UPDATE, DELETE, etc.)
    
    Returns:
        list: Lista de diccionarios con los registros del tipo de acción
    """
    try:
        conn = get_db_connection()
        if not conn:
            return []
            
        query = """
        SELECT 
            a.id,
            a.usuario_id,
            u.nombre as usuario_nombre,
            a.tipo_accion,
            a.tabla,
            a.registro_id,
            a.detalles,
            a.resultado,
            a.ip_address,
            a.fecha_hora
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        WHERE a.tipo_accion = %s
        ORDER BY a.fecha_hora DESC
        """
        result = execute_query_dict(conn, query, (tipo_accion,))
        conn.close()
        return result
    except Exception as e:
        st.error(f"Error al obtener auditoría por tipo de acción: {e}")
        return []

def get_estadisticas_auditoria_db():
    """
    Obtiene estadísticas de auditoría
    
    Returns:
        dict: Diccionario con estadísticas
    """
    try:
        conn = get_db_connection()
        if not conn:
            return {
                'total': 0,
                'acciones': [],
                'tablas': [],
                'usuarios': [],
                'dias': []
            }
        
        # Total de registros
        total_query = "SELECT COUNT(*) as total FROM auditoria"
        total_result = execute_query_dict(conn, total_query)
        total = total_result[0]['total'] if total_result else 0
        
        # Registros por tipo de acción
        acciones_query = """
        SELECT tipo_accion, COUNT(*) as cantidad
        FROM auditoria
        GROUP BY tipo_accion
        ORDER BY cantidad DESC
        """
        acciones = execute_query_dict(conn, acciones_query)
        
        # Registros por tabla
        tablas_query = """
        SELECT tabla, COUNT(*) as cantidad
        FROM auditoria
        GROUP BY tabla
        ORDER BY cantidad DESC
        """
        tablas = execute_query_dict(conn, tablas_query)
        
        # Registros por usuario
        usuarios_query = """
        SELECT u.nombre as usuario_nombre, COUNT(*) as cantidad
        FROM auditoria a
        LEFT JOIN usuarios u ON a.usuario_id = u.id
        GROUP BY u.id, u.nombre
        ORDER BY cantidad DESC
        LIMIT 10
        """
        usuarios = execute_query_dict(conn, usuarios_query)
        
        # Registros por día (últimos 7 días)
        dias_query = """
        SELECT DATE(fecha_hora) as fecha, COUNT(*) as cantidad
        FROM auditoria
        WHERE fecha_hora >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(fecha_hora)
        ORDER BY fecha DESC
        """
        dias = execute_query_dict(conn, dias_query)
        
        conn.close()
        
        return {
            'total': total,
            'acciones': acciones,
            'tablas': tablas,
            'usuarios': usuarios,
            'dias': dias
        }
    except Exception as e:
        st.error(f"Error al obtener estadísticas de auditoría: {e}")
        return {
            'total': 0,
            'acciones': [],
            'tablas': [],
            'usuarios': [],
            'dias': []
        } 