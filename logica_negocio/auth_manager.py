import streamlit as st
import os
from dotenv import load_dotenv
from capa_datos.database_connection import get_connection, test_connection, reset_connection_if_needed
from capa_datos.usuarios_data import get_info_usuario_actual_db, get_roles_usuario_db

# Cargar variables de entorno
load_dotenv()

class AuthManager:
    """
    Gestor de autenticación que maneja la lógica de autenticación y roles.
    """
    
    def __init__(self):
        self.roles_permitidos = [
            'admin_reservas',
            'operador_reservas', 
            'consultor_reservas'
        ]
    
    def autenticar_usuario(self, username, password, host=None, port=None, dbname=None):
        """
        Autentica un usuario intentando conectarse a la base de datos.
        
        Args:
            username (str): Nombre de usuario/rol
            password (str): Contraseña del usuario
            host (str): Host de la base de datos (opcional, usa .env por defecto)
            port (str): Puerto de la base de datos (opcional, usa .env por defecto)
            dbname (str): Nombre de la base de datos (opcional, usa .env por defecto)
        
        Returns:
            dict: Información de autenticación o None si falla
        """
        try:
            # Usar configuración del archivo .env si no se proporcionan parámetros
            if host is None:
                host = os.getenv('DB_HOST', 'localhost')
            if port is None:
                port = os.getenv('DB_PORT', '5432')
            if dbname is None:
                dbname = os.getenv('DB_NAME', 'sportcourt_reservations')
            
            # Intentar conectar con las credenciales proporcionadas
            conn = get_connection(username, password, host, port, dbname)
            
            if not conn:
                return None
            
            # Verificar que la conexión esté activa
            if not test_connection(conn):
                conn.close()
                return None
            
            # Obtener información del usuario actual
            info_usuario = get_info_usuario_actual_db(conn)
            if not info_usuario:
                conn.close()
                return None
            
            # Verificar que el rol esté en la lista de roles permitidos
            rol_actual = info_usuario['usuario_actual']
            if rol_actual not in self.roles_permitidos:
                st.warning(f"El rol '{rol_actual}' no tiene permisos para acceder al sistema.")
                conn.close()
                return None
            
            # Obtener roles adicionales del usuario
            roles_usuario = get_roles_usuario_db(conn, username)
            
            return {
                'success': True,
                'username': username,
                'rol_principal': rol_actual,
                'roles': [r['role_name'] for r in roles_usuario],
                'connection': conn,
                'info_usuario': info_usuario
            }
            
        except Exception as e:
            st.error(f"Error durante la autenticación: {e}")
            return None
    
    def verificar_permiso(self, rol_usuario, operacion, entidad=None):
        """
        Verifica si un usuario tiene permisos para realizar una operación.
        
        Args:
            rol_usuario (str): Rol del usuario
            operacion (str): Operación a realizar (crear, leer, actualizar, eliminar)
            entidad (str): Entidad sobre la que se realiza la operación (opcional)
        
        Returns:
            bool: True si tiene permisos, False en caso contrario
        """
        # Definir permisos por rol
        permisos = {
            'admin_reservas': {
                'clientes': ['crear', 'leer', 'actualizar', 'eliminar'],
                'reservas': ['crear', 'leer', 'actualizar', 'eliminar'],
                'canchas': ['crear', 'leer', 'actualizar', 'eliminar'],
                'pagos': ['crear', 'leer', 'actualizar', 'eliminar'],
                'reportes': ['leer'],
                'usuarios': ['crear', 'leer', 'actualizar', 'eliminar'],
                'auditoria': ['leer']
            },
            'operador_reservas': {
                'clientes': ['crear', 'leer', 'actualizar'],
                'reservas': ['crear', 'leer', 'actualizar'],
                'canchas': ['leer'],
                'pagos': ['crear', 'leer', 'actualizar'],
                'reportes': ['leer'],
                'usuarios': ['leer'],
                'auditoria': ['leer']
            },
            'consultor_reservas': {
                'clientes': ['leer'],
                'reservas': ['leer'],
                'canchas': ['leer'],
                'pagos': ['leer'],
                'reportes': ['leer'],
                'usuarios': ['leer'],
                'auditoria': ['leer']
            }
        }
        
        # Verificar si el rol tiene permisos para la entidad
        if rol_usuario not in permisos:
            return False
        
        if entidad and entidad not in permisos[rol_usuario]:
            return False
        
        # Si no se especifica entidad, verificar si tiene algún permiso
        if not entidad:
            return True
        
        # Verificar si tiene el permiso específico
        return operacion in permisos[rol_usuario][entidad]
    
    def obtener_menu_por_rol(self, rol_usuario):
        """
        Obtiene las opciones de menú disponibles para un rol específico.
        
        Args:
            rol_usuario (str): Rol del usuario
        
        Returns:
            dict: Diccionario con las opciones de menú disponibles
        """
        menu_completo = {
            'dashboard': '📊 Dashboard',
            'clientes': '👥 Clientes',
            'reservas': '📅 Reservas',
            'canchas': '⚽ Canchas',
            'pagos': '💰 Pagos',
            'reportes': '📈 Reportes',
            'usuarios': '👤 Usuarios',
            'auditoria': '📋 Auditoría',
            'perfil': '👤 Mi Perfil'
        }
        
        # Definir qué opciones puede ver cada rol
        permisos_menu = {
            'admin_reservas': list(menu_completo.keys()),  # Acceso completo
            'operador_reservas': ['dashboard', 'clientes', 'reservas', 'canchas', 'pagos', 'reportes', 'perfil'],
            'consultor_reservas': ['dashboard', 'clientes', 'reservas', 'canchas', 'pagos', 'reportes', 'perfil']
        }
        
        # Filtrar opciones según el rol
        opciones_permitidas = permisos_menu.get(rol_usuario, [])
        return {k: v for k, v in menu_completo.items() if k in opciones_permitidas}
    
    def cerrar_sesion(self):
        """
        Cierra la sesión del usuario y limpia las variables de sesión.
        """
        try:
            # Cerrar conexión a la base de datos
            if 'db_connection' in st.session_state and st.session_state['db_connection']:
                try:
                    st.session_state['db_connection'].close()
                except:
                    pass
                del st.session_state['db_connection']
            
            # Limpiar variables de sesión
            keys_to_remove = [
                'authenticated', 'username', 'user_role', 'db_connection',
                'user_info', 'user_roles', 'session_info'
            ]
            
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("✅ Sesión cerrada correctamente")
            
        except Exception as e:
            st.error(f"Error al cerrar sesión: {e}")
    
    def obtener_info_sesion(self):
        """
        Obtiene información de la sesión actual.
        
        Returns:
            dict: Información de la sesión o None si no hay sesión activa
        """
        if not self.verificar_sesion_activa():
            return None
        
        return {
            'username': st.session_state.get('username'),
            'user_role': st.session_state.get('user_role'),
            'authenticated': st.session_state.get('authenticated', False)
        }
    
    def verificar_sesion_activa(self):
        """
        Verifica si hay una sesión activa y la conexión está funcionando.
        
        Returns:
            bool: True si la sesión está activa, False en caso contrario
        """
        # Verificar si está autenticado
        if not st.session_state.get('authenticated', False):
            return False
        
        # Verificar conexión a la base de datos
        conn = st.session_state.get('db_connection')
        if not conn or not test_connection(conn):
            # Intentar reiniciar la conexión
            username = st.session_state.get('username')
            password = st.session_state.get('password', '')  # Asumiendo que se guarda la contraseña
            
            if username and password:
                new_conn = reset_connection_if_needed(conn, username, password)
                if new_conn:
                    st.session_state['db_connection'] = new_conn
                    return True
                else:
                    # Si no se puede reconectar, cerrar sesión
                    self.cerrar_sesion()
                    return False
            else:
                # Si no hay credenciales, cerrar sesión
                self.cerrar_sesion()
                return False
        
        return True

# Instancia global del gestor de autenticación
auth_manager = AuthManager() 