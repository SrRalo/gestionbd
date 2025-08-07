import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor

def reset_transaction(conn):
    """
    Reinicia una transacción abortada.
    
    Args:
        conn: Conexión a la base de datos
    """
    try:
        # Verificar que la conexión existe
        if conn is None:
            return False
        
        # Intentar hacer rollback para limpiar la transacción abortada
        conn.rollback()
    except psycopg2.Error:
        # Si el rollback falla, intentar hacer commit para forzar un nuevo estado
        try:
            if conn is not None:
                conn.commit()
        except psycopg2.Error:
            # Si ambos fallan, la conexión está en mal estado
            return False
    except Exception:
        # Si hay cualquier otro error, la conexión está en mal estado
        return False
    return True

def execute_query(conn, sql, params=None, fetch=True):
    """
    Ejecuta una consulta SQL genérica.
    
    Args:
        conn: Conexión a la base de datos
        sql (str): Consulta SQL a ejecutar
        params (tuple): Parámetros para la consulta
        fetch (bool): Si debe hacer fetch de los resultados
    
    Returns:
        list: Resultados de la consulta o None si hay error
    """
    try:
        # Verificar que la conexión existe
        if conn is None:
            st.error("❌ Error: No hay conexión a la base de datos")
            return None
        
        # Verificar si la transacción está abortada y reiniciarla
        if hasattr(conn, 'status') and conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            reset_transaction(conn)
        
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()
            else:
                conn.commit()
                return cur.rowcount
    except psycopg2.Error as e:
        st.error(f"Error en consulta SQL: {e}")
        # Intentar reiniciar la transacción después del error
        if conn is not None:
            reset_transaction(conn)
        return None
    except Exception as e:
        st.error(f"Error inesperado en consulta SQL: {e}")
        return None

def execute_query_dict(conn, sql, params=None):
    """
    Ejecuta una consulta SQL y retorna resultados como diccionarios.
    
    Args:
        conn: Conexión a la base de datos
        sql (str): Consulta SQL a ejecutar
        params (tuple): Parámetros para la consulta
    
    Returns:
        list: Lista de diccionarios con los resultados
    """
    try:
        # Verificar que la conexión existe
        if conn is None:
            st.error("❌ Error: No hay conexión a la base de datos")
            return []
        
        # Verificar si la transacción está abortada y reiniciarla
        if hasattr(conn, 'status') and conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            reset_transaction(conn)
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    except psycopg2.Error as e:
        st.error(f"Error en consulta SQL: {e}")
        # Intentar reiniciar la transacción después del error
        if conn is not None:
            reset_transaction(conn)
        return []
    except Exception as e:
        st.error(f"Error inesperado en consulta SQL: {e}")
        return []

def execute_transaction(conn, queries):
    """
    Ejecuta múltiples consultas en una transacción.
    
    Args:
        conn: Conexión a la base de datos
        queries (list): Lista de tuplas (sql, params) a ejecutar
    
    Returns:
        bool: True si la transacción fue exitosa, False en caso contrario
    """
    try:
        # Verificar que la conexión existe
        if conn is None:
            st.error("❌ Error: No hay conexión a la base de datos")
            return False
        
        # Verificar si la transacción está abortada y reiniciarla
        if hasattr(conn, 'status') and conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            reset_transaction(conn)
        
        with conn.cursor() as cur:
            for sql, params in queries:
                cur.execute(sql, params)
            conn.commit()
            return True
    except psycopg2.Error as e:
        st.error(f"Error en transacción: {e}")
        if conn is not None:
            conn.rollback()
        return False
    except Exception as e:
        st.error(f"Error inesperado en transacción: {e}")
        return False

def call_function(conn, function_name, params=None):
    """
    Llama a una función almacenada de PostgreSQL.
    
    Args:
        conn: Conexión a la base de datos
        function_name (str): Nombre de la función a llamar
        params (tuple): Parámetros para la función
    
    Returns:
        tuple: Resultado de la función o None si hay error
    """
    try:
        # Verificar que la conexión existe
        if conn is None:
            st.error("❌ Error: No hay conexión a la base de datos")
            return None
        
        # Verificar si la transacción está abortada y reiniciarla
        if hasattr(conn, 'status') and conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            reset_transaction(conn)
        
        with conn.cursor() as cur:
            if params:
                cur.callproc(function_name, params)
            else:
                cur.callproc(function_name)
            result = cur.fetchone()
            conn.commit()
            return result
    except psycopg2.Error as e:
        st.error(f"Error al llamar función {function_name}: {e}")
        if conn is not None:
            conn.rollback()
        return None
    except Exception as e:
        st.error(f"Error inesperado al llamar función {function_name}: {e}")
        return None

def call_procedure(conn, procedure_name, params=None):
    """
    Llama a un procedimiento almacenado de PostgreSQL.
    
    Args:
        conn: Conexión a la base de datos
        procedure_name (str): Nombre del procedimiento a llamar
        params (tuple): Parámetros para el procedimiento
    
    Returns:
        bool: True si el procedimiento se ejecutó correctamente
    """
    try:
        # Verificar que la conexión existe
        if conn is None:
            st.error("❌ Error: No hay conexión a la base de datos")
            return False
        
        # Verificar si la transacción está abortada y reiniciarla
        if hasattr(conn, 'status') and conn.status == psycopg2.extensions.STATUS_IN_TRANSACTION:
            reset_transaction(conn)
        
        with conn.cursor() as cur:
            # Construir la llamada CALL con parámetros
            if params:
                # Crear placeholders para los parámetros
                placeholders = ', '.join(['%s'] * len(params))
                call_sql = f"CALL {procedure_name}({placeholders})"
                cur.execute(call_sql, params)
            else:
                call_sql = f"CALL {procedure_name}()"
                cur.execute(call_sql)
            
            # No hacer commit aquí, dejar que la función llamadora maneje la transacción
            return True
    except psycopg2.Error as e:
        st.error(f"Error al llamar procedimiento {procedure_name}: {e}")
        # No hacer rollback aquí, dejar que la función llamadora maneje la transacción
        return False
    except Exception as e:
        st.error(f"Error inesperado al llamar procedimiento {procedure_name}: {e}")
        return False 