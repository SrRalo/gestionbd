import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict

def insert_cliente_db(conn, nombre, apellido, telefono, email, fecha_nacimiento):
    """
    Inserta un nuevo cliente en la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        nombre (str): Nombre del cliente
        apellido (str): Apellido del cliente
        telefono (str): Teléfono del cliente
        email (str): Email del cliente
        fecha_nacimiento (date): Fecha de nacimiento
    
    Returns:
        int: ID del cliente insertado o None si hay error
    """
    sql = """
    INSERT INTO clientes (nombre, apellido, telefono, email, fecha_nacimiento)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id;
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (nombre, apellido, telefono, email, fecha_nacimiento))
            cliente_id = cur.fetchone()[0]
            conn.commit()
            return cliente_id
    except psycopg2.Error as e:
        st.error(f"Error al insertar cliente: {e}")
        conn.rollback()
        return None

def get_clientes_db(conn):
    """
    Obtiene todos los clientes de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de clientes
    """
    sql = """
    SELECT id, nombre, apellido, telefono, email, 
           fecha_nacimiento, estado, fecha_registro, fecha_actualizacion
    FROM clientes 
    ORDER BY nombre, apellido;
    """
    return execute_query_dict(conn, sql)

def get_cliente_by_id_db(conn, cliente_id):
    """
    Obtiene un cliente específico por su ID.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente
    
    Returns:
        dict: Datos del cliente o None si no existe
    """
    sql = """
    SELECT id, nombre, apellido, telefono, email, 
           fecha_nacimiento, estado, fecha_registro, fecha_actualizacion
    FROM clientes 
    WHERE id = %s;
    """
    result = execute_query_dict(conn, sql, (cliente_id,))
    return result[0] if result else None

def update_cliente_db(conn, cliente_id, nombre, apellido, telefono, email, fecha_nacimiento, estado):
    """
    Actualiza los datos de un cliente.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente a actualizar
        nombre (str): Nuevo nombre
        apellido (str): Nuevo apellido
        telefono (str): Nuevo teléfono
        email (str): Nuevo email
        fecha_nacimiento (date): Nueva fecha de nacimiento
        estado (str): Estado del cliente (Activo/Inactivo)
    
    Returns:
        bool: True si la actualización fue exitosa
    """
    sql = """
    UPDATE clientes 
    SET nombre = %s, apellido = %s, telefono = %s, email = %s, 
        fecha_nacimiento = %s, estado = %s, fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE id = %s;
    """
    return execute_query(conn, sql, (nombre, apellido, telefono, email, fecha_nacimiento, estado, cliente_id), fetch=False) is not None

def delete_cliente_db(conn, cliente_id):
    """
    Elimina un cliente de la base de datos.
    
    Args:
        conn: Conexión a la base de datos
        cliente_id (int): ID del cliente a eliminar
    
    Returns:
        bool: True si la eliminación fue exitosa
    """
    sql = "DELETE FROM clientes WHERE id = %s;"
    return execute_query(conn, sql, (cliente_id,), fetch=False) is not None

def search_clientes_db(conn, search_term):
    """
    Busca clientes por nombre, apellido o email.
    
    Args:
        conn: Conexión a la base de datos
        search_term (str): Término de búsqueda
    
    Returns:
        list: Lista de clientes que coinciden con la búsqueda
    """
    sql = """
    SELECT id, nombre, apellido, telefono, email, 
           fecha_nacimiento, estado, fecha_registro, fecha_actualizacion
    FROM clientes 
    WHERE LOWER(nombre) LIKE LOWER(%s) 
       OR LOWER(apellido) LIKE LOWER(%s) 
       OR LOWER(email) LIKE LOWER(%s)
    ORDER BY nombre, apellido;
    """
    search_pattern = f"%{search_term}%"
    return execute_query_dict(conn, sql, (search_pattern, search_pattern, search_pattern))

def get_clientes_activos_db(conn):
    """
    Obtiene solo los clientes activos.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de clientes activos
    """
    sql = """
    SELECT id, nombre, apellido, telefono, email, 
           fecha_nacimiento, estado, fecha_registro, fecha_actualizacion
    FROM clientes 
    WHERE estado = 'Activo'
    ORDER BY nombre, apellido;
    """
    return execute_query_dict(conn, sql) 