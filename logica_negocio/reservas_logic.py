import streamlit as st
from datetime import datetime, date, timedelta
from capa_datos.reservas_data import (
    crear_reserva_db, get_reservas_db, get_reserva_by_id_db,
    actualizar_reserva_db, cancelar_reserva_db, get_reservas_por_fecha_db,
    get_reservas_por_cliente_db, get_reservas_por_cancha_db, get_reservas_activas_db,
    verificar_disponibilidad_db
)
from capa_datos.canchas_data import get_cancha_by_id_db
from capa_datos.clientes_data import get_cliente_by_id_db

class ReservasLogic:
    """
    Lógica de negocio para la gestión de reservas.
    """
    
    def __init__(self):
        self.conn = st.session_state.get('db_connection')
        self.estados_reserva = ['pendiente', 'confirmada', 'cancelada', 'completada']
        self.hora_minima = datetime.strptime('06:00', '%H:%M').time()  # 6:00 AM
        self.hora_maxima = datetime.strptime('23:00', '%H:%M').time()  # 11:00 PM
        self.duracion_minima = 30  # minutos
        self.duracion_maxima = 240  # minutos (4 horas)
    
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
            observaciones (str): Observaciones opcionales
        
        Returns:
            bool: True si se creó correctamente, False en caso contrario
        """
        try:
            # Validar que la reserva no esté en el pasado
            if fecha_reserva < date.today():
                st.error("❌ No se pueden crear reservas en fechas pasadas")
                return False
            
            # Validar que la hora de fin sea posterior a la de inicio
            if hora_fin <= hora_inicio:
                st.error("❌ La hora de fin debe ser posterior a la hora de inicio")
                return False
            
            # Verificar disponibilidad
            if not verificar_disponibilidad_db(self.conn, cancha_id, fecha_reserva, hora_inicio, hora_fin):
                st.error("❌ La cancha no está disponible en el horario especificado")
                return False
            
            # Crear la reserva usando el procedimiento almacenado
            return crear_reserva_db(self.conn, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones)
            
        except Exception as e:
            st.error(f"Error al crear reserva: {e}")
            return False
    
    def obtener_reservas(self, solo_activas=False):
        """
        Obtiene la lista de reservas.
        
        Args:
            solo_activas (bool): Si True, solo retorna reservas activas
        
        Returns:
            list: Lista de reservas
        """
        try:
            if solo_activas:
                return get_reservas_activas_db(self.conn)
            else:
                return get_reservas_db(self.conn)
        except Exception as e:
            st.error(f"Error al obtener reservas: {e}")
            return []
    
    def obtener_reserva_por_id(self, reserva_id):
        """
        Obtiene una reserva específica por su ID.
        
        Args:
            reserva_id (int): ID de la reserva
        
        Returns:
            dict: Datos de la reserva o None si no existe
        """
        try:
            return get_reserva_by_id_db(self.conn, reserva_id)
        except Exception as e:
            st.error(f"Error al obtener reserva: {e}")
            return None
    
    def actualizar_reserva(self, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones=None, estado='pendiente'):
        """
        Actualiza una reserva existente usando el procedimiento almacenado.
        
        Args:
            reserva_id (int): ID de la reserva a actualizar
            cliente_id (int): ID del cliente
            cancha_id (int): ID de la cancha
            fecha_reserva (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
            observaciones (str): Observaciones opcionales
            estado (str): Estado de la reserva
        
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Validar que la reserva existe
            reserva_actual = get_reserva_by_id_db(self.conn, reserva_id)
            if not reserva_actual:
                st.error("❌ La reserva especificada no existe")
                return False
            
            # Validar que la hora de fin sea posterior a la de inicio
            if hora_fin <= hora_inicio:
                st.error("❌ La hora de fin debe ser posterior a la hora de inicio")
                return False
            
            # Verificar disponibilidad (excluyendo la reserva actual)
            if not verificar_disponibilidad_db(self.conn, cancha_id, fecha_reserva, hora_inicio, hora_fin, reserva_id):
                st.error("❌ La cancha no está disponible en el horario especificado")
                return False
            
            # Actualizar la reserva usando el procedimiento almacenado
            return actualizar_reserva_db(self.conn, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, observaciones, estado)
            
        except Exception as e:
            st.error(f"Error al actualizar reserva: {e}")
            return False
    
    def cancelar_reserva(self, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin):
        """
        Cancela una reserva usando el procedimiento almacenado.
        
        Args:
            reserva_id (int): ID de la reserva a cancelar
            cliente_id (int): ID del cliente
            cancha_id (int): ID de la cancha
            fecha_reserva (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
        
        Returns:
            bool: True si se canceló correctamente, False en caso contrario
        """
        try:
            # Validar que la reserva existe
            reserva = get_reserva_by_id_db(self.conn, reserva_id)
            if not reserva:
                st.error("❌ La reserva especificada no existe")
                return False
            
            # Validar que la reserva no esté ya cancelada
            if reserva['estado'] == 'cancelada':
                st.warning("⚠️ La reserva ya está cancelada")
                return True
            
            # Cancelar la reserva usando el procedimiento almacenado
            return cancelar_reserva_db(self.conn, reserva_id, cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin)
            
        except Exception as e:
            st.error(f"Error al cancelar reserva: {e}")
            return False
    
    def obtener_reservas_por_fecha(self, fecha):
        """
        Obtiene las reservas para una fecha específica.
        
        Args:
            fecha (date): Fecha para filtrar
        
        Returns:
            list: Lista de reservas para esa fecha
        """
        try:
            return get_reservas_por_fecha_db(self.conn, fecha)
        except Exception as e:
            st.error(f"Error al obtener reservas por fecha: {e}")
            return []
    
    def obtener_reservas_por_cliente(self, cliente_id):
        """
        Obtiene todas las reservas de un cliente específico.
        
        Args:
            cliente_id (int): ID del cliente
        
        Returns:
            list: Lista de reservas del cliente
        """
        try:
            return get_reservas_por_cliente_db(self.conn, cliente_id)
        except Exception as e:
            st.error(f"Error al obtener reservas por cliente: {e}")
            return []
    
    def obtener_reservas_por_cancha(self, cancha_id):
        """
        Obtiene todas las reservas de una cancha específica.
        
        Args:
            cancha_id (int): ID de la cancha
        
        Returns:
            list: Lista de reservas de la cancha
        """
        try:
            return get_reservas_por_cancha_db(self.conn, cancha_id)
        except Exception as e:
            st.error(f"Error al obtener reservas por cancha: {e}")
            return []
    
    def obtener_reservas_por_estado(self, estado):
        """
        Obtiene todas las reservas de un estado específico.
        
        Args:
            estado (str): Estado de las reservas a filtrar
        
        Returns:
            list: Lista de reservas del estado especificado
        """
        try:
            # Obtener todas las reservas y filtrar por estado
            reservas = get_reservas_db(self.conn)
            return [r for r in reservas if r['estado'].lower() == estado.lower()]
        except Exception as e:
            st.error(f"Error al obtener reservas por estado: {e}")
            return []
    
    def obtener_todas_las_reservas(self):
        """
        Obtiene todas las reservas sin filtros.
        
        Returns:
            list: Lista de todas las reservas
        """
        try:
            return get_reservas_db(self.conn)
        except Exception as e:
            st.error(f"Error al obtener todas las reservas: {e}")
            return []
    
    def verificar_disponibilidad(self, cancha_id, fecha, hora_inicio, hora_fin, reserva_id_excluir=None):
        """
        Verifica si una cancha está disponible en un horario específico.
        
        Args:
            cancha_id (int): ID de la cancha
            fecha (date): Fecha de la reserva
            hora_inicio (time): Hora de inicio
            hora_fin (time): Hora de fin
            reserva_id_excluir (int): ID de reserva a excluir (para actualizaciones)
        
        Returns:
            bool: True si está disponible, False si hay conflicto
        """
        try:
            return verificar_disponibilidad_db(self.conn, cancha_id, fecha, hora_inicio, hora_fin, reserva_id_excluir)
        except Exception as e:
            st.error(f"Error al verificar disponibilidad: {e}")
            return False
    
    def limpiar_reservas_antiguas(self, fecha_corte):
        """
        Ejecuta el procedimiento para limpiar reservas antiguas.
        
        Args:
            fecha_corte (date): Fecha de corte para eliminar reservas
        
        Returns:
            bool: True si el procedimiento se ejecutó correctamente
        """
        try:
            # Este procedimiento no está definido en capa_datos.reservas_data,
            # por lo que se asume que se ejecuta directamente o se maneja en capa_datos.
            # Si se necesita una lógica de limpieza más compleja, se debe implementar aquí.
            st.warning("La limpieza de reservas antiguas no está implementada en capa_datos.")
            return False
        except Exception as e:
            st.error(f"Error inesperado al limpiar reservas antiguas: {e}")
            return False
    
    def obtener_estadisticas_reservas(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas básicas de reservas.
        
        Args:
            fecha_inicio (date): Fecha de inicio (opcional)
            fecha_fin (date): Fecha de fin (opcional)
        
        Returns:
            dict: Estadísticas de reservas
        """
        try:
            reservas = self.obtener_reservas()
            
            # Filtrar por fecha si se especifica
            if fecha_inicio and fecha_fin:
                reservas = [r for r in reservas if fecha_inicio <= r['fecha_reserva'] <= fecha_fin]
            
            # Contar por estado
            estados_count = {}
            total_ingresos = 0
            
            for reserva in reservas:
                estado = reserva['estado']
                estados_count[estado] = estados_count.get(estado, 0) + 1
                
                if reserva.get('precio_total_calculado'):
                    total_ingresos += float(reserva['precio_total_calculado'])
            
            return {
                'total_reservas': len(reservas),
                'por_estado': estados_count,
                'total_ingresos': total_ingresos,
                'promedio_por_reserva': total_ingresos / len(reservas) if reservas else 0
            }
        except Exception as e:
            st.error(f"Error al obtener estadísticas de reservas: {e}")
            return {
                'total_reservas': 0,
                'por_estado': {},
                'total_ingresos': 0,
                'promedio_por_reserva': 0
            }
    
    def obtener_horarios_disponibles(self, cancha_id, fecha):
        """
        Obtiene los horarios disponibles para una cancha en una fecha específica.
        
        Args:
            cancha_id (int): ID de la cancha
            fecha (date): Fecha para verificar
        
        Returns:
            list: Lista de horarios disponibles
        """
        try:
            # Obtener reservas existentes para esa fecha y cancha
            reservas_fecha = self.obtener_reservas_por_fecha(fecha)
            reservas_cancha = [r for r in reservas_fecha if r['cancha_id'] == cancha_id and r['estado'] in ['confirmada', 'pendiente']]
            
            # Generar horarios disponibles (cada 30 minutos)
            horarios_disponibles = []
            hora_actual = self.hora_minima
            
            while hora_actual < self.hora_maxima:
                hora_fin = datetime.strptime(f"{hora_actual.hour}:{hora_actual.minute + 30}", '%H:%M').time()
                if hora_fin.minute >= 60:
                    hora_fin = datetime.strptime(f"{hora_actual.hour + 1}:{hora_fin.minute - 60}", '%H:%M').time()
                
                # Verificar si este horario está disponible
                disponible = True
                for reserva in reservas_cancha:
                    if (reserva['hora_inicio'] < hora_fin and reserva['hora_fin'] > hora_actual):
                        disponible = False
                        break
                
                if disponible:
                    horarios_disponibles.append({
                        'hora_inicio': hora_actual,
                        'hora_fin': hora_fin
                    })
                
                hora_actual = hora_fin
            
            return horarios_disponibles
            
        except Exception as e:
            st.error(f"Error al obtener horarios disponibles: {e}")
            return []

    def get_reservas_por_estado(self):
        """Obtener reservas agrupadas por estado"""
        try:
            reservas = self.obtener_reservas()
            
            # Agrupar por estado
            estados_count = {}
            for reserva in reservas:
                estado = reserva['estado']
                estados_count[estado] = estados_count.get(estado, 0) + 1
            
            # Convertir a formato de lista para el dashboard
            result = []
            for estado, cantidad in estados_count.items():
                result.append({
                    'estado': estado.capitalize(),
                    'cantidad': cantidad
                })
            
            return result
            
        except Exception as e:
            st.error(f"Error al obtener reservas por estado: {e}")
            return []
    
    def get_ocupacion_por_cancha(self):
        """Obtener ocupación de canchas en los últimos 30 días"""
        try:
            from logica_negocio.canchas_logic import CanchasLogic
            canchas_logic = CanchasLogic()
            canchas = canchas_logic.get_all_canchas()
            
            fecha_inicio = datetime.now().date() - timedelta(days=30)
            fecha_fin = datetime.now().date()
            
            result = []
            for cancha in canchas:
                # Obtener reservas para esta cancha en el período
                reservas_cancha = self.obtener_reservas_por_cancha(cancha['id'])
                reservas_periodo = [r for r in reservas_cancha 
                                  if fecha_inicio <= r['fecha_reserva'] <= fecha_fin]
                
                result.append({
                    'nombre_cancha': cancha['nombre'],
                    'tipo_deporte': cancha['tipo_deporte'],
                    'reservas_totales': len(reservas_periodo)
                })
            
            return result
            
        except Exception as e:
            st.error(f"Error al obtener ocupación por cancha: {e}")
            return []
    
    def get_reservas_recientes(self, limit=10):
        """Obtener reservas recientes"""
        try:
            reservas = self.obtener_reservas()
            
            # Ordenar por fecha de creación (más recientes primero)
            reservas_ordenadas = sorted(reservas, 
                                      key=lambda x: x.get('fecha_creacion', ''), 
                                      reverse=True)
            
            # Limitar resultados
            return reservas_ordenadas[:limit]
            
        except Exception as e:
            st.error(f"Error al obtener reservas recientes: {e}")
            return []
    
    def get_reservas_filtradas(self, fecha_inicio=None, fecha_fin=None, estado=None):
        """Obtener reservas con filtros"""
        try:
            reservas = self.obtener_reservas()
            
            # Aplicar filtros
            if fecha_inicio and fecha_fin:
                reservas = [r for r in reservas 
                          if fecha_inicio <= r['fecha_reserva'] <= fecha_fin]
            
            if estado:
                reservas = [r for r in reservas if r['estado'] == estado.lower()]
            
            return reservas
            
        except Exception as e:
            st.error(f"Error al obtener reservas filtradas: {e}")
            return []
    
    def get_reserva_by_id(self, reserva_id):
        """Obtener reserva por ID"""
        try:
            return self.obtener_reserva_por_id(reserva_id)
        except Exception as e:
            st.error(f"Error al obtener reserva por ID: {e}")
            return None
    
    def get_reservas_pendientes_pago(self):
        """Obtener reservas pendientes de pago"""
        try:
            # Obtener todas las reservas
            reservas = self.obtener_reservas()
            
            # Filtrar reservas confirmadas que no tienen pagos completos
            reservas_pendientes = []
            for reserva in reservas:
                if reserva['estado'] in ['confirmada', 'pendiente']:
                    # Verificar si la reserva tiene pagos completos
                    # Por ahora, asumimos que todas las reservas confirmadas están pendientes de pago
                    # En una implementación más completa, se verificaría contra la tabla de pagos
                    reservas_pendientes.append(reserva)
            
            return reservas_pendientes
            
        except Exception as e:
            st.error(f"Error al obtener reservas pendientes de pago: {e}")
            return []
    
    def crear_reserva_completa(self, datos_reserva):
        """Crear nueva reserva con datos completos"""
        try:
            return self.crear_reserva(
                cliente_id=datos_reserva['cliente_id'],
                cancha_id=datos_reserva['cancha_id'],
                fecha_reserva=datos_reserva['fecha_reserva'],
                hora_inicio=datos_reserva['hora_inicio'],
                hora_fin=datos_reserva['hora_fin'],
                observaciones=datos_reserva.get('observaciones')
            )
        except Exception as e:
            st.error(f"Error al crear reserva: {e}")
            return {'success': False, 'message': str(e)}
    
    def actualizar_reserva_completa(self, reserva_id, datos_actualizados):
        """Actualizar reserva con datos completos"""
        try:
            return self.actualizar_reserva(
                reserva_id=reserva_id,
                cliente_id=datos_actualizados['cliente_id'],
                cancha_id=datos_actualizados['cancha_id'],
                fecha_reserva=datos_actualizados['fecha_reserva'],
                hora_inicio=datos_actualizados['hora_inicio'],
                hora_fin=datos_actualizados['hora_fin'],
                observaciones=datos_actualizados.get('observaciones', ''),
                estado=datos_actualizados.get('estado', 'pendiente')
            )
        except Exception as e:
            st.error(f"Error al actualizar reserva: {e}")
            return {'success': False, 'message': str(e)}
    
    def cancelar_reserva_completa(self, reserva_id, motivo_cancelacion):
        """Cancelar reserva con motivo"""
        try:
            # Para cancelar, necesitamos el cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin
            # Esto requiere obtener la reserva actual para extraer estos datos.
            reserva_actual = self.obtener_reserva_por_id(reserva_id)
            if not reserva_actual:
                st.error("❌ La reserva especificada no existe")
                return {'success': False, 'message': "Reserva no encontrada"}

            return self.cancelar_reserva(
                reserva_id=reserva_id,
                cliente_id=reserva_actual['cliente_id'],
                cancha_id=reserva_actual['cancha_id'],
                fecha_reserva=reserva_actual['fecha_reserva'],
                hora_inicio=reserva_actual['hora_inicio'],
                hora_fin=reserva_actual['hora_fin']
            )
        except Exception as e:
            st.error(f"Error al cancelar reserva: {e}")
            return {'success': False, 'message': str(e)}

# Instancia global de la lógica de reservas
reservas_logic = ReservasLogic() 