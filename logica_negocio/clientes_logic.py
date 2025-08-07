import streamlit as st
import psycopg2
import re
from datetime import date
from capa_datos.database_connection import get_db_connection

class ClientesLogic:
    """
    Lógica de negocio para la gestión de clientes.
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
    
    def validar_email(self, email):
        """
        Valida el formato de un email.
        
        Args:
            email (str): Email a validar
        
        Returns:
            bool: True si el email es válido
        """
        if not email:
            return False
        
        # Patrón básico para validar email
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def validar_telefono(self, telefono):
        """
        Valida el formato de un teléfono.
        
        Args:
            telefono (str): Teléfono a validar
        
        Returns:
            bool: True si el teléfono es válido
        """
        if not telefono:
            return True  # El teléfono es opcional
        
        # Eliminar espacios, guiones y paréntesis
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
        
        # Verificar que solo contenga dígitos y posiblemente un +
        if not re.match(r'^\+?[\d]+$', telefono_limpio):
            return False
        
        # Verificar longitud mínima (al menos 7 dígitos)
        if len(telefono_limpio.replace('+', '')) < 7:
            return False
        
        return True
    
    def validar_fecha_nacimiento(self, fecha_nacimiento):
        """
        Valida que la fecha de nacimiento sea válida.
        
        Args:
            fecha_nacimiento (date): Fecha de nacimiento
        
        Returns:
            bool: True si la fecha es válida
        """
        if not fecha_nacimiento:
            return True  # La fecha de nacimiento es opcional
        
        # No permitir fechas futuras
        if fecha_nacimiento > date.today():
            return False
        
        # No permitir fechas muy antiguas (más de 120 años)
        fecha_minima = date.today().replace(year=date.today().year - 120)
        if fecha_nacimiento < fecha_minima:
            return False
        
        return True
    
    def obtener_clientes(self):
        """
        Obtiene todos los clientes.
        
        Returns:
            list: Lista de clientes
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener clientes
            cur.execute("""
                SELECT id, nombre, apellido, telefono, email, fecha_nacimiento,
                       estado, fecha_registro, fecha_actualizacion
                FROM clientes
                ORDER BY apellido, nombre
            """)
            
            clientes = cur.fetchall()
            cur.close()
            
            return clientes
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener clientes: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_clientes_activos(self):
        """
        Obtiene solo los clientes activos.
        
        Returns:
            list: Lista de clientes activos
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener clientes activos
            cur.execute("""
                SELECT id, nombre, apellido, telefono, email, fecha_nacimiento,
                       estado, fecha_registro, fecha_actualizacion
                FROM clientes
                WHERE estado = 'Activo'
                ORDER BY apellido, nombre
            """)
            
            clientes = cur.fetchall()
            cur.close()
            
            return clientes
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener clientes activos: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_cliente_por_id(self, cliente_id):
        """
        Obtiene un cliente específico por su ID.
        
        Args:
            cliente_id (int): ID del cliente
            
        Returns:
            tuple or None: Datos del cliente o None si no se encuentra
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener cliente por ID
            cur.execute("""
                SELECT id, nombre, apellido, telefono, email, fecha_nacimiento,
                       estado, fecha_registro, fecha_actualizacion
                FROM clientes
                WHERE id = %s
            """, (cliente_id,))
            
            cliente = cur.fetchone()
            cur.close()
            
            return cliente
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener cliente por ID: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def crear_cliente(self, nombre, apellido, telefono, email, fecha_nacimiento=None):
        """
        Crea un nuevo cliente.
        
        Args:
            nombre (str): Nombre del cliente
            apellido (str): Apellido del cliente
            telefono (str): Teléfono del cliente
            email (str): Email del cliente
            fecha_nacimiento (date, optional): Fecha de nacimiento
            
        Returns:
            int or None: ID del cliente creado o None si falla
        """
        conn = None
        try:
            # Validaciones
            if not nombre or not apellido:
                self._log_error("Nombre y apellido son obligatorios")
                return None
            
            if not self.validar_email(email):
                self._log_error("Email no válido")
                return None
            
            if not self.validar_telefono(telefono):
                self._log_error("Teléfono no válido")
                return None
            
            if fecha_nacimiento and not self.validar_fecha_nacimiento(fecha_nacimiento):
                self._log_error("Fecha de nacimiento no válida")
                return None
            
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL crear_cliente
            cur.execute("""
                SELECT crear_cliente(%s, %s, %s, %s, %s)
            """, (nombre, apellido, telefono, email, fecha_nacimiento))
            
            cliente_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return cliente_id
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al crear cliente: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def actualizar_cliente(self, cliente_id, nombre, apellido, telefono, email, fecha_nacimiento=None, estado="Activo"):
        """
        Actualiza un cliente existente.
        
        Args:
            cliente_id (int): ID del cliente
            nombre (str): Nombre del cliente
            apellido (str): Apellido del cliente
            telefono (str): Teléfono del cliente
            email (str): Email del cliente
            fecha_nacimiento (date, optional): Fecha de nacimiento
            estado (str): Estado del cliente
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        conn = None
        try:
            # Validaciones
            if not nombre or not apellido:
                self._log_error("Nombre y apellido son obligatorios")
                return False
            
            if not self.validar_email(email):
                self._log_error("Email no válido")
                return False
            
            if not self.validar_telefono(telefono):
                self._log_error("Teléfono no válido")
                return False
            
            if fecha_nacimiento and not self.validar_fecha_nacimiento(fecha_nacimiento):
                self._log_error("Fecha de nacimiento no válida")
                return False
            
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL actualizar_cliente
            cur.execute("""
                SELECT actualizar_cliente(%s, %s, %s, %s, %s, %s, %s)
            """, (cliente_id, nombre, apellido, telefono, email, fecha_nacimiento, estado))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al actualizar cliente: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def eliminar_cliente(self, cliente_id):
        """
        Elimina un cliente.
        
        Args:
            cliente_id (int): ID del cliente
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL eliminar_cliente
            cur.execute("""
                SELECT eliminar_cliente(%s)
            """, (cliente_id,))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al eliminar cliente: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def buscar_clientes(self, termino_busqueda):
        """
        Busca clientes por nombre, apellido o email.
        
        Args:
            termino_busqueda (str): Término de búsqueda
            
        Returns:
            list: Lista de clientes que coinciden con la búsqueda
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para buscar clientes
            cur.execute("""
                SELECT id, nombre, apellido, telefono, email, fecha_nacimiento,
                       estado, fecha_registro, fecha_actualizacion
                FROM clientes
                WHERE LOWER(nombre) LIKE LOWER(%s) 
                   OR LOWER(apellido) LIKE LOWER(%s)
                   OR LOWER(email) LIKE LOWER(%s)
                ORDER BY apellido, nombre
            """, (f'%{termino_busqueda}%', f'%{termino_busqueda}%', f'%{termino_busqueda}%'))
            
            clientes = cur.fetchall()
            cur.close()
            
            return clientes
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al buscar clientes: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_estadisticas_clientes(self):
        """
        Obtiene estadísticas de clientes.
        
        Returns:
            dict: Estadísticas de clientes
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
                    COUNT(*) as total_clientes,
                    COUNT(CASE WHEN estado = 'Activo' THEN 1 END) as clientes_activos,
                    COUNT(CASE WHEN estado = 'Inactivo' THEN 1 END) as clientes_inactivos,
                    COUNT(CASE WHEN fecha_nacimiento IS NOT NULL THEN 1 END) as con_fecha_nacimiento,
                    COUNT(CASE WHEN email IS NOT NULL AND email != '' THEN 1 END) as con_email,
                    COUNT(CASE WHEN telefono IS NOT NULL AND telefono != '' THEN 1 END) as con_telefono
                FROM clientes
            """)
            
            stats = cur.fetchone()
            cur.close()
            
            return {
                'total_clientes': stats[0],
                'clientes_activos': stats[1],
                'clientes_inactivos': stats[2],
                'con_fecha_nacimiento': stats[3],
                'con_email': stats[4],
                'con_telefono': stats[5]
            }
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener estadísticas de clientes: {error}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def obtener_reservas_activas_cliente(self, cliente_id):
        """
        Obtiene las reservas activas de un cliente específico.
        
        Args:
            cliente_id (int): ID del cliente
            
        Returns:
            list: Lista de reservas activas del cliente
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener reservas activas del cliente
            cur.execute("""
                SELECT r.id, r.fecha_reserva, r.hora_inicio, r.hora_fin, r.duracion,
                       r.observaciones, r.estado, r.fecha_creacion,
                       ca.nombre as nombre_cancha, ca.tipo_deporte
                FROM reservas r
                JOIN canchas ca ON r.cancha_id = ca.id
                WHERE r.cliente_id = %s 
                AND r.estado IN ('pendiente', 'confirmada')
                ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC
            """, (cliente_id,))
            
            reservas = cur.fetchall()
            cur.close()
            
            return reservas
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener reservas activas del cliente: {error}")
            return []
        finally:
            if conn:
                conn.close() 