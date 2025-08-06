import streamlit as st
from datetime import datetime, date, timedelta
from capa_datos.reports_data import (
    get_vista_reservas_completas_db, get_vista_estadisticas_canchas_db,
    get_estadisticas_generales_db, get_estadisticas_mensuales_db,
    get_estadisticas_semanales_db, get_top_clientes_db, get_top_canchas_db,
    get_estadisticas_horarios_db, get_estadisticas_dias_semana_db,
    get_canchas_mas_usadas_db, get_canchas_mas_recaudan_db
)
from logica_negocio.clientes_logic import clientes_logic
from logica_negocio.canchas_logic import canchas_logic
from logica_negocio.reservas_logic import reservas_logic
from logica_negocio.pagos_logic import pagos_logic

class ReportsLogic:
    """
    Lógica de negocio para reportes y estadísticas.
    """
    
    def __init__(self):
        self.conn = st.session_state.get('db_connection')
        self.pagos_logic = pagos_logic
    
    def obtener_dashboard_principal(self):
        """
        Obtiene los datos principales para el dashboard.
        
        Returns:
            dict: Datos del dashboard principal
        """
        try:
            # Estadísticas generales
            stats_generales = get_estadisticas_generales_db(self.conn)
            
            # Estadísticas de clientes
            stats_clientes = clientes_logic.obtener_estadisticas_clientes()
            
            # Estadísticas de canchas
            stats_canchas = canchas_logic.obtener_estadisticas_canchas()
            
            # Estadísticas de reservas
            stats_reservas = reservas_logic.obtener_estadisticas_reservas()
            
            # Estadísticas de pagos
            stats_pagos = self.pagos_logic.obtener_estadisticas_generales_pagos()
            
            # Reservas recientes (últimas 5)
            reservas_recientes = reservas_logic.obtener_reservas(solo_activas=True)[:5]
            
            # Pagos recientes (últimos 5)
            pagos_recientes = self.pagos_logic.obtener_pagos()[:5]
            
            return {
                'stats_generales': stats_generales,
                'stats_clientes': stats_clientes,
                'stats_canchas': stats_canchas,
                'stats_reservas': stats_reservas,
                'stats_pagos': stats_pagos,
                'reservas_recientes': reservas_recientes,
                'pagos_recientes': pagos_recientes
            }
        except Exception as e:
            st.error(f"Error al obtener datos del dashboard: {e}")
            return {}
    
    def obtener_vista_reservas_completas(self, fecha_inicio=None, fecha_fin=None, cliente_id=None, cancha_id=None):
        """
        Obtiene la vista de reservas completas con filtros.
        
        Args:
            fecha_inicio (date): Fecha de inicio para filtrar
            fecha_fin (date): Fecha de fin para filtrar
            cliente_id (int): ID del cliente para filtrar
            cancha_id (int): ID de la cancha para filtrar
        
        Returns:
            list: Lista de reservas completas
        """
        try:
            return get_vista_reservas_completas_db(self.conn, fecha_inicio, fecha_fin, cliente_id, cancha_id)
        except Exception as e:
            st.error(f"Error al obtener vista de reservas completas: {e}")
            return []
    
    def obtener_vista_estadisticas_canchas(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene la vista de estadísticas de canchas con filtros.
        
        Args:
            fecha_inicio (date): Fecha de inicio para filtrar
            fecha_fin (date): Fecha de fin para filtrar
        
        Returns:
            list: Lista de estadísticas de canchas
        """
        try:
            return get_vista_estadisticas_canchas_db(self.conn, fecha_inicio, fecha_fin)
        except Exception as e:
            st.error(f"Error al obtener vista de estadísticas de canchas: {e}")
            return []
    
    def obtener_estadisticas_mensuales(self, año=None):
        """
        Obtiene estadísticas mensuales.
        
        Args:
            año (int): Año para filtrar (opcional)
        
        Returns:
            list: Estadísticas mensuales
        """
        try:
            return get_estadisticas_mensuales_db(self.conn, año)
        except Exception as e:
            st.error(f"Error al obtener estadísticas mensuales: {e}")
            return []
    
    def obtener_estadisticas_semanales(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas semanales.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
        
        Returns:
            list: Estadísticas semanales
        """
        try:
            return get_estadisticas_semanales_db(self.conn, fecha_inicio, fecha_fin)
        except Exception as e:
            st.error(f"Error al obtener estadísticas semanales: {e}")
            return []
    
    def obtener_top_clientes(self, fecha_inicio=None, fecha_fin=None, limit=10):
        """
        Obtiene los clientes con más reservas.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            limit (int): Límite de clientes a retornar
        
        Returns:
            list: Top clientes
        """
        try:
            return get_top_clientes_db(self.conn, fecha_inicio, fecha_fin, limit)
        except Exception as e:
            st.error(f"Error al obtener top clientes: {e}")
            return []
    
    def obtener_top_canchas(self, fecha_inicio=None, fecha_fin=None, limit=10):
        """
        Obtiene las canchas más utilizadas.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            limit (int): Límite de canchas a retornar
        
        Returns:
            list: Top canchas
        """
        try:
            return get_top_canchas_db(self.conn, fecha_inicio, fecha_fin, limit)
        except Exception as e:
            st.error(f"Error al obtener top canchas: {e}")
            return []
    
    def obtener_estadisticas_horarios(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas por horarios.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
        
        Returns:
            list: Estadísticas por horarios
        """
        try:
            return get_estadisticas_horarios_db(self.conn, fecha_inicio, fecha_fin)
        except Exception as e:
            st.error(f"Error al obtener estadísticas por horarios: {e}")
            return []
    
    def obtener_estadisticas_dias_semana(self, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas por días de la semana.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
        
        Returns:
            list: Estadísticas por días de la semana
        """
        try:
            return get_estadisticas_dias_semana_db(self.conn, fecha_inicio, fecha_fin)
        except Exception as e:
            st.error(f"Error al obtener estadísticas por días de la semana: {e}")
            return []
    
    def obtener_canchas_mas_usadas(self, fecha_inicio=None, fecha_fin=None, limit=10):
        """
        Obtiene las canchas más utilizadas ordenadas de forma descendente.
        
        Args:
            fecha_inicio (date): Fecha de inicio para filtrar
            fecha_fin (date): Fecha de fin para filtrar
            limit (int): Límite de canchas a retornar
        
        Returns:
            list: Lista de canchas más utilizadas
        """
        try:
            return get_canchas_mas_usadas_db(self.conn, fecha_inicio, fecha_fin, limit)
        except Exception as e:
            st.error(f"Error al obtener canchas más utilizadas: {e}")
            return []
    
    def obtener_canchas_mas_recaudan(self, fecha_inicio=None, fecha_fin=None, limit=10):
        """
        Obtiene las canchas que más dinero recaudan ordenadas de forma descendente.
        
        Args:
            fecha_inicio (date): Fecha de inicio para filtrar
            fecha_fin (date): Fecha de fin para filtrar
            limit (int): Límite de canchas a retornar
        
        Returns:
            list: Lista de canchas que más recaudan
        """
        try:
            return get_canchas_mas_recaudan_db(self.conn, fecha_inicio, fecha_fin, limit)
        except Exception as e:
            st.error(f"Error al obtener canchas que más recaudan: {e}")
            return []
    
    def generar_reporte_reservas(self, fecha_inicio, fecha_fin, formato='resumen'):
        """
        Genera un reporte de reservas.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            formato (str): Formato del reporte ('resumen', 'detallado', 'completo')
        
        Returns:
            dict: Reporte de reservas
        """
        try:
            # Obtener datos básicos
            reservas = self.obtener_vista_reservas_completas(fecha_inicio, fecha_fin)
            
            # Estadísticas básicas
            total_reservas = len(reservas)
            total_ingresos = sum(float(r['precio_total_calculado']) for r in reservas if r.get('precio_total_calculado'))
            
            # Contar por estado
            estados_count = {}
            for reserva in reservas:
                estado = reserva['estado']
                estados_count[estado] = estados_count.get(estado, 0) + 1
            
            # Contar por tipo de cancha
            tipos_count = {}
            for reserva in reservas:
                tipo = reserva.get('tipo_cancha_nombre', 'Sin tipo')
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
            
            reporte = {
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                },
                'resumen': {
                    'total_reservas': total_reservas,
                    'total_ingresos': total_ingresos,
                    'promedio_por_reserva': total_ingresos / total_reservas if total_reservas > 0 else 0
                },
                'por_estado': estados_count,
                'por_tipo_cancha': tipos_count
            }
            
            # Agregar detalles si se solicita
            if formato in ['detallado', 'completo']:
                reporte['reservas'] = reservas
            
            # Agregar estadísticas adicionales si es completo
            if formato == 'completo':
                reporte['estadisticas_horarios'] = self.obtener_estadisticas_horarios(fecha_inicio, fecha_fin)
                reporte['estadisticas_dias'] = self.obtener_estadisticas_dias_semana(fecha_inicio, fecha_fin)
                reporte['top_clientes'] = self.obtener_top_clientes(fecha_inicio, fecha_fin, 5)
                reporte['top_canchas'] = self.obtener_top_canchas(fecha_inicio, fecha_fin, 5)
            
            return reporte
            
        except Exception as e:
            st.error(f"Error al generar reporte de reservas: {e}")
            return {}
    
    def generar_reporte_pagos(self, fecha_inicio, fecha_fin, formato='resumen'):
        """
        Genera un reporte de pagos.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            formato (str): Formato del reporte ('resumen', 'detallado', 'completo')
        
        Returns:
            dict: Reporte de pagos
        """
        try:
            # Obtener datos básicos
            pagos = self.pagos_logic.obtener_pagos_por_fecha(fecha_inicio, fecha_fin)
            
            # Estadísticas básicas
            total_pagos = len(pagos)
            total_monto = sum(float(p['monto']) for p in pagos if p['estado'] == 'confirmado')
            
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
            
            reporte = {
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                },
                'resumen': {
                    'total_pagos': total_pagos,
                    'total_monto': total_monto,
                    'promedio_por_pago': total_monto / total_pagos if total_pagos > 0 else 0
                },
                'por_metodo': metodos_count,
                'por_estado': estados_count
            }
            
            # Agregar detalles si se solicita
            if formato in ['detallado', 'completo']:
                reporte['pagos'] = pagos
            
            # Agregar estadísticas adicionales si es completo
            if formato == 'completo':
                reporte['estadisticas_detalladas'] = self.pagos_logic.obtener_estadisticas_pagos(fecha_inicio, fecha_fin)
                reporte['reservas_sin_pago'] = self.pagos_logic.obtener_reservas_sin_pago()
            
            return reporte
            
        except Exception as e:
            st.error(f"Error al generar reporte de pagos: {e}")
            return {}
    
    def generar_reporte_clientes(self, formato='resumen'):
        """
        Genera un reporte de clientes.
        
        Args:
            formato (str): Formato del reporte ('resumen', 'detallado', 'completo')
        
        Returns:
            dict: Reporte de clientes
        """
        try:
            # Obtener datos básicos
            clientes = clientes_logic.obtener_clientes()
            clientes_activos = clientes_logic.obtener_clientes(solo_activos=True)
            
            # Estadísticas básicas
            total_clientes = len(clientes)
            clientes_activos_count = len(clientes_activos)
            clientes_inactivos_count = total_clientes - clientes_activos_count
            
            # Contar por rango de edad (aproximado)
            rangos_edad = {
                '18-25': 0,
                '26-35': 0,
                '36-45': 0,
                '46-55': 0,
                '56+': 0
            }
            
            fecha_actual = date.today()
            for cliente in clientes:
                if cliente['fecha_nacimiento']:
                    edad = fecha_actual.year - cliente['fecha_nacimiento'].year
                    if fecha_actual < cliente['fecha_nacimiento'].replace(year=fecha_actual.year):
                        edad -= 1
                    
                    if edad < 26:
                        rangos_edad['18-25'] += 1
                    elif edad < 36:
                        rangos_edad['26-35'] += 1
                    elif edad < 46:
                        rangos_edad['36-45'] += 1
                    elif edad < 56:
                        rangos_edad['46-55'] += 1
                    else:
                        rangos_edad['56+'] += 1
            
            reporte = {
                'resumen': {
                    'total_clientes': total_clientes,
                    'clientes_activos': clientes_activos_count,
                    'clientes_inactivos': clientes_inactivos_count,
                    'porcentaje_activos': (clientes_activos_count / total_clientes * 100) if total_clientes > 0 else 0
                },
                'por_rango_edad': rangos_edad
            }
            
            # Agregar detalles si se solicita
            if formato in ['detallado', 'completo']:
                reporte['clientes'] = clientes
            
            # Agregar estadísticas adicionales si es completo
            if formato == 'completo':
                reporte['top_clientes'] = self.obtener_top_clientes(limit=10)
                reporte['clientes_nuevos_mes'] = self.obtener_clientes_nuevos_mes()
            
            return reporte
            
        except Exception as e:
            st.error(f"Error al generar reporte de clientes: {e}")
            return {}
    
    def obtener_clientes_nuevos_mes(self):
        """
        Obtiene los clientes registrados en el último mes.
        
        Returns:
            list: Clientes nuevos del mes
        """
        try:
            clientes = clientes_logic.obtener_clientes()
            fecha_limite = date.today() - timedelta(days=30)
            
            clientes_nuevos = [
                cliente for cliente in clientes 
                if cliente['fecha_registro'] and cliente['fecha_registro'].date() >= fecha_limite
            ]
            
            return clientes_nuevos
        except Exception as e:
            st.error(f"Error al obtener clientes nuevos del mes: {e}")
            return []
    
    def generar_reporte_completo_sistema(self, fecha_inicio, fecha_fin):
        """
        Genera un reporte completo del sistema.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
        
        Returns:
            dict: Reporte completo del sistema
        """
        try:
            reporte = {
                'periodo': {
                    'fecha_inicio': fecha_inicio,
                    'fecha_fin': fecha_fin
                },
                'dashboard': self.obtener_dashboard_principal(),
                'reservas': self.generar_reporte_reservas(fecha_inicio, fecha_fin, 'completo'),
                'pagos': self.generar_reporte_pagos(fecha_inicio, fecha_fin, 'completo'),
                'clientes': self.generar_reporte_clientes('completo'),
                'estadisticas_mensuales': self.obtener_estadisticas_mensuales(fecha_inicio.year),
                'estadisticas_semanales': self.obtener_estadisticas_semanales(fecha_inicio, fecha_fin),
                'estadisticas_horarios': self.obtener_estadisticas_horarios(fecha_inicio, fecha_fin),
                'estadisticas_dias': self.obtener_estadisticas_dias_semana(fecha_inicio, fecha_fin),
                'top_clientes': self.obtener_top_clientes(fecha_inicio, fecha_fin, 10),
                'top_canchas': self.obtener_top_canchas(fecha_inicio, fecha_fin, 10)
            }
            
            return reporte
            
        except Exception as e:
            st.error(f"Error al generar reporte completo del sistema: {e}")
            return {}

# Instancia global de la lógica de reportes
reports_logic = ReportsLogic() 