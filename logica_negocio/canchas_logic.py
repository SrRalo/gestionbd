import streamlit as st
from capa_datos.canchas_data import (
    get_canchas_con_tipos_db, 
    get_canchas_db, 
    get_tipos_cancha_db,
    get_cancha_by_id_db,
    crear_cancha_db,
    crear_tipo_cancha_db,
    actualizar_cancha_db,
    actualizar_tipo_cancha_db,
    eliminar_cancha_db,
    eliminar_tipo_cancha_db
)

class CanchasLogic:
    """
    Lógica de negocio para la gestión de canchas.
    """
    
    def __init__(self):
        self.conn = st.session_state.get('db_connection')
    
    def obtener_canchas_con_tipos(self):
        """
        Obtiene todas las canchas con información de sus tipos.
        
        Returns:
            list: Lista de canchas con tipos
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return []
            
            return get_canchas_con_tipos_db(self.conn)
            
        except Exception as e:
            st.error(f"Error al obtener canchas con tipos: {e}")
            return []
    
    def obtener_canchas(self):
        """
        Obtiene todas las canchas.
        
        Returns:
            list: Lista de canchas
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return []
            
            return get_canchas_db(self.conn)
            
        except Exception as e:
            st.error(f"Error al obtener canchas: {e}")
            return []
    
    def obtener_tipos_cancha(self):
        """
        Obtiene todos los tipos de cancha.
        
        Returns:
            list: Lista de tipos de cancha
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return []
            
            return get_tipos_cancha_db(self.conn)
            
        except Exception as e:
            st.error(f"Error al obtener tipos de cancha: {e}")
            return []
    
    def obtener_cancha_por_id(self, cancha_id):
        """
        Obtiene una cancha específica por su ID.
        
        Args:
            cancha_id (int): ID de la cancha
        
        Returns:
            dict: Datos de la cancha o None si no existe
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return None
            
            return get_cancha_by_id_db(self.conn, cancha_id)
            
        except Exception as e:
            st.error(f"Error al obtener cancha por ID: {e}")
            return None
    
    def obtener_estadisticas_canchas(self):
        """
        Obtiene estadísticas básicas de canchas.
        
        Returns:
            dict: Estadísticas de canchas
        """
        try:
            canchas = self.obtener_canchas()
            
            total_canchas = len(canchas)
            canchas_activas = len([c for c in canchas if c.get('estado') == 'activa'])
            canchas_inactivas = total_canchas - canchas_activas
            
            # Calcular precio promedio
            precios = [float(c.get('precio_hora', 0)) for c in canchas if c.get('precio_hora')]
            precio_promedio = sum(precios) / len(precios) if precios else 0
            
            return {
                'total_canchas': total_canchas,
                'canchas_activas': canchas_activas,
                'canchas_inactivas': canchas_inactivas,
                'precio_promedio': round(precio_promedio, 2)
            }
            
        except Exception as e:
            st.error(f"Error al obtener estadísticas de canchas: {e}")
            return {
                'total_canchas': 0,
                'canchas_activas': 0,
                'canchas_inactivas': 0,
                'precio_promedio': 0
            }
    
    def crear_cancha(self, nombre, tipo_deporte, capacidad, precio_hora, estado, 
                    horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
        """
        Crear una nueva cancha.
        
        Args:
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
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return None
            
            nuevo_id = crear_cancha_db(
                self.conn, nombre, tipo_deporte, capacidad, precio_hora, 
                estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id
            )
            return nuevo_id
            
        except Exception as e:
            st.error(f"Error al crear cancha: {e}")
            return None
    
    def crear_tipo_cancha(self, nombre, descripcion, precio_por_hora):
        """
        Crear un nuevo tipo de cancha.
        
        Args:
            nombre (str): Nombre del tipo de cancha
            descripcion (str): Descripción del tipo de cancha
            precio_por_hora (float): Precio por hora
            
        Returns:
            int: ID del tipo de cancha creado o None si hay error
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return None
            
            nuevo_id = crear_tipo_cancha_db(self.conn, nombre, descripcion, precio_por_hora)
            return nuevo_id
            
        except Exception as e:
            st.error(f"Error al crear tipo de cancha: {e}")
            return None
    
    def actualizar_cancha(self, cancha_id, nombre, tipo_deporte, capacidad, precio_hora, 
                         estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
        """
        Actualizar una cancha existente.
        
        Args:
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
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return False
            
            resultado = actualizar_cancha_db(
                self.conn, cancha_id, nombre, tipo_deporte, capacidad, precio_hora,
                estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id
            )
            return resultado
            
        except Exception as e:
            st.error(f"Error al actualizar cancha: {e}")
            return False
    
    def actualizar_tipo_cancha(self, tipo_id, nombre, descripcion, precio_por_hora, activo):
        """
        Actualizar un tipo de cancha existente.
        
        Args:
            tipo_id (int): ID del tipo de cancha
            nombre (str): Nuevo nombre
            descripcion (str): Nueva descripción
            precio_por_hora (float): Nuevo precio por hora
            activo (bool): Estado activo/inactivo
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return False
            
            resultado = actualizar_tipo_cancha_db(self.conn, tipo_id, nombre, descripcion, precio_por_hora, activo)
            return resultado
            
        except Exception as e:
            st.error(f"Error al actualizar tipo de cancha: {e}")
            return False
    
    def eliminar_cancha(self, cancha_id):
        """
        Eliminar una cancha.
        
        Args:
            cancha_id (int): ID de la cancha a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return False
            
            resultado = eliminar_cancha_db(self.conn, cancha_id)
            return resultado
            
        except Exception as e:
            st.error(f"Error al eliminar cancha: {e}")
            return False
    
    def eliminar_tipo_cancha(self, tipo_id):
        """
        Eliminar un tipo de cancha.
        
        Args:
            tipo_id (int): ID del tipo de cancha a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if not self.conn:
                st.error("No hay conexión a la base de datos")
                return False
            
            resultado = eliminar_tipo_cancha_db(self.conn, tipo_id)
            return resultado
            
        except Exception as e:
            st.error(f"Error al eliminar tipo de cancha: {e}")
            return False

# Instancia global de la lógica de canchas
canchas_logic = CanchasLogic() 