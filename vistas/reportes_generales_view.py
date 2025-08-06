import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from logica_negocio.reports_logic import reports_logic

class ReportesGeneralesView:
    """
    Vista para reportes generales del sistema.
    """
    
    def __init__(self):
        self.reports_logic = reports_logic
    
    def show(self):
        """
        Muestra la interfaz de reportes generales.
        """
        # Verificar el rol del usuario
        user_role = st.session_state.get('user_role', 'consultor_reservas')
        
        if user_role == 'consultor_reservas':
            st.error("🚫 **Acceso Denegado**")
            st.warning("El usuario consultor no tiene permisos para acceder a los reportes financieros.")
            st.info("Solo los administradores y operadores pueden ver estos reportes.")
            return
        
        st.markdown("## 📊 Reportes Generales")
        st.markdown("Genera reportes detallados sobre el rendimiento de las canchas y los ingresos del sistema.")
        
        # Mostrar información del rol
        if user_role == 'admin_reservas':
            st.success("👑 **Rol: Administrador** - Acceso completo a todos los reportes")
        elif user_role == 'operador_reservas':
            st.info("👨‍💼 **Rol: Operador** - Acceso de lectura a todos los reportes")
        
        # Filtros de fecha
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha_inicio = st.date_input(
                "📅 Fecha de inicio",
                value=date.today() - timedelta(days=30),
                max_value=date.today()
            )
        
        with col2:
            fecha_fin = st.date_input(
                "📅 Fecha de fin",
                value=date.today(),
                max_value=date.today()
            )
        
        with col3:
            limit_registros = st.number_input(
                "📊 Número de registros",
                min_value=5,
                max_value=50,
                value=10,
                step=5
            )
        
        # Validar fechas
        if fecha_inicio > fecha_fin:
            st.error("❌ La fecha de inicio no puede ser mayor que la fecha de fin.")
            return
        
        # Botón para generar reportes
        if st.button("🔄 Generar Reportes", type="primary", key="generar_reportes_btn"):
            self.mostrar_reportes(fecha_inicio, fecha_fin, limit_registros)
    
    def mostrar_reportes(self, fecha_inicio, fecha_fin, limit_registros):
        """
        Muestra los reportes generados.
        
        Args:
            fecha_inicio (date): Fecha de inicio
            fecha_fin (date): Fecha de fin
            limit_registros (int): Número de registros a mostrar
        """
        with st.spinner("🔄 Generando reportes..."):
            # Obtener datos
            canchas_mas_usadas = self.reports_logic.obtener_canchas_mas_usadas(
                fecha_inicio, fecha_fin, limit_registros
            )
            
            canchas_mas_recaudan = self.reports_logic.obtener_canchas_mas_recaudan(
                fecha_inicio, fecha_fin, limit_registros
            )
            
            # Mostrar resumen
            self.mostrar_resumen(fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan)
            
            # Mostrar tablas
            col1, col2 = st.columns(2)
            
            with col1:
                self.mostrar_tabla_canchas_mas_usadas(canchas_mas_usadas)
            
            with col2:
                self.mostrar_tabla_canchas_mas_recaudan(canchas_mas_recaudan)
            
            # Mostrar gráficos
            self.mostrar_graficos(canchas_mas_usadas, canchas_mas_recaudan)
    
    def mostrar_resumen(self, fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan):
        """
        Muestra un resumen de los reportes.
        """
        st.markdown("### 📈 Resumen del Período")
        
        # Calcular estadísticas
        total_reservas = sum(c['total_reservas'] for c in canchas_mas_usadas)
        total_ingresos = sum(c['ingresos_totales'] for c in canchas_mas_recaudan)
        canchas_activas = len([c for c in canchas_mas_usadas if c['total_reservas'] > 0])
        
        # Mostrar métricas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🏟️ Canchas Activas",
                value=canchas_activas,
                help="Canchas con al menos una reserva en el período"
            )
        
        with col2:
            st.metric(
                label="📅 Total Reservas",
                value=total_reservas,
                help="Número total de reservas en el período"
            )
        
        with col3:
            st.metric(
                label="💰 Ingresos Totales",
                value=f"${total_ingresos:,.2f}",
                help="Ingresos totales generados en el período"
            )
        
        with col4:
            promedio_por_reserva = total_ingresos / total_reservas if total_reservas > 0 else 0
            st.metric(
                label="📊 Promedio por Reserva",
                value=f"${promedio_por_reserva:,.2f}",
                help="Promedio de ingresos por reserva"
            )
        
        st.markdown(f"**Período analizado:** {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}")
        st.markdown("---")
    
    def mostrar_tabla_canchas_mas_usadas(self, canchas_mas_usadas):
        """
        Muestra la tabla de canchas más utilizadas.
        """
        st.markdown("### 🏆 Canchas Más Utilizadas")
        
        if not canchas_mas_usadas:
            st.info("📭 No hay datos de canchas utilizadas en el período seleccionado.")
            return
        
        # Preparar datos para la tabla
        datos_tabla = []
        for i, cancha in enumerate(canchas_mas_usadas, 1):
            datos_tabla.append({
                "Posición": i,
                "Cancha": cancha['nombre'],
                "Deporte": cancha['tipo_deporte'],
                "Precio/Hora": f"${cancha['precio_hora']:,.2f}",
                "Reservas": cancha['total_reservas'],
                "Ingresos": f"${cancha['ingresos_totales']:,.2f}",
                "Promedio": f"${cancha['promedio_por_reserva']:,.2f}"
            })
        
        # Crear DataFrame
        df = pd.DataFrame(datos_tabla)
        
        # Implementar paginación
        total_registros = len(df)
        registros_por_pagina = 5
        total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
        
        # Controles de paginación
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Anterior", disabled=st.session_state.get('pagina_canchas_usadas', 1) <= 1, key="anterior_canchas_usadas"):
                st.session_state.pagina_canchas_usadas = max(1, st.session_state.get('pagina_canchas_usadas', 1) - 1)
                st.rerun()
        
        with col2:
            pagina_actual = st.session_state.get('pagina_canchas_usadas', 1)
            st.markdown(f"**Página {pagina_actual} de {total_paginas}**")
        
        with col3:
            if st.button("➡️ Siguiente", disabled=pagina_actual >= total_paginas, key="siguiente_canchas_usadas"):
                st.session_state.pagina_canchas_usadas = min(total_paginas, pagina_actual + 1)
                st.rerun()
        
        # Calcular índices para la página actual
        inicio = (pagina_actual - 1) * registros_por_pagina
        fin = min(inicio + registros_por_pagina, total_registros)
        
        # Mostrar registros de la página actual
        df_pagina = df.iloc[inicio:fin]
        
        # Mostrar tabla con estilo
        st.dataframe(
            df_pagina,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Posición": st.column_config.NumberColumn(
                    "Posición",
                    help="Ranking de la cancha",
                    format="%d"
                ),
                "Cancha": st.column_config.TextColumn(
                    "Cancha",
                    help="Nombre de la cancha"
                ),
                "Deporte": st.column_config.TextColumn(
                    "Deporte",
                    help="Tipo de deporte"
                ),
                "Precio/Hora": st.column_config.TextColumn(
                    "Precio/Hora",
                    help="Precio por hora de la cancha"
                ),
                "Reservas": st.column_config.NumberColumn(
                    "Reservas",
                    help="Número total de reservas",
                    format="%d"
                ),
                "Ingresos": st.column_config.TextColumn(
                    "Ingresos",
                    help="Ingresos totales generados"
                ),
                "Promedio": st.column_config.TextColumn(
                    "Promedio",
                    help="Promedio por reserva"
                )
            }
        )
        
        # Información de paginación
        st.info(f"📊 Mostrando registros {inicio + 1}-{fin} de {total_registros} canchas (5 por página)")
        
        # Mostrar estadísticas adicionales
        if canchas_mas_usadas:
            cancha_top = canchas_mas_usadas[0]
            st.info(f"🏆 **Cancha más utilizada:** {cancha_top['nombre']} con {cancha_top['total_reservas']} reservas")
    
    def mostrar_tabla_canchas_mas_recaudan(self, canchas_mas_recaudan):
        """
        Muestra la tabla de canchas que más dinero recaudan.
        """
        st.markdown("### 💰 Canchas que Más Dinero Recaudan")
        
        if not canchas_mas_recaudan:
            st.info("📭 No hay datos de ingresos en el período seleccionado.")
            return
        
        # Preparar datos para la tabla
        datos_tabla = []
        for i, cancha in enumerate(canchas_mas_recaudan, 1):
            datos_tabla.append({
                "Posición": i,
                "Cancha": cancha['nombre'],
                "Deporte": cancha['tipo_deporte'],
                "Precio/Hora": f"${cancha['precio_hora']:,.2f}",
                "Reservas": cancha['total_reservas'],
                "Ingresos": f"${cancha['ingresos_totales']:,.2f}",
                "Promedio": f"${cancha['promedio_por_reserva']:,.2f}",
                "Ingreso/Reserva": f"${cancha.get('ingreso_promedio_por_reserva', 0):,.2f}"
            })
        
        # Crear DataFrame
        df = pd.DataFrame(datos_tabla)
        
        # Implementar paginación
        total_registros = len(df)
        registros_por_pagina = 5
        total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
        
        # Controles de paginación
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Anterior", disabled=st.session_state.get('pagina_canchas_recaudan', 1) <= 1, key="anterior_canchas_recaudan"):
                st.session_state.pagina_canchas_recaudan = max(1, st.session_state.get('pagina_canchas_recaudan', 1) - 1)
                st.rerun()
        
        with col2:
            pagina_actual = st.session_state.get('pagina_canchas_recaudan', 1)
            st.markdown(f"**Página {pagina_actual} de {total_paginas}**")
        
        with col3:
            if st.button("➡️ Siguiente", disabled=pagina_actual >= total_paginas, key="siguiente_canchas_recaudan"):
                st.session_state.pagina_canchas_recaudan = min(total_paginas, pagina_actual + 1)
                st.rerun()
        
        # Calcular índices para la página actual
        inicio = (pagina_actual - 1) * registros_por_pagina
        fin = min(inicio + registros_por_pagina, total_registros)
        
        # Mostrar registros de la página actual
        df_pagina = df.iloc[inicio:fin]
        
        # Mostrar tabla con estilo
        st.dataframe(
            df_pagina,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Posición": st.column_config.NumberColumn(
                    "Posición",
                    help="Ranking de la cancha por ingresos",
                    format="%d"
                ),
                "Cancha": st.column_config.TextColumn(
                    "Cancha",
                    help="Nombre de la cancha"
                ),
                "Deporte": st.column_config.TextColumn(
                    "Deporte",
                    help="Tipo de deporte"
                ),
                "Precio/Hora": st.column_config.TextColumn(
                    "Precio/Hora",
                    help="Precio por hora de la cancha"
                ),
                "Reservas": st.column_config.NumberColumn(
                    "Reservas",
                    help="Número total de reservas",
                    format="%d"
                ),
                "Ingresos": st.column_config.TextColumn(
                    "Ingresos",
                    help="Ingresos totales generados"
                ),
                "Promedio": st.column_config.TextColumn(
                    "Promedio",
                    help="Promedio por reserva"
                ),
                "Ingreso/Reserva": st.column_config.TextColumn(
                    "Ingreso/Reserva",
                    help="Ingreso promedio por reserva"
                )
            }
        )
        
        # Información de paginación
        st.info(f"📊 Mostrando registros {inicio + 1}-{fin} de {total_registros} canchas (5 por página)")
        
        # Mostrar estadísticas adicionales
        if canchas_mas_recaudan:
            cancha_top = canchas_mas_recaudan[0]
            st.info(f"💰 **Cancha que más recauda:** {cancha_top['nombre']} con ${cancha_top['ingresos_totales']:,.2f}")
    
    def mostrar_graficos(self, canchas_mas_usadas, canchas_mas_recaudan):
        """
        Muestra gráficos comparativos.
        """
        st.markdown("### 📊 Gráficos Comparativos")
        
        if not canchas_mas_usadas:
            st.info("📊 No hay suficientes datos para generar gráficos.")
            return
        
        # Preparar datos para gráficos
        nombres_canchas = [c['nombre'] for c in canchas_mas_usadas[:5]]
        reservas = [c['total_reservas'] for c in canchas_mas_usadas[:5]]
        
        # Gráfico de barras para reservas
        st.markdown("#### 📅 Top 5 Canchas por Número de Reservas")
        chart_data = pd.DataFrame({
            "Cancha": nombres_canchas,
            "Reservas": reservas
        })
        st.bar_chart(chart_data.set_index("Cancha"))
    
    def exportar_reporte(self, fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan):
        """
        Permite exportar el reporte a diferentes formatos.
        """
        st.markdown("### 📤 Exportar Reporte")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Exportar a Excel", key="exportar_excel_btn"):
                self.exportar_a_excel(fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan)
        
        with col2:
            if st.button("📄 Exportar a CSV", key="exportar_csv_btn"):
                self.exportar_a_csv(fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan)
    
    def exportar_a_excel(self, fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan):
        """
        Exporta el reporte a formato Excel.
        """
        try:
            # Crear DataFrame para canchas más usadas
            df_usadas = pd.DataFrame(canchas_mas_usadas)
            df_usadas['ranking'] = range(1, len(df_usadas) + 1)
            
            # Crear DataFrame para canchas que más recaudan
            df_recaudan = pd.DataFrame(canchas_mas_recaudan)
            df_recaudan['ranking'] = range(1, len(df_recaudan) + 1)
            
            # Crear archivo Excel
            from io import BytesIO
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_usadas.to_excel(writer, sheet_name='Canchas_Mas_Usadas', index=False)
                df_recaudan.to_excel(writer, sheet_name='Canchas_Mas_Recaudan', index=False)
            
            output.seek(0)
            
            # Descargar archivo
            st.download_button(
                label="📥 Descargar Excel",
                data=output.getvalue(),
                file_name=f"reporte_canchas_{fecha_inicio}_{fecha_fin}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ Reporte exportado exitosamente a Excel")
            
        except Exception as e:
            st.error(f"❌ Error al exportar a Excel: {e}")
    
    def exportar_a_csv(self, fecha_inicio, fecha_fin, canchas_mas_usadas, canchas_mas_recaudan):
        """
        Exporta el reporte a formato CSV.
        """
        try:
            # Crear DataFrame combinado
            df_usadas = pd.DataFrame(canchas_mas_usadas)
            df_usadas['tipo_reporte'] = 'Mas_Usadas'
            
            df_recaudan = pd.DataFrame(canchas_mas_recaudan)
            df_recaudan['tipo_reporte'] = 'Mas_Recaudan'
            
            df_combinado = pd.concat([df_usadas, df_recaudan], ignore_index=True)
            
            # Convertir a CSV
            csv = df_combinado.to_csv(index=False)
            
            # Descargar archivo
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"reporte_canchas_{fecha_inicio}_{fecha_fin}.csv",
                mime="text/csv"
            )
            
            st.success("✅ Reporte exportado exitosamente a CSV")
            
        except Exception as e:
            st.error(f"❌ Error al exportar a CSV: {e}") 