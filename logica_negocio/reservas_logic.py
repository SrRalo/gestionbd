import streamlit as st
import psycopg2
from datetime import datetime, date, timedelta
from capa_datos.database_connection import get_db_connection

class ReservasLogic:
    """
    Lógica de negocio para la gestión de reservas.
    """
    
    def __init__(self):
        self.estados_reserva = ['pendiente', 'confirmada', 'cancelada', 'completada']
        self.hora_minima = datetime.strptime('06:00', '%H:%M').time()  # 6:00 AM
        self.hora_maxima = datetime.strptime('23:00', '%H:%M').time()  # 11:00 PM
        self.duracion_minima = 30  # minutos
        self.duracion_maxima = 240  # minutos (4 horas)
    
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
    
    def validar_fecha_reserva(self, fecha_reserva):
        """
        Valida que la fecha de reserva sea válida.
        
        Args:
            fecha_reserva (date): Fecha de la reserva
        
        Returns:
            bool: True si la fecha es válida
        """
        if not fecha_reserva:
            return False
        
        # No permitir reservas en el pasado
        if fecha_reserva < date.today():
            return False
        
        # No permitir reservas más allá de 3 meses
        fecha_maxima = date.today() + timedelta(days=90)
        if fecha_reserva > fecha_maxima:
            return False
        
        return True
    
    def validar_horario(self, hora_inicio, hora_fin):
        """
        Valida que el horario sea válido.
        
        Args:
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
        
        Returns:
            bool: True si el horario es válido
        """
        if not hora_inicio or not hora_fin:
            return False
        
        # Verificar que la hora de fin sea posterior a la de inicio
        if hora_fin <= hora_inicio:
            return False
        
        # Verificar que esté dentro del horario permitido
        if hora_inicio < self.hora_minima or hora_fin > self.hora_maxima:
            return False
        
        # Calcular duración en minutos
        duracion = (hora_fin.hour * 60 + hora_fin.minute) - (hora_inicio.hour * 60 + hora_inicio.minute)
        
        # Verificar duración mínima y máxima
        if duracion < self.duracion_minima:
            return False
        
        if duracion > self.duracion_maxima:
            return False
        
        return True
    
    def validar_estado_reserva(self, estado):
        """
        Valida que el estado de la reserva sea válido.
        
        Args:
            estado (str): Estado a validar
        
        Returns:
            bool: True si el estado es válido
        """
        return estado in self.estados_reserva
    
    def crear_reserva(self, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones=None):
        """
        Crea una nueva reserva usando el procedimiento almacenado.
        
        Args:
            cliente_id (int): ID del cliente
            cancha_id (int): ID de la cancha
            fecha_reserva (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
            observaciones (str, optional): Observaciones de la reserva
            
        Returns:
            int or None: ID de la reserva creada o None si falla
        """
        conn = None
        try:
            # Validaciones
            if not self.validar_fecha_reserva(fecha_reserva):
                self._log_error("Fecha de reserva no válida")
                return None
            
            if not self.validar_horario(hora_inicio, hora_fin):
                self._log_error("Horario no válido")
                return None
            
            # Verificar disponibilidad
            if not self.verificar_disponibilidad(cancha_id, fecha_reserva, hora_inicio, hora_fin):
                self._log_error("La cancha no está disponible en el horario seleccionado")
                return None
            
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Llamada directa al procedimiento almacenado proc_gestionar_reserva
            cur.execute("""
                CALL proc_gestionar_reserva('INSERT', %s, %s, %s, %s, %s, %s, %s)
            """, (cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones, 'pendiente'))
            
            # Obtener el ID de la reserva creada
            cur.execute("""
                SELECT id FROM reservas 
                WHERE cliente_id = %s AND cancha_id = %s 
                ORDER BY fecha_creacion DESC LIMIT 1
            """, (cliente_id, cancha_id))
            
            resultado = cur.fetchone()
            if resultado:
                reserva_id = resultado[0]
                conn.commit()
                cur.close()
                return reserva_id
            else:
                conn.rollback()
                cur.close()
                return None
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al crear reserva: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def obtener_reservas(self, solo_activas=False):
        """
        Obtiene todas las reservas.
        
        Args:
            solo_activas (bool): Si True, solo obtiene reservas activas
            
        Returns:
            list: Lista de reservas
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            if solo_activas:
                # Consulta SQL directa para reservas activas
                cur.execute("""
                    SELECT r.id, r.cliente_id, r.cancha_id, r.fecha_reserva, r.hora_inicio,
                           r.hora_fin, r.duracion, r.observaciones, r.estado,
                           r.fecha_creacion, r.fecha_actualizacion,
                           c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                           ca.nombre as nombre_cancha
                    FROM reservas r
                    JOIN clientes c ON r.cliente_id = c.id
                    JOIN canchas ca ON r.cancha_id = ca.id
                    WHERE r.estado IN ('pendiente', 'confirmada')
                    ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC
                """)
            else:
                # Consulta SQL directa para todas las reservas
                cur.execute("""
                    SELECT r.id, r.cliente_id, r.cancha_id, r.fecha_reserva, r.hora_inicio,
                           r.hora_fin, r.duracion, r.observaciones, r.estado,
                           r.fecha_creacion, r.fecha_actualizacion,
                           c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                           ca.nombre as nombre_cancha
                    FROM reservas r
                    JOIN clientes c ON r.cliente_id = c.id
                    JOIN canchas ca ON r.cancha_id = ca.id
                    ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC
                """)
            
            reservas = cur.fetchall()
            cur.close()
            
            return reservas
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener reservas: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_reserva_por_id(self, reserva_id):
        """
        Obtiene una reserva específica por su ID.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            tuple or None: Datos de la reserva o None si no se encuentra
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener reserva por ID
            cur.execute("""
                SELECT r.id, r.cliente_id, r.cancha_id, r.fecha_reserva, r.hora_inicio,
                       r.hora_fin, r.duracion, r.observaciones, r.estado,
                       r.fecha_creacion, r.fecha_actualizacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       ca.nombre as nombre_cancha
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.id
                JOIN canchas ca ON r.cancha_id = ca.id
                WHERE r.id = %s
            """, (reserva_id,))
            
            reserva = cur.fetchone()
            cur.close()
            
            return reserva
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener reserva por ID: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def actualizar_reserva(self, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones=None, estado='pendiente'):
        """
        Actualiza una reserva existente.
        
        Args:
            reserva_id (int): ID de la reserva
            cliente_id (int): ID del cliente
            cancha_id (int): ID de la cancha
            fecha_reserva (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
            observaciones (str, optional): Observaciones
            estado (str): Estado de la reserva
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        conn = None
        try:
            # Validaciones
            if not self.validar_fecha_reserva(fecha_reserva):
                self._log_error("Fecha de reserva no válida")
                return False
            
            if not self.validar_horario(hora_inicio, hora_fin):
                self._log_error("Horario no válido")
                return False
            
            if not self.validar_estado_reserva(estado):
                self._log_error("Estado de reserva no válido")
                return False
            
            # Verificar disponibilidad (excluyendo la reserva actual)
            if not self.verificar_disponibilidad(cancha_id, fecha_reserva, hora_inicio, hora_fin, reserva_id):
                self._log_error("La cancha no está disponible en el horario seleccionado")
                return False
            
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa al procedimiento almacenado proc_gestionar_reserva
            cur.execute("""
                CALL proc_gestionar_reserva('UPDATE', %s, %s, %s, %s, %s, %s, %s)
            """, (cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones, estado))
            
            conn.commit()
            cur.close()
            
            return True
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al actualizar reserva: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def cancelar_reserva(self, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin):
        """
        Cancela una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            cliente_id (int): ID del cliente
            cancha_id (int): ID de la cancha
            fecha_reserva (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
            
        Returns:
            bool: True si se canceló correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa al procedimiento almacenado proc_gestionar_reserva
            cur.execute("""
                CALL proc_gestionar_reserva('DELETE', %s, %s, %s, %s, %s, 'Reserva cancelada', 'cancelada')
            """, (cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin))
            
            conn.commit()
            cur.close()
            
            return True
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al cancelar reserva: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def verificar_disponibilidad(self, cancha_id, fecha, hora_inicio, hora_fin, reserva_id_excluir=None):
        """
        Verifica si una cancha está disponible en un horario específico.
        
        Args:
            cancha_id (int): ID de la cancha
            fecha (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
            reserva_id_excluir (int, optional): ID de reserva a excluir (para actualizaciones)
            
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            if reserva_id_excluir:
                # Consulta SQL directa excluyendo una reserva específica
                cur.execute("""
                    SELECT COUNT(*) FROM reservas 
                    WHERE cancha_id = %s 
                    AND fecha_reserva = %s 
                    AND estado IN ('pendiente', 'confirmada')
                    AND id != %s
                    AND (
                        (hora_inicio < %s AND hora_fin > %s) OR
                        (hora_inicio < %s AND hora_fin > %s) OR
                        (hora_inicio >= %s AND hora_fin <= %s)
                    )
                """, (cancha_id, fecha, reserva_id_excluir, hora_fin, hora_inicio, hora_fin, hora_inicio, hora_inicio, hora_fin))
            else:
                # Consulta SQL directa para verificar disponibilidad
                cur.execute("""
                    SELECT COUNT(*) FROM reservas 
                    WHERE cancha_id = %s 
                    AND fecha_reserva = %s 
                    AND estado IN ('pendiente', 'confirmada')
                    AND (
                        (hora_inicio < %s AND hora_fin > %s) OR
                        (hora_inicio < %s AND hora_fin > %s) OR
                        (hora_inicio >= %s AND hora_fin <= %s)
                    )
                """, (cancha_id, fecha, hora_fin, hora_inicio, hora_fin, hora_inicio, hora_inicio, hora_fin))
            
            count = cur.fetchone()[0]
            cur.close()
            
            return count == 0
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al verificar disponibilidad: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def obtener_estadisticas_reservas(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas de reservas.
        
        Args:
            fecha_inicio (date, optional): Fecha de inicio para el filtro
            fecha_fin (date, optional): Fecha de fin para el filtro
            
        Returns:
            dict: Estadísticas de reservas
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return {}
            
            cur = conn.cursor()
            
            if fecha_inicio and fecha_fin:
                # Consulta SQL directa con filtro de fechas
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_reservas,
                        COUNT(CASE WHEN estado = 'confirmada' THEN 1 END) as reservas_confirmadas,
                        COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as reservas_pendientes,
                        COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as reservas_canceladas,
                        COUNT(CASE WHEN estado = 'completada' THEN 1 END) as reservas_completadas,
                        AVG(duracion) as duracion_promedio,
                        SUM(duracion) as duracion_total
                    FROM reservas
                    WHERE fecha_reserva BETWEEN %s AND %s
                """, (fecha_inicio, fecha_fin))
            else:
                # Consulta SQL directa sin filtro de fechas
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_reservas,
                        COUNT(CASE WHEN estado = 'confirmada' THEN 1 END) as reservas_confirmadas,
                        COUNT(CASE WHEN estado = 'pendiente' THEN 1 END) as reservas_pendientes,
                        COUNT(CASE WHEN estado = 'cancelada' THEN 1 END) as reservas_canceladas,
                        COUNT(CASE WHEN estado = 'completada' THEN 1 END) as reservas_completadas,
                        AVG(duracion) as duracion_promedio,
                        SUM(duracion) as duracion_total
                    FROM reservas
                """)
            
            stats = cur.fetchone()
            cur.close()
            
            return {
                'total_reservas': stats[0],
                'reservas_confirmadas': stats[1],
                'reservas_pendientes': stats[2],
                'reservas_canceladas': stats[3],
                'reservas_completadas': stats[4],
                'duracion_promedio': float(stats[5]) if stats[5] else 0,
                'duracion_total': float(stats[6]) if stats[6] else 0
            }
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener estadísticas de reservas: {error}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def obtener_reservas_paginadas(self, pagina=1, registros_por_pagina=10):
        """
        Obtiene reservas con paginación.
        
        Args:
            pagina (int): Número de página
            registros_por_pagina (int): Registros por página
            
        Returns:
            tuple: (reservas, total_registros)
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return [], 0
            
            cur = conn.cursor()
            
            # Calcular offset
            offset = (pagina - 1) * registros_por_pagina
            
            # Consulta SQL directa con paginación
            cur.execute("""
                SELECT r.id, r.cliente_id, r.cancha_id, r.fecha_reserva, r.hora_inicio,
                       r.hora_fin, r.duracion, r.observaciones, r.estado,
                       r.fecha_creacion, r.fecha_actualizacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       ca.nombre as nombre_cancha
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.id
                JOIN canchas ca ON r.cancha_id = ca.id
                ORDER BY r.fecha_reserva DESC, r.hora_inicio DESC
                LIMIT %s OFFSET %s
            """, (registros_por_pagina, offset))
            
            reservas = cur.fetchall()
            
            # Obtener total de registros
            cur.execute("SELECT COUNT(*) FROM reservas")
            total_registros = cur.fetchone()[0]
            
            cur.close()
            
            return reservas, total_registros
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener reservas paginadas: {error}")
            return [], 0
        finally:
            if conn:
                conn.close() 