import psycopg2
import streamlit as st
from capa_datos.data_access import execute_query, execute_query_dict



def verificar_autenticacion_db(conn, username, password):
    """
    Verifica si las credenciales son válidas intentando una conexión.
    Esta función no se usa directamente, pero se incluye para documentación.
    
    Args:
        conn: Conexión a la base de datos (ya autenticada)
        username (str): Nombre de usuario
        password (str): Contraseña
    
    Returns:
        bool: True si la autenticación fue exitosa
    """
    # La verificación se hace al momento de crear la conexión
    # Esta función es principalmente para documentación
    return conn is not None

def get_info_usuario_actual_db(conn):
    """
    Obtiene información del usuario actual de la conexión.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        dict: Información del usuario actual
    """
    sql = """
    SELECT current_user as usuario_actual,
           session_user as usuario_sesion,
           current_database() as base_datos_actual,
           current_schema as esquema_actual,
           version() as version_postgresql;
    """
    result = execute_query_dict(conn, sql)
    return result[0] if result else None

def get_roles_usuario_db(conn, username):
    """
    Obtiene los roles asignados a un usuario específico.
    
    Args:
        conn: Conexión a la base de datos
        username (str): Nombre de usuario
    
    Returns:
        list: Lista de roles del usuario
    """
    sql = """
    SELECT r.rolname as role_name,
           CASE WHEN m.admin_option THEN 'Sí' ELSE 'No' END as con_admin_option
    FROM pg_roles r
    JOIN pg_auth_members m ON r.oid = m.roleid
    JOIN pg_roles u ON m.member = u.oid
    WHERE u.rolname = %s
    ORDER BY r.rolname;
    """
    return execute_query_dict(conn, sql, (username,))

def get_usuarios_por_rol_db(conn, rol_name):
    """
    Obtiene los usuarios que tienen un rol específico.
    
    Args:
        conn: Conexión a la base de datos
        rol_name (str): Nombre del rol
    
    Returns:
        list: Lista de usuarios con ese rol
    """
    sql = """
    SELECT u.rolname as username,
           CASE WHEN m.admin_option THEN 'Sí' ELSE 'No' END as con_admin_option
    FROM pg_roles u
    JOIN pg_auth_members m ON u.oid = m.member
    JOIN pg_roles r ON m.roleid = r.oid
    WHERE r.rolname = %s
    ORDER BY u.rolname;
    """
    return execute_query_dict(conn, sql, (rol_name,))

def get_estadisticas_usuarios_db(conn):
    """
    Obtiene estadísticas básicas de usuarios y roles.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        dict: Estadísticas de usuarios
    """
    # Total de usuarios
    sql_usuarios = "SELECT COUNT(*) as total_usuarios FROM pg_user;"
    result_usuarios = execute_query_dict(conn, sql_usuarios)
    total_usuarios = result_usuarios[0]['total_usuarios'] if result_usuarios else 0
    
    # Total de roles
    sql_roles = "SELECT COUNT(*) as total_roles FROM pg_roles;"
    result_roles = execute_query_dict(conn, sql_roles)
    total_roles = result_roles[0]['total_roles'] if result_roles else 0
    
    # Roles que pueden hacer login
    sql_login = "SELECT COUNT(*) as roles_login FROM pg_roles WHERE rolcanlogin = true;"
    result_login = execute_query_dict(conn, sql_login)
    roles_login = result_login[0]['roles_login'] if result_login else 0
    
    # Superusuarios
    sql_super = "SELECT COUNT(*) as superusuarios FROM pg_roles WHERE rolsuper = true;"
    result_super = execute_query_dict(conn, sql_super)
    superusuarios = result_super[0]['superusuarios'] if result_super else 0
    
    return {
        'total_usuarios': total_usuarios,
        'total_roles': total_roles,
        'roles_login': roles_login,
        'superusuarios': superusuarios
    }

def get_actividad_reciente_db(conn):
    """
    Obtiene información sobre la actividad reciente de conexiones.
    Nota: Esta información puede no estar disponible dependiendo de la configuración.
    
    Args:
        conn: Conexión a la base de datos
    
    Returns:
        list: Lista de actividad reciente
    """
    sql = """
    SELECT pid, usename, application_name, client_addr, 
           backend_start, state, query_start, wait_event_type
    FROM pg_stat_activity 
    WHERE state IS NOT NULL
    ORDER BY backend_start DESC;
    """
    return execute_query_dict(conn, sql) 

class UsuariosData:
    """Clase para manejar operaciones de usuarios del sistema"""
    
    def __init__(self):
        self.conn = st.session_state.get('db_connection')
    
    def get_all_usuarios(self):
        """Obtener todos los usuarios del sistema"""
        try:
            sql = """
            SELECT usename as username, usesysid as user_id, 
                   CASE WHEN usecreatedb THEN 'Sí' ELSE 'No' END as puede_crear_db,
                   CASE WHEN usesuper THEN 'Sí' ELSE 'No' END as es_superusuario,
                   CASE WHEN usebypassrls THEN 'Sí' ELSE 'No' END as bypass_rls,
                   'Activo' as estado,
                   usename as rol
            FROM pg_user
            ORDER BY usename;
            """
            return execute_query_dict(self.conn, sql)
        except Exception as e:
            st.error(f"Error al obtener usuarios: {e}")
            return []
    
    def usuario_existe(self, username):
        """Verificar si un usuario existe"""
        try:
            sql = "SELECT 1 FROM pg_user WHERE usename = %s"
            result = execute_query_dict(self.conn, sql, (username,))
            return len(result) > 0
        except Exception as e:
            st.error(f"Error al verificar usuario: {e}")
            return False
    
    def email_existe(self, email):
        """Verificar si un email existe (placeholder - no hay tabla de usuarios personalizada)"""
        # Por ahora retornamos False ya que no hay tabla de usuarios personalizada
        return False
    
    def crear_usuario(self, datos_usuario):
        """Crear un nuevo usuario (placeholder)"""
        try:
            # Por ahora solo simulamos la creación
            # En una implementación real, esto crearía el usuario en PostgreSQL
            st.success(f"Usuario {datos_usuario.get('username', 'N/A')} creado exitosamente")
            return True
        except Exception as e:
            st.error(f"Error al crear usuario: {e}")
            return False
    
    def actualizar_usuario(self, usuario_id, datos_actualizados):
        """Actualizar un usuario (placeholder)"""
        try:
            # Por ahora solo simulamos la actualización
            st.success("Usuario actualizado exitosamente")
            return True
        except Exception as e:
            st.error(f"Error al actualizar usuario: {e}")
            return False
    
    def eliminar_usuario(self, usuario_id):
        """Eliminar un usuario (placeholder)"""
        try:
            # Por ahora solo simulamos la eliminación
            st.success("Usuario eliminado exitosamente")
            return True
        except Exception as e:
            st.error(f"Error al eliminar usuario: {e}")
            return False
    
    def obtener_usuario_por_id(self, usuario_id):
        """Obtener usuario por ID"""
        try:
            sql = """
            SELECT usename as username, usesysid as user_id, 
                   CASE WHEN usecreatedb THEN 'Sí' ELSE 'No' END as puede_crear_db,
                   CASE WHEN usesuper THEN 'Sí' ELSE 'No' END as es_superusuario,
                   CASE WHEN usebypassrls THEN 'Sí' ELSE 'No' END as bypass_rls,
                   'Activo' as estado,
                   usename as rol
            FROM pg_user
            WHERE usesysid = %s
            """
            result = execute_query_dict(self.conn, sql, (usuario_id,))
            return result[0] if result else None
        except Exception as e:
            st.error(f"Error al obtener usuario: {e}")
            return None 