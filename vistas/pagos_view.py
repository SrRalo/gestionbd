import streamlit as st
import pandas as pd
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from capa_datos.database_connection import get_db_connection

class PagosView:
    def __init__(self):
        self.db_connection = get_db_connection()
    
    def show(self):
        """Mostrar la vista principal de gestión de pagos"""
        st.markdown("## 💰 Gestión de Pagos")
        
        # Verificar permisos (solo admin y operador)
        if st.session_state.user_role not in ['admin_reservas', 'operador_reservas']:
            st.error("❌ No tienes permisos para acceder a esta sección.")
            st.info("Esta funcionalidad está disponible solo para administradores y operadores.")
            return
        
        # Mostrar badge de rol
        role_display = "👑 Administrador" if st.session_state.user_role == 'admin_reservas' else "👨‍💼 Operador"
        st.markdown(f'<div class="role-badge">{role_display}</div>', unsafe_allow_html=True)
        
        # Pestañas para diferentes funcionalidades
        tab1, tab2, tab3, tab4 = st.tabs([
            "💳 Registrar Pago", 
            "📋 Reservas Pendientes", 
            "📊 Historial de Pagos",
            "📈 Resumen de Pagos"
        ])
        
        with tab1:
            self.show_registrar_pago()
        
        with tab2:
            self.show_reservas_pendientes()
        
        with tab3:
            self.show_historial_pagos()
        
        with tab4:
            self.show_resumen_pagos()
    
    def show_registrar_pago(self):
        """Mostrar formulario para registrar un nuevo pago"""
        st.markdown("### 💳 Registrar Nuevo Pago")
        st.info("Utiliza esta sección para registrar pagos de reservas usando el procedimiento almacenado.")
        
        # Obtener reservas pendientes de pago
        reservas_pendientes = self.get_reservas_pendientes_pago()
        
        if not reservas_pendientes:
            st.warning("No hay reservas pendientes de pago.")
            return
        
        # Formulario para registrar pago
        with st.form("form_registrar_pago"):
            st.markdown("#### Seleccionar Reserva")
            
            # Crear opciones para el selectbox
            opciones_reservas = []
            for reserva in reservas_pendientes:
                opcion = f"Reserva #{reserva['reserva_id']} - {reserva['nombre_cliente']} {reserva['apellido_cliente']} - {reserva['nombre_cancha']} - {reserva['fecha_reserva']} - Saldo: ${reserva['saldo_pendiente']:.2f}"
                opciones_reservas.append(opcion)
            
            reserva_seleccionada = st.selectbox(
                "Selecciona la reserva:",
                opciones_reservas,
                help="Selecciona la reserva para la cual registrarás el pago"
            )
            
            # Obtener la reserva seleccionada
            if reserva_seleccionada:
                reserva_id = int(reserva_seleccionada.split(" - ")[0].replace("Reserva #", ""))
                reserva_info = next((r for r in reservas_pendientes if r['reserva_id'] == reserva_id), None)
                
                if reserva_info:
                    # Mostrar información de la reserva
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Información de la Reserva:**")
                        st.write(f"**Cliente:** {reserva_info['nombre_cliente']} {reserva_info['apellido_cliente']}")
                        st.write(f"**Cancha:** {reserva_info['nombre_cancha']}")
                        st.write(f"**Fecha:** {reserva_info['fecha_reserva']}")
                        st.write(f"**Horario:** {reserva_info['hora_inicio']} - {reserva_info['hora_fin']}")
                    
                    with col2:
                        st.markdown("**Información de Pago:**")
                        st.write(f"**Precio Total:** ${reserva_info['precio_total_calculado']:.2f}")
                        st.write(f"**Total Pagado:** ${reserva_info['total_pagado']:.2f}")
                        st.write(f"**Saldo Pendiente:** ${reserva_info['saldo_pendiente']:.2f}")
                        st.write(f"**Estado:** {reserva_info['estado_pago']}")
            
            st.markdown("#### Información del Pago")
            
            # Campos del formulario
            monto = st.number_input(
                "Monto del pago ($):",
                min_value=0.01,
                max_value=float(reserva_info['saldo_pendiente']) if reserva_info else 10000.0,
                value=float(reserva_info['saldo_pendiente']) if reserva_info else 0.0,
                step=0.01,
                help="Ingresa el monto a pagar"
            )
            
            metodo_pago = st.selectbox(
                "Método de pago:",
                ["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", "Transferencia Bancaria", "Pago Móvil"],
                help="Selecciona el método de pago utilizado"
            )
            
            observaciones = st.text_area(
                "Observaciones (opcional):",
                placeholder="Ingresa cualquier observación adicional sobre el pago...",
                help="Observaciones adicionales sobre el pago"
            )
            
            # Botón para registrar el pago
            submitted = st.form_submit_button("💳 Registrar Pago", type="primary")
            
            if submitted and reserva_info:
                self.registrar_pago(reserva_id, monto, metodo_pago, observaciones)
    
    def show_reservas_pendientes(self):
        """Mostrar lista de reservas pendientes de pago"""
        st.markdown("### 📋 Reservas Pendientes de Pago")
        
        reservas_pendientes = self.get_reservas_pendientes_pago()
        
        if not reservas_pendientes:
            st.success("✅ No hay reservas pendientes de pago.")
            return
        
        # Convertir a DataFrame para mejor visualización
        df = pd.DataFrame(reservas_pendientes)
        
        # Formatear columnas
        df['fecha_reserva'] = pd.to_datetime(df['fecha_reserva']).dt.strftime('%Y-%m-%d')
        df['precio_total_calculado'] = df['precio_total_calculado'].apply(lambda x: f"${x:.2f}")
        df['total_pagado'] = df['total_pagado'].apply(lambda x: f"${x:.2f}")
        df['saldo_pendiente'] = df['saldo_pendiente'].apply(lambda x: f"${x:.2f}")
        
        # Mostrar tabla
        st.dataframe(
            df[[
                'reserva_id', 'nombre_cliente', 'apellido_cliente', 'nombre_cancha',
                'fecha_reserva', 'hora_inicio', 'hora_fin', 'precio_total_calculado',
                'total_pagado', 'saldo_pendiente', 'estado_pago'
            ]].rename(columns={
                'reserva_id': 'ID Reserva',
                'nombre_cliente': 'Nombre',
                'apellido_cliente': 'Apellido',
                'nombre_cancha': 'Cancha',
                'fecha_reserva': 'Fecha',
                'hora_inicio': 'Hora Inicio',
                'hora_fin': 'Hora Fin',
                'precio_total_calculado': 'Precio Total',
                'total_pagado': 'Pagado',
                'saldo_pendiente': 'Saldo',
                'estado_pago': 'Estado'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Reservas", len(reservas_pendientes))
        with col2:
            total_saldo = sum(r['saldo_pendiente'] for r in reservas_pendientes)
            st.metric("Saldo Total Pendiente", f"${total_saldo:.2f}")
        with col3:
            reservas_sin_pago = len([r for r in reservas_pendientes if r['estado_pago'] == 'Sin Pago'])
            st.metric("Sin Pago", reservas_sin_pago)
    
    def show_historial_pagos(self):
        """Mostrar historial de pagos"""
        st.markdown("### 📊 Historial de Pagos")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fecha_inicio = st.date_input(
                "Fecha de inicio:",
                value=date.today().replace(day=1),
                help="Selecciona la fecha de inicio para filtrar"
            )
        
        with col2:
            fecha_fin = st.date_input(
                "Fecha de fin:",
                value=date.today(),
                help="Selecciona la fecha de fin para filtrar"
            )
        
        with col3:
            metodo_filtro = st.selectbox(
                "Método de pago:",
                ["Todos", "Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", "Transferencia Bancaria", "Pago Móvil"],
                help="Filtrar por método de pago"
            )
        
        # Obtener historial de pagos
        historial = self.get_historial_pagos(fecha_inicio, fecha_fin, metodo_filtro)
        
        if not historial:
            st.info("No se encontraron pagos en el período seleccionado.")
            return
        
        # Convertir a DataFrame
        df = pd.DataFrame(historial)
        
        # Formatear columnas
        df['fecha_pago'] = pd.to_datetime(df['fecha_pago']).dt.strftime('%Y-%m-%d %H:%M')
        df['monto'] = df['monto'].apply(lambda x: f"${x:.2f}")
        df['precio_total_reserva'] = df['precio_total_reserva'].apply(lambda x: f"${x:.2f}")
        
        # Mostrar tabla
        st.dataframe(
            df[[
                'pago_id', 'fecha_pago', 'nombre_cliente', 'apellido_cliente',
                'nombre_cancha', 'monto', 'metodo_pago', 'estado_pago'
            ]].rename(columns={
                'pago_id': 'ID Pago',
                'fecha_pago': 'Fecha Pago',
                'nombre_cliente': 'Nombre',
                'apellido_cliente': 'Apellido',
                'nombre_cancha': 'Cancha',
                'monto': 'Monto',
                'metodo_pago': 'Método',
                'estado_pago': 'Estado'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Estadísticas del período
        col1, col2, col3 = st.columns(3)
        with col1:
            total_pagos = len(historial)
            st.metric("Total Pagos", total_pagos)
        with col2:
            total_recaudado = sum(p['monto'] for p in historial)
            st.metric("Total Recaudado", f"${total_recaudado:.2f}")
        with col3:
            promedio_pago = total_recaudado / total_pagos if total_pagos > 0 else 0
            st.metric("Promedio por Pago", f"${promedio_pago:.2f}")
    
    def show_resumen_pagos(self):
        """Mostrar resumen de pagos por período"""
        st.markdown("### 📈 Resumen de Pagos por Período")
        
        # Obtener resumen de pagos
        resumen = self.get_resumen_pagos_periodo()
        
        if not resumen:
            st.info("No hay datos de pagos para mostrar.")
            return
        
        # Convertir a DataFrame
        df = pd.DataFrame(resumen)
        
        # Formatear columnas
        df['mes'] = pd.to_datetime(df['mes']).dt.strftime('%B %Y')
        df['total_recaudado'] = df['total_recaudado'].apply(lambda x: f"${x:.2f}")
        df['promedio_pago'] = df['promedio_pago'].apply(lambda x: f"${x:.2f}")
        
        # Mostrar tabla
        st.dataframe(
            df[[
                'mes', 'total_pagos', 'total_recaudado', 'promedio_pago',
                'clientes_unicos', 'canchas_utilizadas', 'pagos_completados'
            ]].rename(columns={
                'mes': 'Mes',
                'total_pagos': 'Total Pagos',
                'total_recaudado': 'Total Recaudado',
                'promedio_pago': 'Promedio',
                'clientes_unicos': 'Clientes Únicos',
                'canchas_utilizadas': 'Canchas',
                'pagos_completados': 'Pagos Completados'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Pagos por Mes")
            # Gráfico de barras para total de pagos por mes
            chart_data = df.copy()
            chart_data['mes'] = pd.to_datetime(chart_data['mes'], format='%B %Y')
            chart_data = chart_data.sort_values('mes')
            
            st.bar_chart(
                chart_data.set_index('mes')['total_pagos'],
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### 💰 Recaudación por Mes")
            # Gráfico de líneas para recaudación
            chart_data['total_recaudado_numeric'] = chart_data['total_recaudado'].str.replace('$', '').astype(float)
            
            st.line_chart(
                chart_data.set_index('mes')['total_recaudado_numeric'],
                use_container_width=True
            )
    
    def get_reservas_pendientes_pago(self):
        """Obtener reservas pendientes de pago"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM vista_reservas_pendientes_pago
                    ORDER BY fecha_reserva DESC, hora_inicio
                """)
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Error al obtener reservas pendientes: {str(e)}")
            return []
    
    def get_historial_pagos(self, fecha_inicio, fecha_fin, metodo_filtro):
        """Obtener historial de pagos con filtros"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM vista_historial_pagos
                    WHERE fecha_pago::date BETWEEN %s AND %s
                """
                params = [fecha_inicio, fecha_fin]
                
                if metodo_filtro != "Todos":
                    query += " AND metodo_pago = %s"
                    params.append(metodo_filtro)
                
                query += " ORDER BY fecha_pago DESC"
                
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Error al obtener historial de pagos: {str(e)}")
            return []
    
    def get_resumen_pagos_periodo(self):
        """Obtener resumen de pagos por período"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM vista_resumen_pagos_periodo
                    ORDER BY mes DESC
                    LIMIT 12
                """)
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Error al obtener resumen de pagos: {str(e)}")
            return []
    
    def registrar_pago(self, reserva_id, monto, metodo_pago, observaciones):
        """Registrar un nuevo pago usando el procedimiento almacenado"""
        try:
            with self.db_connection.cursor() as cursor:
                # Llamar al procedimiento almacenado usando CALL
                cursor.execute("""
                    CALL proc_registrar_pago(%s, %s, %s, %s)
                """, (reserva_id, monto, metodo_pago, observaciones))
                
                self.db_connection.commit()
                
                st.success(f"✅ Pago registrado exitosamente!")
                st.info(f"**Detalles del pago:**")
                st.info(f"- Reserva ID: {reserva_id}")
                st.info(f"- Monto: ${monto:.2f}")
                st.info(f"- Método: {metodo_pago}")
                if observaciones:
                    st.info(f"- Observaciones: {observaciones}")
                
                # Recargar la página para actualizar los datos
                st.rerun()
                
        except Exception as e:
            self.db_connection.rollback()
            st.error(f"❌ Error al registrar el pago: {str(e)}")
            st.error("El pago no se pudo registrar. Verifica los datos e intenta nuevamente.") 