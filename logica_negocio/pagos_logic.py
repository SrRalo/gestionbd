import streamlit as st
import psycopg2
from datetime import datetime, date, timedelta
from capa_datos.database_connection import get_db_connection

class PagosLogic:
    """
    Lógica de negocio para la gestión de pagos.
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
    
    def obtener_pagos(self):
        """
        Obtiene todos los pagos.
        
        Returns:
            list: Lista de pagos
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pagos
            cur.execute("""
                SELECT p.id, p.reserva_id, p.cliente_id, p.monto, p.metodo_pago,
                       p.estado, p.observaciones, p.fecha_pago, p.fecha_creacion,
                       p.fecha_actualizacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                ORDER BY p.fecha_pago DESC
            """)
            
            pagos = cur.fetchall()
            cur.close()
            
            return pagos
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pagos: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_pago_por_id(self, pago_id):
        """
        Obtiene un pago específico por su ID.
        
        Args:
            pago_id (int): ID del pago
        
        Returns:
            tuple or None: Datos del pago o None si no se encuentra
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pago por ID
            cur.execute("""
                SELECT p.id, p.reserva_id, p.cliente_id, p.monto, p.metodo_pago,
                       p.estado, p.observaciones, p.fecha_pago, p.fecha_creacion,
                       p.fecha_actualizacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                WHERE p.id = %s
            """, (pago_id,))
            
            pago = cur.fetchone()
            cur.close()
            
            return pago
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pago por ID: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def crear_pago(self, reserva_id, monto, metodo_pago, observaciones=None):
        """
        Crea un nuevo pago.
        
        Args:
            reserva_id (int): ID de la reserva
            monto (float): Monto del pago
            metodo_pago (str): Método de pago
            observaciones (str, optional): Observaciones del pago
            
        Returns:
            int or None: ID del pago creado o None si falla
        """
        conn = None
        try:
            # Validaciones
            if monto <= 0:
                self._log_error("El monto debe ser mayor a 0")
                return None
            
            if not metodo_pago:
                self._log_error("El método de pago es obligatorio")
                return None
            
            conn = get_db_connection()
            if not conn:
                return None
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL registrar_pago
            cur.execute("""
                SELECT registrar_pago(%s, %s, %s, %s)
            """, (reserva_id, monto, metodo_pago, observaciones))
            
            pago_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return pago_id
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al crear pago: {error}")
            return None
        finally:
            if conn:
                conn.close()
    
    def actualizar_pago(self, pago_id, monto, metodo_pago, estado, observaciones=None):
        """
        Actualiza un pago existente.
        
        Args:
            pago_id (int): ID del pago
            monto (float): Nuevo monto
            metodo_pago (str): Nuevo método de pago
            estado (str): Nuevo estado
            observaciones (str, optional): Nuevas observaciones
            
        Returns:
            bool: True si se actualizó correctamente, False en caso contrario
        """
        conn = None
        try:
            # Validaciones
            if monto <= 0:
                self._log_error("El monto debe ser mayor a 0")
                return False
            
            if not metodo_pago:
                self._log_error("El método de pago es obligatorio")
                return False
            
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL actualizar_pago
            cur.execute("""
                SELECT actualizar_pago(%s, %s, %s, %s, %s)
            """, (pago_id, monto, metodo_pago, estado, observaciones))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al actualizar pago: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def eliminar_pago(self, pago_id):
        """
        Elimina un pago.
        
        Args:
            pago_id (int): ID del pago
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Llamada directa a la función SQL eliminar_pago
            cur.execute("""
                SELECT eliminar_pago(%s)
            """, (pago_id,))
            
            resultado = cur.fetchone()[0]
            conn.commit()
            cur.close()
            
            return resultado
            
        except (Exception, psycopg2.DatabaseError) as error:
            if conn:
                conn.rollback()
            self._log_error(f"Error al eliminar pago: {error}")
            return False
        finally:
            if conn:
                conn.close()
    
    def obtener_pagos_por_cliente(self, cliente_id):
        """
        Obtiene todos los pagos de un cliente específico.
        
        Args:
            cliente_id (int): ID del cliente
            
        Returns:
            list: Lista de pagos del cliente
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pagos por cliente
            cur.execute("""
                SELECT p.id, p.reserva_id, p.monto, p.metodo_pago, p.estado,
                       p.observaciones, p.fecha_pago, p.fecha_creacion,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                WHERE p.cliente_id = %s
                ORDER BY p.fecha_pago DESC
            """, (cliente_id,))
            
            pagos = cur.fetchall()
            cur.close()
            
            return pagos
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pagos por cliente: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_pagos_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Obtiene pagos en un rango de fechas.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            
        Returns:
            list: Lista de pagos en el rango de fechas
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pagos por fecha
            cur.execute("""
                SELECT p.id, p.reserva_id, p.cliente_id, p.monto, p.metodo_pago,
                       p.estado, p.observaciones, p.fecha_pago, p.fecha_creacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                WHERE p.fecha_pago BETWEEN %s AND %s
                ORDER BY p.fecha_pago DESC
            """, (fecha_inicio, fecha_fin))
            
            pagos = cur.fetchall()
            cur.close()
            
            return pagos
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pagos por fecha: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_estadisticas_pagos(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas de pagos.
        
        Args:
            fecha_inicio (date, optional): Fecha de inicio para el filtro
            fecha_fin (date, optional): Fecha de fin para el filtro
            
        Returns:
            dict: Estadísticas de pagos
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
                        COUNT(*) as total_pagos,
                        COALESCE(SUM(monto), 0) as total_recaudado,
                        AVG(monto) as promedio_pago,
                        COUNT(CASE WHEN estado = 'Completado' THEN 1 END) as pagos_completados,
                        COUNT(CASE WHEN estado = 'Pendiente' THEN 1 END) as pagos_pendientes,
                        COUNT(CASE WHEN metodo_pago = 'Efectivo' THEN 1 END) as pagos_efectivo,
                        COUNT(CASE WHEN metodo_pago = 'Tarjeta de Crédito' THEN 1 END) as pagos_tarjeta_credito,
                        COUNT(CASE WHEN metodo_pago = 'Tarjeta de Débito' THEN 1 END) as pagos_tarjeta_debito,
                        COUNT(CASE WHEN metodo_pago = 'Transferencia Bancaria' THEN 1 END) as pagos_transferencia,
                        COUNT(CASE WHEN metodo_pago = 'Pago Móvil' THEN 1 END) as pagos_movil
                    FROM pagos
                    WHERE fecha_pago BETWEEN %s AND %s
                """, (fecha_inicio, fecha_fin))
            else:
                # Consulta SQL directa sin filtro de fechas
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_pagos,
                        COALESCE(SUM(monto), 0) as total_recaudado,
                        AVG(monto) as promedio_pago,
                        COUNT(CASE WHEN estado = 'Completado' THEN 1 END) as pagos_completados,
                        COUNT(CASE WHEN estado = 'Pendiente' THEN 1 END) as pagos_pendientes,
                        COUNT(CASE WHEN metodo_pago = 'Efectivo' THEN 1 END) as pagos_efectivo,
                        COUNT(CASE WHEN metodo_pago = 'Tarjeta de Crédito' THEN 1 END) as pagos_tarjeta_credito,
                        COUNT(CASE WHEN metodo_pago = 'Tarjeta de Débito' THEN 1 END) as pagos_tarjeta_debito,
                        COUNT(CASE WHEN metodo_pago = 'Transferencia Bancaria' THEN 1 END) as pagos_transferencia,
                        COUNT(CASE WHEN metodo_pago = 'Pago Móvil' THEN 1 END) as pagos_movil
                    FROM pagos
                """)
            
            stats = cur.fetchone()
            cur.close()
            
            return {
                'total_pagos': stats[0],
                'total_recaudado': float(stats[1]) if stats[1] else 0,
                'promedio_pago': float(stats[2]) if stats[2] else 0,
                'pagos_completados': stats[3],
                'pagos_pendientes': stats[4],
                'pagos_efectivo': stats[5],
                'pagos_tarjeta_credito': stats[6],
                'pagos_tarjeta_debito': stats[7],
                'pagos_transferencia': stats[8],
                'pagos_movil': stats[9]
            }
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener estadísticas de pagos: {error}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def obtener_reservas_sin_pago(self):
        """
        Obtiene reservas que no tienen pagos registrados.
        
        Returns:
            list: Lista de reservas sin pago
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener reservas sin pago
            cur.execute("""
                SELECT r.id, r.cliente_id, r.cancha_id, r.fecha_reserva, r.hora_inicio,
                       r.hora_fin, r.duracion, r.estado, r.fecha_creacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       ca.nombre as nombre_cancha, ca.precio_hora,
                       (r.duracion * ca.precio_hora) as precio_total
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.id
                JOIN canchas ca ON r.cancha_id = ca.id
                WHERE r.estado IN ('confirmada', 'completada')
                AND NOT EXISTS (
                    SELECT 1 FROM pagos p 
                    WHERE p.reserva_id = r.id 
                    AND p.estado = 'Completado'
                )
                ORDER BY r.fecha_reserva DESC
            """)
            
            reservas = cur.fetchall()
            cur.close()
            
            return reservas
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener reservas sin pago: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def calcular_saldo_pendiente_reserva(self, reserva_id):
        """
        Calcula el saldo pendiente de una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            float: Saldo pendiente
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return 0.0
            
            cur = conn.cursor()
            
            # Consulta SQL directa para calcular saldo pendiente
            cur.execute("""
                SELECT 
                    COALESCE(r.duracion * ca.precio_hora, 0) as precio_total,
                    COALESCE(SUM(p.monto), 0) as total_pagado
                FROM reservas r
                JOIN canchas ca ON r.cancha_id = ca.id
                LEFT JOIN pagos p ON r.id = p.reserva_id AND p.estado = 'Completado'
                WHERE r.id = %s
                GROUP BY r.duracion, ca.precio_hora
            """, (reserva_id,))
            
            resultado = cur.fetchone()
            cur.close()
            
            if resultado:
                precio_total = float(resultado[0]) if resultado[0] else 0
                total_pagado = float(resultado[1]) if resultado[1] else 0
                return max(0, precio_total - total_pagado)
            
            return 0.0
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al calcular saldo pendiente: {error}")
            return 0.0
        finally:
            if conn:
                conn.close()
    
    def get_ingresos_periodo(self, fecha_inicio, fecha_fin):
        """
        Obtiene los ingresos de un período específico.
        
        Args:
            fecha_inicio (datetime): Fecha de inicio
            fecha_fin (datetime): Fecha de fin
        
        Returns:
            list: Lista de pagos en el período
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Convertir fechas a string si son objetos datetime
            if isinstance(fecha_inicio, datetime):
                fecha_inicio_str = fecha_inicio.strftime('%Y-%m-%d')
            else:
                fecha_inicio_str = fecha_inicio
            if isinstance(fecha_fin, datetime):
                fecha_fin_str = fecha_fin.strftime('%Y-%m-%d')
            else:
                fecha_fin_str = fecha_fin
            
            # Consulta SQL directa para obtener pagos por fecha
            cur.execute("""
                SELECT p.id, p.reserva_id, p.cliente_id, p.monto, p.metodo_pago,
                       p.estado, p.observaciones, p.fecha_pago, p.fecha_creacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                WHERE p.fecha_pago BETWEEN %s AND %s
                ORDER BY p.fecha_pago DESC
            """, (fecha_inicio_str, fecha_fin_str))
            
            pagos_periodo = cur.fetchall()
            cur.close()
            
            return [p for p in pagos_periodo if p[10] == 'Completado'] # Usar índice 10 para 'estado'
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener ingresos del período: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_pagos_recientes(self, limit=10):
        """
        Obtiene los pagos más recientes.
        
        Args:
            limit (int): Número máximo de pagos a obtener
        
        Returns:
            list: Lista de pagos recientes
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pagos más recientes
            cur.execute("""
                SELECT p.id, p.reserva_id, p.cliente_id, p.monto, p.metodo_pago,
                       p.estado, p.observaciones, p.fecha_pago, p.fecha_creacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                ORDER BY p.fecha_pago DESC
                LIMIT %s
            """, (limit,))
            
            pagos_recientes = cur.fetchall()
            cur.close()
            
            return pagos_recientes
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pagos recientes: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_ingresos_mensuales(self):
        """
        Obtiene los ingresos de los últimos 12 meses.
        
        Returns:
            list: Lista de ingresos mensuales
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
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
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener ingresos mensuales: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
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
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pagos filtrados
            query = """
                SELECT p.id, p.reserva_id, p.cliente_id, p.monto, p.metodo_pago,
                       p.estado, p.observaciones, p.fecha_pago, p.fecha_creacion,
                       c.nombre as nombre_cliente, c.apellido as apellido_cliente,
                       r.fecha_reserva, r.hora_inicio, r.hora_fin,
                       ca.nombre as nombre_cancha
                FROM pagos p
                JOIN clientes c ON p.cliente_id = c.id
                LEFT JOIN reservas r ON p.reserva_id = r.id
                LEFT JOIN canchas ca ON r.cancha_id = ca.id
                ORDER BY p.fecha_pago DESC
            """
            
            params = []
            if fecha_inicio and fecha_fin:
                query += " WHERE p.fecha_pago BETWEEN %s AND %s"
                params.extend([fecha_inicio, fecha_fin])
            
            if cliente_id:
                if params:
                    query += " AND p.cliente_id = %s"
                else:
                    query += " WHERE p.cliente_id = %s"
                params.append(cliente_id)
            
            if estado:
                if params:
                    query += " AND p.estado = %s"
                else:
                    query += " WHERE p.estado = %s"
                params.append(estado)
            
            cur.execute(query, params)
            
            pagos_filtrados = cur.fetchall()
            cur.close()
            
            return pagos_filtrados
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pagos filtrados: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_resumen_mensual(self, mes, año):
        """
        Obtiene el resumen de pagos de un mes específico.
        
        Args:
            mes (int): Mes (1-12)
            año (int): Año
        
        Returns:
            dict: Resumen mensual
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return {
                    'total_ingresos': 0, 
                    'total_pagos': 0, 
                    'monto_total': 0,
                    'promedio_por_pago': 0,
                    'promedio_pago': 0,
                    'pagos_completados': 0
                }
            
            cur = conn.cursor()
            
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
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener resumen mensual: {error}")
            return {
                'total_ingresos': 0, 
                'total_pagos': 0, 
                'monto_total': 0,
                'promedio_por_pago': 0,
                'promedio_pago': 0,
                'pagos_completados': 0
            }
        finally:
            if conn:
                conn.close()
    
    def get_pagos_por_cliente(self):
        """
        Obtiene estadísticas de pagos por cliente.
        
        Returns:
            list: Lista de estadísticas por cliente
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener pagos por cliente
            cur.execute("""
                SELECT c.id as cliente_id, c.nombre, c.apellido,
                       COALESCE(SUM(p.monto), 0) as total_pagado,
                       COUNT(p.id) as total_pagos
                FROM clientes c
                LEFT JOIN pagos p ON c.id = p.cliente_id AND p.estado = 'Completado'
                GROUP BY c.id, c.nombre, c.apellido
                ORDER BY total_pagado DESC
            """)
            
            clientes_stats = cur.fetchall()
            cur.close()
            
            return [
                {
                    'cliente_id': row[0],
                    'nombre': f"{row[1]} {row[2]}",
                    'total_pagado': float(row[3]),
                    'total_pagos': row[4]
                } for row in clientes_stats
            ]
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener pagos por cliente: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_estadisticas_metodos_pago(self):
        """
        Obtiene estadísticas por método de pago.
        
        Returns:
            list: Lista de estadísticas por método
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
            # Consulta SQL directa para obtener estadísticas por método de pago
            cur.execute("""
                SELECT metodo_pago,
                       COALESCE(SUM(monto), 0) as total_pagado,
                       COUNT(p.id) as total_pagos
                FROM pagos p
                WHERE p.estado = 'Completado'
                GROUP BY metodo_pago
                ORDER BY total_pagado DESC
            """)
            
            metodos_stats = cur.fetchall()
            cur.close()
            
            return [
                {
                    'metodo': row[0],
                    'total_pagado': float(row[1]),
                    'total_pagos': row[2]
                } for row in metodos_stats
            ]
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener estadísticas de métodos de pago: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def get_tendencias_pagos(self):
        """
        Obtiene tendencias de pagos en el tiempo.
        
        Returns:
            list: Lista de tendencias
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return []
            
            cur = conn.cursor()
            
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
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener tendencias de pagos: {error}")
            return []
        finally:
            if conn:
                conn.close()
    
    def obtener_estadisticas_generales_pagos(self):
        """
        Obtiene estadísticas generales de pagos.
        
        Returns:
            dict: Estadísticas generales
        """
        conn = None
        try:
            conn = get_db_connection()
            if not conn:
                return {
                    'total_pagos': 0,
                    'total_monto': 0,
                    'promedio_por_pago': 0,
                    'por_metodo': {},
                    'por_estado': {}
                }
            
            cur = conn.cursor()
            
            # Estadísticas básicas
            cur.execute("""
                SELECT COUNT(p.id) as total_pagos,
                       COALESCE(SUM(p.monto), 0) as total_monto
                FROM pagos p
                WHERE p.estado = 'Completado'
            """)
            total_pagos_row = cur.fetchone()
            total_pagos = total_pagos_row[0] if total_pagos_row else 0
            total_monto = total_pagos_row[1] if total_pagos_row else 0
            
            # Contar por método de pago
            cur.execute("""
                SELECT metodo_pago, COUNT(p.id) as total_pagos_por_metodo
                FROM pagos p
                WHERE p.estado = 'Completado'
                GROUP BY metodo_pago
            """)
            metodos_count = {row[0]: row[1] for row in cur.fetchall()}
            
            # Contar por estado
            cur.execute("""
                SELECT estado, COUNT(p.id) as total_pagos_por_estado
                FROM pagos p
                WHERE p.estado = 'Completado'
                GROUP BY estado
            """)
            estados_count = {row[0]: row[1] for row in cur.fetchall()}
            
            cur.close()
            
            return {
                'total_pagos': total_pagos,
                'total_monto': total_monto,
                'promedio_por_pago': total_monto / total_pagos if total_pagos > 0 else 0,
                'por_metodo': metodos_count,
                'por_estado': estados_count
            }
            
        except (Exception, psycopg2.DatabaseError) as error:
            self._log_error(f"Error al obtener estadísticas generales de pagos: {error}")
            return {
                'total_pagos': 0,
                'total_monto': 0,
                'promedio_por_pago': 0,
                'por_metodo': {},
                'por_estado': {}
            }
        finally:
            if conn:
                conn.close()

# Instancia global de la lógica de pagos
pagos_logic = PagosLogic() 