"""
Vista para mostrar la auditoría del sistema
"""
import streamlit as st
import pandas as pd
from logica_negocio.auditoria_logic import AuditoriaLogic

class AuditoriaView:
    """Vista para mostrar la auditoría del sistema"""
    
    def __init__(self):
        """Inicializar la vista de auditoría"""
        self.auditoria_logic = AuditoriaLogic()
    
    def show(self):
        """Mostrar la vista principal de auditoría"""
        # Verificar si el usuario es administrador
        if st.session_state.get('user_role') != 'admin_reservas':
            st.error("❌ Acceso denegado. Solo los administradores pueden ver la auditoría del sistema.")
            return
        
        st.markdown("## 📋 Auditoría del Sistema")
        st.markdown("Registro de todas las acciones realizadas en el sistema.")
        
        # Mostrar registros de auditoría
        self.show_registros_auditoria()
    
    def show_registros_auditoria(self):
        """Mostrar registros de auditoría"""
        st.markdown("### 📊 Registros de Auditoría")
        
        # Obtener registros
        registros = self.auditoria_logic.obtener_auditoria()
        
        if not registros:
            st.info("📝 No hay registros de auditoría disponibles.")
            st.markdown("**Nota:** Los registros aparecerán automáticamente cuando se realicen cambios en la base de datos.")
            return
        
        # Convertir a DataFrame
        df = pd.DataFrame(registros)
        
        # Formatear fecha_hora
        if 'fecha_hora' in df.columns:
            df['fecha_hora'] = pd.to_datetime(df['fecha_hora']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        # Mostrar métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Registros", len(registros))
        
        with col2:
            usuarios_unicos = df['usuario_nombre'].nunique() if 'usuario_nombre' in df.columns else 0
            st.metric("Usuarios Activos", usuarios_unicos)
        
        with col3:
            tablas_unicas = df['tabla'].nunique() if 'tabla' in df.columns else 0
            st.metric("Tablas Afectadas", tablas_unicas)
        
        with col4:
            acciones_unicas = df['tipo_accion'].nunique() if 'tipo_accion' in df.columns else 0
            st.metric("Tipos de Acción", acciones_unicas)
        
        # Mostrar tabla de registros
        st.markdown("### 📋 Registros de Auditoría")
        
        # Seleccionar columnas para mostrar
        columnas_mostrar = ['fecha_hora', 'usuario_nombre', 'tipo_accion', 'tabla', 'registro_id', 'resultado', 'detalles']
        columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
        
        if columnas_disponibles:
            # Mostrar todos los registros (no solo los últimos 50)
            df_mostrar = df[columnas_disponibles]
            
            # Renombrar columnas para mejor presentación
            df_mostrar = df_mostrar.rename(columns={
                'fecha_hora': 'Fecha y Hora',
                'usuario_nombre': 'Usuario',
                'tipo_accion': 'Acción',
                'tabla': 'Tabla',
                'registro_id': 'ID Registro',
                'resultado': 'Resultado',
                'detalles': 'Detalles'
            })
            
            # Implementar paginación
            total_registros = len(df_mostrar)
            registros_por_pagina = 5
            total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
            
            # Controles de paginación
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if st.button("⬅️ Anterior", disabled=st.session_state.get('pagina_auditoria', 1) <= 1):
                    st.session_state.pagina_auditoria = max(1, st.session_state.get('pagina_auditoria', 1) - 1)
                    st.rerun()
            
            with col2:
                pagina_actual = st.session_state.get('pagina_auditoria', 1)
                st.markdown(f"**Página {pagina_actual} de {total_paginas}**")
            
            with col3:
                if st.button("➡️ Siguiente", disabled=pagina_actual >= total_paginas):
                    st.session_state.pagina_auditoria = min(total_paginas, pagina_actual + 1)
                    st.rerun()
            
            # Calcular índices para la página actual
            inicio = (pagina_actual - 1) * registros_por_pagina
            fin = min(inicio + registros_por_pagina, total_registros)
            
            # Mostrar registros de la página actual
            df_pagina = df_mostrar.iloc[inicio:fin]
            
            st.dataframe(df_pagina, use_container_width=True)
            
            # Información de paginación
            st.info(f"📊 Mostrando registros {inicio + 1}-{fin} de {total_registros} registros de auditoría (5 por página)")
        else:
            st.warning("No hay columnas disponibles para mostrar.") 