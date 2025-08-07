import streamlit as st
import psycopg2
from capa_datos.database_connection import get_db_connection

class CanchasLogic:
    """
    Lógica de negocio para la gestión de canchas.
    """
    
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
    
    def obtener_canchas_con_tipos(self):
        """
        Obtiene todas las canchas con información de sus tipos.
        
        Returns:
            list: Lista de canchas con tipos
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener canchas con tipos
            cur.execute("""
                SELECT 
                    c.id, c.nombre, c.tipo_deporte, c.capacidad, c.precio_hora,
                    c.estado, c.horario_apertura, c.horario_cierre, c.descripcion,
                    c.fecha_creacion, c.fecha_actualizacion,
                    tc.id as tipo_cancha_id, tc.nombre as tipo_cancha_nombre,
                    tc.descripcion as tipo_cancha_descripcion, tc.precio_por_hora
                FROM canchas c
                LEFT JOIN tipos_cancha tc ON c.tipo_cancha_id = tc.id
                ORDER BY c.nombre
            """)
            
            canchas = cur.fetchall()
            cur.close()
            
            return canchas
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener canchas con tipos: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_canchas(self):
        """
        Obtiene todas las canchas.
        
        Returns:
            list: Lista de canchas
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener canchas
            cur.execute("""
                SELECT id, nombre, tipo_deporte, capacidad, precio_hora,
                       estado, horario_apertura, horario_cierre, descripcion,
                       fecha_creacion, fecha_actualizacion
                FROM canchas
                ORDER BY nombre
            """)
            
            canchas = cur.fetchall()
            cur.close()
            
            return canchas
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener canchas: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_tipos_cancha(self):
        """
        Obtiene todos los tipos de cancha.
        
        Returns:
            list: Lista de tipos de cancha
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener tipos de cancha
            cur.execute("""
                SELECT id, nombre, descripcion, precio_por_hora, estado,
                       fecha_creacion, fecha_actualizacion
                FROM tipos_cancha
                WHERE estado = 'Activo'
                ORDER BY nombre
            """)
            
            tipos = cur.fetchall()
            cur.close()
            
            return tipos
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener tipos de cancha: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_cancha_por_id(self, cancha_id):
        """
        Obtiene una cancha específica por su ID.
        
        Args:
            cancha_id (int): ID de la cancha
            
        Returns:
            tuple or None: Datos de la cancha o None si no se encuentra
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener cancha por ID
            cur.execute("""
                SELECT id, nombre, tipo_deporte, capacidad, precio_hora,
                       estado, horario_apertura, horario_cierre, descripcion,
                       fecha_creacion, fecha_actualizacion
                FROM canchas
                WHERE id = %s
            """, (cancha_id,))
            
            cancha = cur.fetchone()
            cur.close()
            
            return cancha
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener cancha por ID: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def obtener_estadisticas_canchas(self):
        """
        Obtiene estadísticas de las canchas.
        
        Returns:
            dict: Estadísticas de canchas
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return {}
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener estadísticas
            cur.execute("""
                SELECT 
                    COUNT(*) as total_canchas,
                    COUNT(CASE WHEN estado = 'Activa' THEN 1 END) as canchas_activas,
                    COUNT(CASE WHEN estado = 'Inactiva' THEN 1 END) as canchas_inactivas,
                    AVG(precio_hora) as precio_promedio,
                    SUM(CASE WHEN estado = 'Activa' THEN precio_hora ELSE 0 END) as ingresos_potenciales
                FROM canchas
            """)
            
            stats = cur.fetchone()
            cur.close()
            
            return {
                'total_canchas': stats[0],
                'canchas_activas': stats[1],
                'canchas_inactivas': stats[2],
                'precio_promedio': float(stats[3]) if stats[3] else 0,
                'ingresos_potenciales': float(stats[4]) if stats[4] else 0
            }
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener estadísticas de canchas: {error}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def crear_cancha(self, nombre, tipo_deporte, capacidad, precio_hora, estado, 
                    horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
        """
        Crea una nueva cancha.
        
        Args:
            nombre (str): Nombre de la cancha
            tipo_deporte (str): Tipo de deporte
            capacidad (int): Capacidad de la cancha
            precio_hora (float): Precio por hora
            estado (str): Estado de la cancha
            horario_apertura (time): Horario de apertura
            horario_cierre (time): Horario de cierre
            descripcion (str): Descripción de la cancha
            tipo_cancha_id (int): ID del tipo de cancha
            
        Returns:
            int or None: ID de la cancha creada o None si falla
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL crear_cancha
            cur.execute("""
                SELECT crear_cancha(%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nombre, tipo_deporte, capacidad, precio_hora, estado, 
                  horario_apertura, horario_cierre, descripcion, tipo_cancha_id))
            
            cancha_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return cancha_id
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al crear cancha: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def crear_tipo_cancha(self, nombre, descripcion, precio_por_hora):
        """
        Crea un nuevo tipo de cancha.
        
        Args:
            nombre (str): Nombre del tipo de cancha
            descripcion (str): Descripción del tipo
            precio_por_hora (float): Precio por hora
            
        Returns:
            int or None: ID del tipo creado o None si falla
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL crear_tipo_cancha
            cur.execute("""
                SELECT crear_tipo_cancha(%s, %s, %s)
            """, (nombre, descripcion, precio_por_hora))
            
            tipo_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return tipo_id
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al crear tipo de cancha: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def actualizar_cancha(self, cancha_id, nombre, tipo_deporte, capacidad, precio_hora, 
                         estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
        """
        Actualiza una cancha existente.
        
        Args:
            cancha_id (int): ID de la cancha
            nombre (str): Nombre de la cancha
            tipo_deporte (str): Tipo de deporte
            capacidad (int): Capacidad de la cancha
            precio_hora (float): Precio por hora
            estado (str): Estado de la cancha
            horario_apertura (time): Horario de apertura
            horario_cierre (time): Horario de cierre
            descripcion (str): Descripción de la cancha
            tipo_cancha_id (int): ID del tipo de cancha
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL actualizar_cancha
            cur.execute("""
                SELECT actualizar_cancha(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (cancha_id, nombre, tipo_deporte, capacidad, precio_hora, 
                  estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al actualizar cancha: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def actualizar_tipo_cancha(self, tipo_id, nombre, descripcion, precio_por_hora, activo):
        """
        Actualiza un tipo de cancha existente.
        
        Args:
            tipo_id (int): ID del tipo de cancha
            nombre (str): Nombre del tipo
            descripcion (str): Descripción del tipo
            precio_por_hora (float): Precio por hora
            activo (bool): Estado activo del tipo
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL actualizar_tipo_cancha
            cur.execute("""
                SELECT actualizar_tipo_cancha(%s, %s, %s, %s, %s)
            """, (tipo_id, nombre, descripcion, precio_por_hora, activo))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al actualizar tipo de cancha: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def eliminar_cancha(self, cancha_id):
        """
        Elimina una cancha.
        
        Args:
            cancha_id (int): ID de la cancha
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL eliminar_cancha
            cur.execute("""
                SELECT eliminar_cancha(%s)
            """, (cancha_id,))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al eliminar cancha: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def eliminar_tipo_cancha(self, tipo_id):
        """
        Elimina un tipo de cancha.
        
        Args:
            tipo_id (int): ID del tipo de cancha
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL eliminar_tipo_cancha
            cur.execute("""
                SELECT eliminar_tipo_cancha(%s)
            """, (tipo_id,))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al eliminar tipo de cancha: {error}")
            return False
        finally:
            if conn:
                conn.close()

# Instancia global de la lógica de canchas
canchas_logic = CanchasLogic() 