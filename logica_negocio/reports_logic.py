import streamlit as st
from datetime import datetime, date, timedelta
from capa_datos.reports_data import (
    get_vista_reservas_completas_db,
    get_vista_estadisticas_canchas_db,
    get_estadisticas_generales_db,
    get_estadisticas_mensuales_db,
    get_estadisticas_semanales_db,
    get_top_clientes_db,
    get_top_canchas_db,
    get_estadisticas_horarios_db,
    get_estadisticas_dias_semana_db,
    get_canchas_mas_usadas_db,
    get_canchas_mas_recaudan_db,
    generar_estadisticas_procedimiento_db
)
from logica_negocio.clientes_logic import clientes_logic
from logica_negocio.canchas_logic import canchas_logic
from logica_negocio.reservas_logic import reservas_logic
from logica_negocio.pagos_logic import pagos_logic
from capa_datos.database_connection import get_db_connection

class ReportsLogic:
    """
    Lógica de negocio para la generación de reportes.
    """
    
    def __init__(self):
        self.conn = None  # Inicializar como None
        self.pagos_logic = pagos_logic
    
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
    
    def obtener_dashboard_principal(self):
        """
        Obtiene los datos principales para el dashboard.
        
        Returns:
            dict: Datos del dashboard principal
        """
        try:
            # Estadísticas generales
            stats_generales = get_estadisticas_generales_db(self._get_connection())
            
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
            self._log_error(f"Error al obtener datos del dashboard: {e}")
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
            return get_vista_reservas_completas_db(self._get_connection(), fecha_inicio, fecha_fin, cliente_id, cancha_id)
        except Exception as e:
            self._log_error(f"Error al obtener vista de reservas completas: {e}")
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
            return get_vista_estadisticas_canchas_db(self._get_connection(), fecha_inicio, fecha_fin)
        except Exception as e:
            self._log_error(f"Error al obtener vista de estadísticas de canchas: {e}")
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
            return get_estadisticas_mensuales_db(self._get_connection(), año)
        except Exception as e:
            self._log_error(f"Error al obtener estadísticas mensuales: {e}")
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
            return get_estadisticas_semanales_db(self._get_connection(), fecha_inicio, fecha_fin)
        except Exception as e:
            self._log_error(f"Error al obtener estadísticas semanales: {e}")
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
            return get_top_clientes_db(self._get_connection(), fecha_inicio, fecha_fin, limit)
        except Exception as e:
            self._log_error(f"Error al obtener top clientes: {e}")
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
            return get_top_canchas_db(self._get_connection(), fecha_inicio, fecha_fin, limit)
        except Exception as e:
            self._log_error(f"Error al obtener top canchas: {e}")
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
            return get_estadisticas_horarios_db(self._get_connection(), fecha_inicio, fecha_fin)
        except Exception as e:
            self._log_error(f"Error al obtener estadísticas por horarios: {e}")
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
            return get_estadisticas_dias_semana_db(self._get_connection(), fecha_inicio, fecha_fin)
        except Exception as e:
            self._log_error(f"Error al obtener estadísticas por días de la semana: {e}")
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
            return get_canchas_mas_usadas_db(self._get_connection(), fecha_inicio, fecha_fin, limit)
        except Exception as e:
            self._log_error(f"Error al obtener canchas más utilizadas: {e}")
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
            return get_canchas_mas_recaudan_db(self._get_connection(), fecha_inicio, fecha_fin, limit)
        except Exception as e:
            self._log_error(f"Error al obtener canchas que más recaudan: {e}")
            return []
    
    def generar_estadisticas_procedimiento(self, fecha_inicio=None, fecha_fin=None, tipo_reporte='mensual'):
        """
        Genera estadísticas usando el procedimiento almacenado.
        
        Args:
            fecha_inicio (date): Fecha de inicio para el reporte
            fecha_fin (date): Fecha de fin para el reporte
            tipo_reporte (str): Tipo de reporte ('mensual', 'semanal', 'diario')
        
        Returns:
            bool: True si el reporte se generó correctamente, False en caso contrario
        """
        try:
            return generar_estadisticas_procedimiento_db(self._get_connection(), fecha_inicio, fecha_fin, tipo_reporte)
        except Exception as e:
            self._log_error(f"Error al generar estadísticas: {e}")
            return False

# Instancia global de la lógica de reportes
reports_logic = ReportsLogic() 