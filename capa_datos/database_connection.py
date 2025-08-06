import psycopg2
import streamlit as st
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from config.database_settings import get_database_config, get_connection_info

# Cargar variables de entorno
load_dotenv()

def get_connection(user, password, host="localhost", port="5432", dbname="postgres"):
    """
    Establece una conexión a la base de datos PostgreSQL.
    
    Args:
        user (str): Nombre de usuario
        password (str): Contraseña del usuario
        host (str): Host de la base de datos
        port (str): Puerto de la base de datos
        dbname (str): Nombre de la base de datos
    
    Returns:
        psycopg2.connection: Conexión a la base de datos o None si hay error
    """
    try:
        # Configuración de conexión con soporte para IPv6 y codificación mejorada
        conn_params = {
            'host': host,
            'port': port,
            'database': dbname,
            'user': user,
            'password': password,
            'client_encoding': 'UTF8',
            'options': '-c client_encoding=UTF8'
        }
        
        # Si es un host remoto (no localhost), agregar configuración adicional
        if host != 'localhost':
            conn_params['connect_timeout'] = 10
            conn_params['application_name'] = 'sportcourt_app'
            # Configuración para manejar IPv6
            conn_params['keepalives_idle'] = 60
            conn_params['keepalives_interval'] = 10
            conn_params['keepalives_count'] = 5
        
        conn = psycopg2.connect(**conn_params)
        return conn
    except psycopg2.Error as e:
        st.error(f"Error inesperado al conectar a PostgreSQL: {e}")
        return None

def get_connection_dict(user, password, host="localhost", port="5432", dbname="postgres"):
    """
    Establece una conexión a la base de datos PostgreSQL con cursor de diccionarios.
    
    Args:
        user (str): Nombre de usuario
        password (str): Contraseña del usuario
        host (str): Host de la base de datos
        port (str): Puerto de la base de datos
        dbname (str): Nombre de la base de datos
    
    Returns:
        tuple: (conexión, cursor) o (None, None) si hay error
    """
    try:
        conn_params = {
            'host': host,
            'port': port,
            'database': dbname,
            'user': user,
            'password': password,
            'client_encoding': 'UTF8',
            'options': '-c client_encoding=UTF8'
        }
        
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cur
    except psycopg2.Error as e:
        st.error(f"Error inesperado al conectar a PostgreSQL: {e}")
        return None, None

def close_connection(conn):
    """
    Cierra la conexión a la base de datos de forma segura.
    
    Args:
        conn: Objeto de conexión a cerrar
    """
    if conn:
        try:
            conn.close()
        except Exception as e:
            st.warning(f"Error al cerrar conexión: {e}")

def test_connection(conn):
    """
    Prueba si la conexión está activa.
    
    Args:
        conn: Objeto de conexión a probar
    
    Returns:
        bool: True si la conexión está activa, False en caso contrario
    """
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            return True
    except psycopg2.Error:
        return False

def get_db_connection():
    """
    Obtiene una conexión a la base de datos usando la configuración actual.
    
    Returns:
        psycopg2.connection: Conexión a la base de datos o None si hay error
    """
    try:
        # Obtener configuración actual
        config = get_database_config()
        
        # Crear conexión
        conn = get_connection(
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port'],
            dbname=config['database']
        )
        
        if conn:
            st.info(f"🔗 Conectado a: {get_connection_info()}")
            return conn
        else:
            st.error("❌ No se pudo establecer conexión a la base de datos")
            return None
            
    except Exception as e:
        st.error(f"Error al conectar a la base de datos: {e}")
        return None

def reset_connection_if_needed(conn, username=None, password=None, host=None, port=None, dbname=None):
    """
    Verifica si una conexión está en mal estado y la reinicia si es necesario.
    
    Args:
        conn: Conexión actual a verificar
        username (str): Nombre de usuario para reconectar (opcional)
        password (str): Contraseña para reconectar (opcional)
        host (str): Host de la base de datos (opcional)
        port (str): Puerto de la base de datos (opcional)
        dbname (str): Nombre de la base de datos (opcional)
    
    Returns:
        psycopg2.connection: Nueva conexión si fue necesario reiniciar, o la misma si está bien
    """
    try:
        # Obtener configuración actual si no se proporcionan parámetros
        config = get_database_config()
        if username is None:
            username = config['user']
        if password is None:
            password = config['password']
        if host is None:
            host = config['host']
        if port is None:
            port = config['port']
        if dbname is None:
            dbname = config['database']
        
        # Verificar si la conexión está activa
        if conn and test_connection(conn):
            return conn
        
        # Si la conexión no está activa, cerrarla y crear una nueva
        if conn:
            try:
                conn.close()
            except:
                pass
        
        # Crear nueva conexión
        new_conn = get_connection(username, password, host, port, dbname)
        if new_conn:
            st.success("✅ Conexión a la base de datos reiniciada correctamente")
            return new_conn
        else:
            st.error("❌ No se pudo reiniciar la conexión a la base de datos")
            return None
            
    except Exception as e:
        st.error(f"Error al reiniciar conexión: {e}")
        return None 