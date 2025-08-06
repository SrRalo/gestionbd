import streamlit as st
import pandas as pd
from datetime import time
from logica_negocio.canchas_logic import CanchasLogic

class DashboardView:
    """
    Vista para el dashboard principal de la aplicación.
    """
    
    def __init__(self):
        self.canchas_logic = CanchasLogic()
    
    def show(self):
        """Mostrar el dashboard completo"""
        
        # Mostrar información del usuario
        self.show_user_info()
        
        # Dashboard básico
        st.markdown("## 📊 Dashboard")
        
        # Obtener estadísticas de canchas
        stats_canchas = self.canchas_logic.obtener_estadisticas_canchas()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Usuarios",
                value="0",
                delta="0"
            )
        
        with col2:
            st.metric(
                label="Total Canchas",
                value=stats_canchas.get('total_canchas', 0),
                delta="0"
            )
        
        with col3:
            st.metric(
                label="Reservas Hoy",
                value="0",
                delta="0"
            )
        
        with col4:
            st.metric(
                label="Ingresos Mes",
                value="$0",
                delta="$0"
            )
        
        # Navegación principal
        self.show_navigation()
        
        # Tabla de canchas con tipos
        self.show_canchas_table()
        
        # Formulario de creación
        self.show_formulario_creacion()
        
        # Vista de edición
        self.show_edicion_section()
        
        # Botón de logout
        self.show_logout_button()
    
    def show_user_info(self):
        """Mostrar información del usuario logueado"""
        if st.session_state.current_user:
            username = st.session_state.current_user
            role_display = self.get_role_display_name(st.session_state.user_role)
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Usuario:** {username}")
                if hasattr(st.session_state, 'user_info') and st.session_state.user_info:
                    st.markdown(f"**Rol:** {st.session_state.user_info.get('usuario_actual', 'N/A')}")
            with col2:
                st.markdown(f'<div class="role-badge">{role_display}</div>', unsafe_allow_html=True)
            
            st.markdown("---")
    
    def show_navigation(self):
        """Mostrar navegación principal"""
        st.markdown("## 🧭 Navegación")
        
        # Verificar si el usuario tiene permisos para gestión de pagos
        can_access_pagos = st.session_state.user_role in ['admin_reservas', 'operador_reservas']
        
        if can_access_pagos:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📅 Gestión de Reservas", use_container_width=True):
                    st.session_state.current_page = "reservas"
                    st.rerun()
            
            with col2:
                if st.button("💰 Gestión de Pagos", use_container_width=True):
                    st.session_state.current_page = "pagos"
                    st.rerun()
            
            with col3:
                if st.button("📊 Reportes", use_container_width=True):
                    st.session_state.current_page = "reportes"
                    st.rerun()
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📅 Gestión de Reservas", use_container_width=True):
                    st.session_state.current_page = "reservas"
                    st.rerun()
            
            with col2:
                if st.button("📊 Reportes", use_container_width=True):
                    st.session_state.current_page = "reportes"
                    st.rerun()
        
        st.markdown("---")
    
    def show_canchas_table(self):
        """Mostrar tabla de canchas con tipos"""
        st.markdown("## 🏟️ Canchas y Tipos")
        
        try:
            # Obtener canchas con tipos
            canchas_con_tipos = self.canchas_logic.obtener_canchas_con_tipos()
            
            if canchas_con_tipos:
                # Crear DataFrame para mejor visualización
                df = pd.DataFrame(canchas_con_tipos)
                
                # Renombrar columnas para mejor visualización
                df_renamed = df.rename(columns={
                    'nombre_cancha': 'Nombre Cancha',
                    'descripcion_cancha': 'Descripción Cancha',
                    'capacidad': 'Capacidad',
                    'precio_hora': 'Precio/Hora',
                    'estado': 'Estado',
                    'tipo_cancha_nombre': 'Tipo de Cancha',
                    'tipo_cancha_descripcion': 'Descripción Tipo'
                })
                
                # Seleccionar columnas relevantes para mostrar
                columns_to_show = [
                    'Nombre Cancha', 'Tipo de Cancha', 'Capacidad', 
                    'Precio/Hora', 'Estado', 'Descripción Cancha'
                ]
                
                # Filtrar solo las columnas que existen
                available_columns = [col for col in columns_to_show if col in df_renamed.columns]
                df_display = df_renamed[available_columns]
                
                # Implementar paginación
                total_registros = len(df_display)
                registros_por_pagina = 5
                total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
                
                # Controles de paginación
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if st.button("⬅️ Anterior", disabled=st.session_state.get('pagina_canchas', 1) <= 1):
                        st.session_state.pagina_canchas = max(1, st.session_state.get('pagina_canchas', 1) - 1)
                        st.rerun()
                
                with col2:
                    pagina_actual = st.session_state.get('pagina_canchas', 1)
                    st.markdown(f"**Página {pagina_actual} de {total_paginas}**")
                
                with col3:
                    if st.button("➡️ Siguiente", disabled=pagina_actual >= total_paginas):
                        st.session_state.pagina_canchas = min(total_paginas, pagina_actual + 1)
                        st.rerun()
                
                # Calcular índices para la página actual
                inicio = (pagina_actual - 1) * registros_por_pagina
                fin = min(inicio + registros_por_pagina, total_registros)
                
                # Mostrar registros de la página actual
                df_pagina = df_display.iloc[inicio:fin]
                
                st.dataframe(
                    df_pagina,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Información de paginación
                st.info(f"📊 Mostrando registros {inicio + 1}-{fin} de {total_registros} canchas (5 por página)")
                
            else:
                st.warning("⚠️ No se encontraron canchas en la base de datos.")
                
        except Exception as e:
            st.error(f"❌ Error al cargar las canchas: {str(e)}")
    
    def show_logout_button(self):
        """Mostrar botón de logout"""
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.rerun()
    
    def get_role_display_name(self, role):
        """Obtener nombre de visualización del rol"""
        role_names = {
            'admin_reservas': '👑 Administrador',
            'operador_reservas': '👨‍💼 Operador',
            'consultor_reservas': '👤 Consultor'
        }
        return role_names.get(role, 'Usuario')
    
    def show_formulario_creacion(self):
        """Mostrar formulario unificado para crear canchas con su tipo"""
        st.markdown("### ➕ Crear Nueva Cancha Completa")
        st.markdown("*Este formulario creará tanto la cancha como su tipo de cancha en una sola operación*")
        
        self.show_formulario_unificado()
    
    def show_formulario_unificado(self):
        """Formulario unificado para crear cancha y tipo de cancha"""
        st.markdown("#### 🏟️ Información de la Cancha")
        
        with st.form("form_crear_cancha_completa"):
            # Sección 1: Información del Tipo de Cancha
            st.markdown("**📋 Información del Tipo de Cancha**")
            col1, col2 = st.columns(2)
            
            with col1:
                tipo_nombre = st.text_input("Nombre del Tipo de Cancha", key="tipo_nombre")
                tipo_precio_por_hora = st.number_input("Precio por Hora del Tipo ($)", min_value=0.0, value=50.0, step=0.5, key="tipo_precio")
            
            with col2:
                tipo_descripcion = st.text_area("Descripción del Tipo", key="tipo_descripcion", height=100)
            
            st.markdown("---")
            
            # Sección 2: Información de la Cancha
            st.markdown("**🏟️ Información de la Cancha**")
            col1, col2 = st.columns(2)
            
            with col1:
                cancha_nombre = st.text_input("Nombre de la Cancha", key="cancha_nombre")
                tipo_deporte = st.selectbox(
                    "Tipo de Deporte",
                    ["Fútbol", "Basketball", "Tennis", "Voleibol", "Otro"],
                    key="cancha_tipo_deporte"
                )
                capacidad = st.number_input("Capacidad", min_value=1, value=50, key="cancha_capacidad")
                precio_hora = st.number_input("Precio por Hora de la Cancha ($)", min_value=0.0, value=50.0, step=0.5, key="cancha_precio")
            
            with col2:
                estado = st.selectbox(
                    "Estado",
                    ["Activa", "Inactiva", "Mantenimiento"],
                    key="cancha_estado"
                )
                horario_apertura = st.time_input("Horario de Apertura", value=time(6, 0), key="cancha_apertura")
                horario_cierre = st.time_input("Horario de Cierre", value=time(22, 0), key="cancha_cierre")
            
            cancha_descripcion = st.text_area("Descripción de la Cancha", key="cancha_descripcion", height=100)
            
            submitted = st.form_submit_button("🏟️ Crear Cancha Completa")
            
            if submitted:
                if (tipo_nombre and tipo_precio_por_hora and 
                    cancha_nombre and tipo_deporte and capacidad and precio_hora):
                    
                    # Crear primero el tipo de cancha
                    tipo_id = self.canchas_logic.crear_tipo_cancha(tipo_nombre, tipo_descripcion, tipo_precio_por_hora)
                    
                    if tipo_id:
                        # Luego crear la cancha usando el ID del tipo creado
                        cancha_id = self.canchas_logic.crear_cancha(
                            cancha_nombre, tipo_deporte, capacidad, precio_hora, estado,
                            horario_apertura.strftime("%H:%M:%S"), 
                            horario_cierre.strftime("%H:%M:%S"), 
                            cancha_descripcion, tipo_id
                        )
                        
                        if cancha_id:
                            st.success(f"""
                            ✅ **Cancha creada exitosamente!**
                            
                            **Tipo de Cancha:**
                            - Nombre: {tipo_nombre}
                            - ID: {tipo_id}
                            - Precio: ${tipo_precio_por_hora}
                            
                            **Cancha:**
                            - Nombre: {cancha_nombre}
                            - ID: {cancha_id}
                            - Tipo de Deporte: {tipo_deporte}
                            - Capacidad: {capacidad}
                            - Precio: ${precio_hora}
                            """)
                            st.rerun()
                        else:
                            st.error("❌ Error al crear la cancha")
                    else:
                        st.error("❌ Error al crear el tipo de cancha")
                else:
                                         st.error("❌ Por favor completa todos los campos obligatorios")
    
    def show_edicion_section(self):
        """Mostrar sección de edición de registros"""
        st.markdown("---")
        st.markdown("## ✏️ Edición de Registros")
        
        # Importar la vista de edición
        from vistas.edicion_view import EdicionView
        
        # Mostrar la vista de edición
        edicion_view = EdicionView()
        edicion_view.show() 