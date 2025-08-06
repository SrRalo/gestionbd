import streamlit as st
from datetime import datetime, date, timedelta
from capa_datos.pagos_data import (
    registrar_pago_db, get_pagos_db, get_pago_by_id_db, get_pagos_por_reserva_db,
    get_pagos_por_cliente_db, update_pago_db, delete_pago_db, get_pagos_por_fecha_db,
    get_estadisticas_pagos_db, get_reservas_sin_pago_db
)
from capa_datos.reservas_data import get_reserva_by_id_db

class PagosLogic:
    """
    Lógica de negocio para la gestión de pagos.
    """
    
    def __init__(self):
        self.conn = st.session_state.get('db_connection')
    
    def registrar_pago(self, reserva_id, monto, metodo_pago, observaciones=None):
        """
        Registra un nuevo pago.
        
        Args:
            reserva_id (int): ID de la reserva
            monto (float): Monto del pago
            metodo_pago (str): Método de pago
            observaciones (str): Observaciones del pago (opcional)
        
        Returns:
            bool: True si se registró correctamente, False en caso contrario
        """
        try:
            # Validar que la reserva existe
            reserva = get_reserva_by_id_db(self.conn, reserva_id)
            if not reserva:
                st.error("La reserva especificada no existe.")
                return False
            
            # Validar monto
            if monto <= 0:
                st.error("El monto debe ser mayor a 0.")
                return False
            
            # Verificar que el monto no exceda el precio de la reserva
            precio_reserva = float(reserva['precio_total_calculado']) if reserva.get('precio_total_calculado') else 0
            if monto > precio_reserva * 1.1:  # Permitir hasta 10% más por cargos adicionales
                st.warning(f"El monto ({monto}) excede significativamente el precio de la reserva ({precio_reserva}).")
            
            # Validar método de pago
            metodos_validos = ['Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia', 'Cheque']
            if metodo_pago not in metodos_validos:
                st.error(f"Método de pago no válido. Opciones válidas: {', '.join(metodos_validos)}")
                return False
            
            # Limpiar y validar observaciones
            observaciones = observaciones.strip() if observaciones else None
            
            # Registrar el pago
            if registrar_pago_db(self.conn, reserva_id, monto, metodo_pago, observaciones):
                st.success("✅ Pago registrado correctamente")
                return True
            else:
                st.error("❌ Error al registrar el pago")
                return False
                
        except Exception as e:
            st.error(f"Error al registrar pago: {e}")
            return False
    
    def obtener_pagos(self):
        """
        Obtiene todos los pagos.
        
        Returns:
            list: Lista de pagos
        """
        try:
            return get_pagos_db(self.conn)
        except Exception as e:
            st.error(f"Error al obtener pagos: {e}")
            return []
    
    def obtener_pago_por_id(self, pago_id):
        """
        Obtiene un pago específico por su ID.
        
        Args:
            pago_id (int): ID del pago
        
        Returns:
            dict: Datos del pago o None si no se encuentra
        """
        try:
            return get_pago_by_id_db(self.conn, pago_id)
        except Exception as e:
            st.error(f"Error al obtener pago: {e}")
            return None
    
    def obtener_pagos_por_reserva(self, reserva_id):
        """
        Obtiene todos los pagos de una reserva específica.
        
        Args:
            reserva_id (int): ID de la reserva
        
        Returns:
            list: Lista de pagos de la reserva
        """
        try:
            return get_pagos_por_reserva_db(self.conn, reserva_id)
        except Exception as e:
            st.error(f"Error al obtener pagos de la reserva: {e}")
            return []
    
    def obtener_pagos_por_cliente(self, cliente_id):
        """
        Obtiene todos los pagos de un cliente específico.
        
        Args:
            cliente_id (int): ID del cliente
        
        Returns:
            list: Lista de pagos del cliente
        """
        try:
            return get_pagos_por_cliente_db(self.conn, cliente_id)
        except Exception as e:
            st.error(f"Error al obtener pagos del cliente: {e}")
            return []
    
    def actualizar_pago(self, pago_id, monto, metodo_pago, estado, observaciones=None):
        """
        Actualiza un pago existente.
        
        Args:
            pago_id (int): ID del pago
            monto (float): Nuevo monto
            metodo_pago (str): Nuevo método de pago
            estado (str): Nuevo estado
            observaciones (str): Nuevas observaciones (opcional)
        
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        try:
            # Validar monto
            if monto <= 0:
                st.error("El monto debe ser mayor a 0.")
                return False
            
            # Validar método de pago
            metodos_validos = ['Efectivo', 'Tarjeta de Crédito', 'Tarjeta de Débito', 'Transferencia', 'Cheque']
            if metodo_pago not in metodos_validos:
                st.error(f"Método de pago no válido. Opciones válidas: {', '.join(metodos_validos)}")
                return False
            
            # Validar estado
            estados_validos = ['Pendiente', 'Completado', 'Cancelado', 'Reembolsado']
            if estado not in estados_validos:
                st.error(f"Estado no válido. Opciones válidas: {', '.join(estados_validos)}")
                return False
            
            # Limpiar observaciones
            observaciones = observaciones.strip() if observaciones else None
            
            # Actualizar el pago
            if update_pago_db(self.conn, pago_id, monto, metodo_pago, estado, observaciones):
                st.success("✅ Pago actualizado correctamente")
                return True
            else:
                st.error("❌ Error al actualizar el pago")
                return False
                
        except Exception as e:
            st.error(f"Error al actualizar pago: {e}")
            return False
    
    def eliminar_pago(self, pago_id):
        """
        Elimina un pago.
        
        Args:
            pago_id (int): ID del pago a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            if delete_pago_db(self.conn, pago_id):
                st.success("✅ Pago eliminado correctamente")
                return True
            else:
                st.error("❌ Error al eliminar el pago")
                return False
        except Exception as e:
            st.error(f"Error al eliminar pago: {e}")
            return False
    
    def obtener_pagos_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Obtiene pagos en un rango de fechas.
        
        Args:
            fecha_inicio (str): Fecha de inicio (YYYY-MM-DD)
            fecha_fin (str): Fecha de fin (YYYY-MM-DD)
        
        Returns:
            list: Lista de pagos en el rango de fechas
        """
        try:
            return get_pagos_por_fecha_db(self.conn, fecha_inicio, fecha_fin)
        except Exception as e:
            st.error(f"Error al obtener pagos por fecha: {e}")
            return []
    
    def obtener_estadisticas_pagos(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas de pagos.
        
        Args:
            fecha_inicio (str): Fecha de inicio (YYYY-MM-DD) (opcional)
            fecha_fin (str): Fecha de fin (YYYY-MM-DD) (opcional)
        
        Returns:
            dict: Estadísticas de pagos
        """
        try:
            return get_estadisticas_pagos_db(self.conn, fecha_inicio, fecha_fin)
        except Exception as e:
            st.error(f"Error al obtener estadísticas de pagos: {e}")
            return {}
    
    def obtener_reservas_sin_pago(self):
        """
        Obtiene las reservas que no tienen pagos registrados.
        
        Returns:
            list: Lista de reservas sin pagos
        """
        try:
            return get_reservas_sin_pago_db(self.conn)
        except Exception as e:
            st.error(f"Error al obtener reservas sin pago: {e}")
            return []
    
    def calcular_saldo_pendiente_reserva(self, reserva_id):
        """
        Calcula el saldo pendiente de una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
        
        Returns:
            float: Saldo pendiente
        """
        try:
            # Obtener la reserva
            reserva = get_reserva_by_id_db(self.conn, reserva_id)
            if not reserva:
                return 0
            
            # Obtener el precio total de la reserva
            precio_total = float(reserva.get('precio_total_calculado', 0))
            
            # Obtener los pagos de la reserva
            pagos = get_pagos_por_reserva_db(self.conn, reserva_id)
            
            # Calcular el total pagado
            total_pagado = sum(float(pago['monto']) for pago in pagos if pago['estado'] == 'Completado')
            
            # Calcular saldo pendiente
            saldo_pendiente = precio_total - total_pagado
            
            return max(0, saldo_pendiente)
            
        except Exception as e:
            st.error(f"Error al calcular saldo pendiente: {e}")
            return 0
    
    def get_ingresos_periodo(self, fecha_inicio, fecha_fin):
        """
        Obtiene los ingresos de un período específico.
        
        Args:
            fecha_inicio (datetime): Fecha de inicio
            fecha_fin (datetime): Fecha de fin
        
        Returns:
            list: Lista de pagos en el período
        """
        try:
            # Convertir fechas a string si son objetos datetime
            if isinstance(fecha_inicio, datetime):
                fecha_inicio = fecha_inicio.strftime('%Y-%m-%d')
            if isinstance(fecha_fin, datetime):
                fecha_fin = fecha_fin.strftime('%Y-%m-%d')
            
            pagos_periodo = get_pagos_por_fecha_db(self.conn, fecha_inicio, fecha_fin)
            return [p for p in pagos_periodo if p['estado'] == 'Completado']
        except Exception as e:
            st.error(f"Error al obtener ingresos del período: {e}")
            return []
    
    def get_pagos_recientes(self, limit=10):
        """
        Obtiene los pagos más recientes.
        
        Args:
            limit (int): Número máximo de pagos a obtener
        
        Returns:
            list: Lista de pagos recientes
        """
        try:
            pagos = get_pagos_db(self.conn)
            
            # Ordenar por fecha de pago (más recientes primero)
            pagos_ordenados = sorted(pagos, 
                                   key=lambda x: x.get('fecha_pago', ''), 
                                   reverse=True)
            
            # Limitar resultados
            return pagos_ordenados[:limit]
            
        except Exception as e:
            st.error(f"Error al obtener pagos recientes: {e}")
            return []
    
    def get_ingresos_mensuales(self):
        """
        Obtiene los ingresos de los últimos 12 meses.
        
        Returns:
            list: Lista de ingresos mensuales
        """
        try:
            result = []
            for i in range(12):
                fecha = datetime.now() - timedelta(days=30*i)
                mes = fecha.strftime('%Y-%m')
                
                # Obtener pagos del mes
                fecha_inicio = fecha.replace(day=1)
                fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                pagos_mes = self.get_ingresos_periodo(fecha_inicio, fecha_fin)
                ingresos_mes = sum(float(p['monto']) for p in pagos_mes if p['estado'] == 'Completado')
                
                result.append({
                    'mes': fecha.strftime('%B %Y'),
                    'ingresos': ingresos_mes
                })
            
            return result[::-1]  # Invertir para mostrar cronológicamente
            
        except Exception as e:
            st.error(f"Error al obtener ingresos mensuales: {e}")
            return []
    
    # Métodos adicionales para pagos_view.py
    def get_pagos_filtrados(self, fecha_inicio=None, fecha_fin=None, cliente_id=None, estado=None):
        """
        Obtiene pagos filtrados por diferentes criterios.
        
        Args:
            fecha_inicio (str): Fecha de inicio (opcional)
            fecha_fin (str): Fecha de fin (opcional)
            cliente_id (int): ID del cliente (opcional)
            estado (str): Estado del pago (opcional)
        
        Returns:
            list: Lista de pagos filtrados
        """
        try:
            pagos = get_pagos_db(self.conn)
            
            # Aplicar filtros
            if fecha_inicio and fecha_fin:
                pagos = [p for p in pagos if fecha_inicio <= p.get('fecha_pago', '') <= fecha_fin]
            
            if cliente_id:
                pagos = [p for p in pagos if p.get('cliente_id') == cliente_id]
            
            if estado:
                pagos = [p for p in pagos if p.get('estado') == estado]
            
            return pagos
        except Exception as e:
            st.error(f"Error al obtener pagos filtrados: {e}")
            return []
    
    def crear_pago(self, datos_pago):
        """
        Crea un nuevo pago.
        
        Args:
            datos_pago (dict): Datos del pago a crear
        
        Returns:
            bool: True si se creó correctamente
        """
        try:
            return self.registrar_pago(
                datos_pago['reserva_id'],
                datos_pago['monto'],
                datos_pago['metodo_pago'],
                datos_pago.get('observaciones')
            )
        except Exception as e:
            st.error(f"Error al crear pago: {e}")
            return False
    
    def get_pago_by_id(self, pago_id):
        """
        Obtiene un pago por su ID.
        
        Args:
            pago_id (int): ID del pago
        
        Returns:
            dict: Datos del pago
        """
        return self.obtener_pago_por_id(pago_id)
    
    def get_resumen_mensual(self, mes, año):
        """
        Obtiene el resumen de pagos de un mes específico.
        
        Args:
            mes (int): Mes (1-12)
            año (int): Año
        
        Returns:
            dict: Resumen mensual
        """
        try:
            fecha_inicio = datetime(año, mes, 1)
            if mes == 12:
                fecha_fin = datetime(año + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = datetime(año, mes + 1, 1) - timedelta(days=1)
            
            pagos_mes = self.get_ingresos_periodo(fecha_inicio, fecha_fin)
            
            total_ingresos = sum(float(p['monto']) for p in pagos_mes)
            total_pagos = len(pagos_mes)
            
            # Contar pagos completados
            pagos_completados = len([p for p in pagos_mes if p.get('estado') == 'Completado'])
            
            return {
                'total_ingresos': total_ingresos,
                'total_pagos': total_pagos,
                'monto_total': total_ingresos,  # Alias para compatibilidad
                'promedio_por_pago': total_ingresos / total_pagos if total_pagos > 0 else 0,
                'promedio_pago': total_ingresos / total_pagos if total_pagos > 0 else 0,  # Alias para compatibilidad
                'pagos_completados': pagos_completados
            }
        except Exception as e:
            st.error(f"Error al obtener resumen mensual: {e}")
            return {
                'total_ingresos': 0, 
                'total_pagos': 0, 
                'monto_total': 0,
                'promedio_por_pago': 0,
                'promedio_pago': 0,
                'pagos_completados': 0
            }
    
    def get_pagos_por_cliente(self):
        """
        Obtiene estadísticas de pagos por cliente.
        
        Returns:
            list: Lista de estadísticas por cliente
        """
        try:
            pagos = get_pagos_db(self.conn)
            
            # Agrupar por cliente
            clientes_stats = {}
            for pago in pagos:
                cliente_id = pago.get('cliente_id')
                if cliente_id not in clientes_stats:
                    clientes_stats[cliente_id] = {
                        'cliente_id': cliente_id,
                        'nombre': f"{pago.get('cliente_nombre', '')} {pago.get('cliente_apellido', '')}",
                        'total_pagado': 0,
                        'total_pagos': 0
                    }
                
                if pago.get('estado') == 'Completado':
                    clientes_stats[cliente_id]['total_pagado'] += float(pago.get('monto', 0))
                clientes_stats[cliente_id]['total_pagos'] += 1
            
            return list(clientes_stats.values())
        except Exception as e:
            st.error(f"Error al obtener pagos por cliente: {e}")
            return []
    
    def get_estadisticas_metodos_pago(self):
        """
        Obtiene estadísticas por método de pago.
        
        Returns:
            list: Lista de estadísticas por método
        """
        try:
            pagos = get_pagos_db(self.conn)
            
            # Agrupar por método de pago
            metodos_stats = {}
            for pago in pagos:
                metodo = pago.get('metodo_pago')
                if metodo not in metodos_stats:
                    metodos_stats[metodo] = {
                        'metodo': metodo,
                        'total_pagado': 0,
                        'total_pagos': 0
                    }
                
                if pago.get('estado') == 'Completado':
                    metodos_stats[metodo]['total_pagado'] += float(pago.get('monto', 0))
                metodos_stats[metodo]['total_pagos'] += 1
            
            return list(metodos_stats.values())
        except Exception as e:
            st.error(f"Error al obtener estadísticas de métodos de pago: {e}")
            return []
    
    def get_tendencias_pagos(self):
        """
        Obtiene tendencias de pagos en el tiempo.
        
        Returns:
            list: Lista de tendencias
        """
        try:
            # Obtener datos de los últimos 6 meses
            tendencias = []
            for i in range(6):
                fecha = datetime.now() - timedelta(days=30*i)
                mes = fecha.strftime('%Y-%m')
                
                fecha_inicio = fecha.replace(day=1)
                fecha_fin = (fecha_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                pagos_mes = self.get_ingresos_periodo(fecha_inicio, fecha_fin)
                ingresos_mes = sum(float(p['monto']) for p in pagos_mes)
                
                tendencias.append({
                    'mes': fecha.strftime('%B %Y'),
                    'fecha': fecha.strftime('%Y-%m'),
                    'ingresos': ingresos_mes,
                    'monto_total': ingresos_mes,  # Alias para compatibilidad
                    'cantidad_pagos': len(pagos_mes)
                })
            
            return tendencias[::-1]  # Invertir para mostrar cronológicamente
        except Exception as e:
            st.error(f"Error al obtener tendencias de pagos: {e}")
            return []
    
    def obtener_estadisticas_generales_pagos(self):
        """
        Obtiene estadísticas generales de pagos.
        
        Returns:
            dict: Estadísticas generales
        """
        try:
            pagos = get_pagos_db(self.conn)
            
            # Estadísticas básicas
            total_pagos = len(pagos)
            total_monto = sum(float(pago['monto']) for pago in pagos if pago['estado'] == 'Completado')
            
            # Contar por método de pago
            metodos_count = {}
            for pago in pagos:
                metodo = pago['metodo_pago']
                metodos_count[metodo] = metodos_count.get(metodo, 0) + 1
            
            # Contar por estado
            estados_count = {}
            for pago in pagos:
                estado = pago['estado']
                estados_count[estado] = estados_count.get(estado, 0) + 1
            
            return {
                'total_pagos': total_pagos,
                'total_monto': total_monto,
                'promedio_por_pago': total_monto / total_pagos if total_pagos > 0 else 0,
                'por_metodo': metodos_count,
                'por_estado': estados_count
            }
        except Exception as e:
            st.error(f"Error al obtener estadísticas generales de pagos: {e}")
            return {
                'total_pagos': 0,
                'total_monto': 0,
                'promedio_por_pago': 0,
                'por_metodo': {},
                'por_estado': {}
            }

# Instancia global de la lógica de pagos
pagos_logic = PagosLogic() 