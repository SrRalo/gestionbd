import psycopg2
import streamlit as st
from capa_datos.data_access import call_procedure

def validar_datos_db(conn, tabla):
    """
    Valida los datos de una tabla usando el procedimiento almacenado.
    
    Args:
        conn: Conexión a la base de datos
        tabla (str): Nombre de la tabla a validar
    
    Returns:
        bool: True si la validación se ejecutó correctamente, False en caso contrario
    """
    try:
        # Llamar al procedimiento almacenado
        success = call_procedure(conn, 'proc_validar_y_limpiar_datos', (tabla, 'VALIDATE'))
        
        if success:
            st.success(f"✅ Validación de datos en tabla '{tabla}' completada")
            return True
        else:
            st.error(f"❌ Error al validar datos en tabla '{tabla}'")
            return False
            
    except Exception as e:
        st.error(f"Error al validar datos: {e}")
        return False

def limpiar_datos_db(conn, tabla):
    """
    Limpia los datos de una tabla usando el procedimiento almacenado.
    
    Args:
        conn: Conexión a la base de datos
        tabla (str): Nombre de la tabla a limpiar
    
    Returns:
        bool: True si la limpieza se ejecutó correctamente, False en caso contrario
    """
    try:
        # Llamar al procedimiento almacenado
        success = call_procedure(conn, 'proc_validar_y_limpiar_datos', (tabla, 'CLEAN'))
        
        if success:
            st.success(f"✅ Limpieza de datos en tabla '{tabla}' completada")
            return True
        else:
            st.error(f"❌ Error al limpiar datos en tabla '{tabla}'")
            return False
            
    except Exception as e:
        st.error(f"Error al limpiar datos: {e}")
        return False

def crear_backup_db(conn, tabla):
    """
    Crea un backup de una tabla usando el procedimiento almacenado.
    
    Args:
        conn: Conexión a la base de datos
        tabla (str): Nombre de la tabla para crear backup
    
    Returns:
        bool: True si el backup se creó correctamente, False en caso contrario
    """
    try:
        # Llamar al procedimiento almacenado
        success = call_procedure(conn, 'proc_validar_y_limpiar_datos', (tabla, 'BACKUP'))
        
        if success:
            st.success(f"✅ Backup de tabla '{tabla}' creado correctamente")
            return True
        else:
            st.error(f"❌ Error al crear backup de tabla '{tabla}'")
            return False
            
    except Exception as e:
        st.error(f"Error al crear backup: {e}")
        return False

def validar_todas_las_tablas_db(conn):
    """
    Valida todas las tablas principales del sistema.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        dict: Diccionario con el resultado de validación de cada tabla
    """
    tablas = ['clientes', 'canchas', 'reservas', 'pagos', 'usuarios']
    resultados = {}
    
    for tabla in tablas:
        resultados[tabla] = validar_datos_db(conn, tabla)
    
    return resultados

def limpiar_todas_las_tablas_db(conn):
    """
    Limpia todas las tablas principales del sistema.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        dict: Diccionario con el resultado de limpieza de cada tabla
    """
    tablas = ['clientes', 'canchas', 'reservas', 'pagos', 'usuarios']
    resultados = {}
    
    for tabla in tablas:
        resultados[tabla] = limpiar_datos_db(conn, tabla)
    
    return resultados

def crear_backup_todas_las_tablas_db(conn):
    """
    Crea backup de todas las tablas principales del sistema.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        dict: Diccionario con el resultado de backup de cada tabla
    """
    tablas = ['clientes', 'canchas', 'reservas', 'pagos', 'usuarios']
    resultados = {}
    
    for tabla in tablas:
        resultados[tabla] = crear_backup_db(conn, tabla)
    
    return resultados 