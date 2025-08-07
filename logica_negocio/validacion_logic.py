import streamlit as st
from capa_datos.validacion_data import (
    validar_datos_db,
    limpiar_datos_db,
    crear_backup_db,
    validar_todas_las_tablas_db,
    limpiar_todas_las_tablas_db,
    crear_backup_todas_las_tablas_db
)
from capa_datos.database_connection import get_db_connection

class ValidacionLogic:
    """
    Lógica de negocio para la validación y limpieza de datos.
    """
    
    def __init__(self):
        self.conn = None  # Inicializar como None
        self.tablas_disponibles = ['clientes', 'canchas', 'reservas', 'pagos', 'usuarios']
    
    def _get_connection(self):
        """
        Obtiene una conexión a la base de datos usando la función ya definida.
        
        Returns:
            psycopg2.connection: Conexión a la base de datos
        """
        if not self.conn:
            self.conn = get_db_connection()
        return self.conn
    
    def _log_error(self, message):
        """
        Registra un error de manera compatible con Streamlit y fuera de él.
        
        Args:
            message (str): Mensaje de error
        """
        try:
            st.error(message)
        except:
            print(f"ERROR: {message}")
    
    def validar_tabla(self, tabla):
        """
        Valida los datos de una tabla específica.
        
        Args:
            tabla (str): Nombre de la tabla a validar
        
        Returns:
            bool: True si la validación se ejecutó correctamente, False en caso contrario
        """
        try:
            if tabla not in self.tablas_disponibles:
                self._log_error(f"❌ Tabla '{tabla}' no está disponible para validación")
                return False
            
            conn = self._get_connection()
            if not conn:
                self._log_error("No hay conexión a la base de datos")
                return False
            
            return validar_datos_db(conn, tabla)
            
        except Exception as e:
            self._log_error(f"Error al validar tabla {tabla}: {e}")
            return False
    
    def limpiar_tabla(self, tabla):
        """
        Limpia los datos de una tabla específica.
        
        Args:
            tabla (str): Nombre de la tabla a limpiar
        
        Returns:
            bool: True si la limpieza se ejecutó correctamente, False en caso contrario
        """
        try:
            if tabla not in self.tablas_disponibles:
                self._log_error(f"❌ Tabla '{tabla}' no está disponible para limpieza")
                return False
            
            # Confirmar antes de limpiar
            if not st.session_state.get('confirmar_limpieza', False):
                st.warning("⚠️ La limpieza de datos es irreversible. Confirme la acción.")
                return False
            
            conn = self._get_connection()
            if not conn:
                self._log_error("No hay conexión a la base de datos")
                return False
            
            return limpiar_datos_db(conn, tabla)
            
        except Exception as e:
            self._log_error(f"Error al limpiar tabla {tabla}: {e}")
            return False
    
    def crear_backup_tabla(self, tabla):
        """
        Crea un backup de una tabla específica.
        
        Args:
            tabla (str): Nombre de la tabla para crear backup
        
        Returns:
            bool: True si el backup se creó correctamente, False en caso contrario
        """
        try:
            if tabla not in self.tablas_disponibles:
                self._log_error(f"❌ Tabla '{tabla}' no está disponible para backup")
                return False
            
            conn = self._get_connection()
            if not conn:
                self._log_error("No hay conexión a la base de datos")
                return False
            
            return crear_backup_db(conn, tabla)
            
        except Exception as e:
            self._log_error(f"Error al crear backup de tabla {tabla}: {e}")
            return False
    
    def validar_todas_las_tablas(self):
        """
        Valida todas las tablas del sistema.
        
        Returns:
            dict: Diccionario con el resultado de validación de cada tabla
        """
        try:
            conn = self._get_connection()
            if not conn:
                self._log_error("No hay conexión a la base de datos")
                return {}
            
            st.info("🔄 Iniciando validación de todas las tablas...")
            resultados = validar_todas_las_tablas_db(conn)
            
            # Mostrar resumen
            exitosas = sum(1 for resultado in resultados.values() if resultado)
            total = len(resultados)
            
            st.success(f"✅ Validación completada: {exitosas}/{total} tablas validadas correctamente")
            
            return resultados
            
        except Exception as e:
            self._log_error(f"Error al validar todas las tablas: {e}")
            return {}
    
    def limpiar_todas_las_tablas(self):
        """
        Limpia todas las tablas del sistema.
        
        Returns:
            dict: Diccionario con el resultado de limpieza de cada tabla
        """
        try:
            # Confirmar antes de limpiar todo
            if not st.session_state.get('confirmar_limpieza_total', False):
                st.warning("⚠️ La limpieza de todas las tablas es irreversible. Confirme la acción.")
                return {}
            
            conn = self._get_connection()
            if not conn:
                self._log_error("No hay conexión a la base de datos")
                return {}
            
            st.info("🔄 Iniciando limpieza de todas las tablas...")
            resultados = limpiar_todas_las_tablas_db(conn)
            
            # Mostrar resumen
            exitosas = sum(1 for resultado in resultados.values() if resultado)
            total = len(resultados)
            
            st.success(f"✅ Limpieza completada: {exitosas}/{total} tablas limpiadas correctamente")
            
            return resultados
            
        except Exception as e:
            self._log_error(f"Error al limpiar todas las tablas: {e}")
            return {}
    
    def crear_backup_todas_las_tablas(self):
        """
        Crea backup de todas las tablas del sistema.
        
        Returns:
            dict: Diccionario con el resultado de backup de cada tabla
        """
        try:
            conn = self._get_connection()
            if not conn:
                self._log_error("No hay conexión a la base de datos")
                return {}
            
            st.info("🔄 Iniciando backup de todas las tablas...")
            resultados = crear_backup_todas_las_tablas_db(conn)
            
            # Mostrar resumen
            exitosas = sum(1 for resultado in resultados.values() if resultado)
            total = len(resultados)
            
            st.success(f"✅ Backup completado: {exitosas}/{total} tablas respaldadas correctamente")
            
            return resultados
            
        except Exception as e:
            self._log_error(f"Error al crear backup de todas las tablas: {e}")
            return {}
    
    def obtener_estadisticas_validacion(self):
        """
        Obtiene estadísticas sobre el estado de validación de las tablas.
        
        Returns:
            dict: Estadísticas de validación
        """
        try:
            estadisticas = {
                'total_tablas': len(self.tablas_disponibles),
                'tablas_disponibles': self.tablas_disponibles,
                'ultima_validacion': st.session_state.get('ultima_validacion', 'Nunca'),
                'ultima_limpieza': st.session_state.get('ultima_limpieza', 'Nunca'),
                'ultimo_backup': st.session_state.get('ultimo_backup', 'Nunca')
            }
            
            return estadisticas
            
        except Exception as e:
            self._log_error(f"Error al obtener estadísticas de validación: {e}")
            return {}

# Instancia global de la lógica de validación
validacion_logic = ValidacionLogic() 