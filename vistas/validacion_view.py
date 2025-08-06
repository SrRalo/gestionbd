import streamlit as st
from datetime import datetime
from logica_negocio.validacion_logic import validacion_logic

def mostrar_vista_validacion():
    """
    Muestra la vista de validación y limpieza de datos.
    """
    st.title("🔧 Validación y Limpieza de Datos")
    st.markdown("---")
    
    # Verificar permisos de administrador (múltiples formas)
    is_admin = (
        st.session_state.get('is_admin', False) or 
        st.session_state.get('user_role') == 'admin_reservas' or
        (st.session_state.get('current_user') and 
         st.session_state.get('current_user', {}).get('rol_principal') == 'admin_reservas')
    )
    
    if not is_admin:
        st.error("❌ Acceso denegado. Solo los administradores pueden acceder a esta sección.")
        st.info(f"Tu rol actual es: {st.session_state.get('user_role', 'No definido')}")
        st.info("Se requiere el rol 'admin_reservas' para acceder a esta funcionalidad.")
        return
    
    # Pestañas para diferentes operaciones
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Validación", "🧹 Limpieza", "💾 Backup", "📈 Estadísticas"])
    
    with tab1:
        mostrar_tab_validacion()
    
    with tab2:
        mostrar_tab_limpieza()
    
    with tab3:
        mostrar_tab_backup()
    
    with tab4:
        mostrar_tab_estadisticas()

def mostrar_tab_validacion():
    """Muestra la pestaña de validación de datos."""
    st.header("📊 Validación de Datos")
    st.write("Valide la integridad de los datos en las tablas del sistema.")
    
    # Validación individual por tabla
    st.subheader("Validación por Tabla")
    tabla_seleccionada = st.selectbox(
        "Seleccione la tabla a validar:",
        validacion_logic.tablas_disponibles,
        key="tabla_validacion"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Validar Tabla", key="btn_validar_tabla"):
            with st.spinner("Validando datos..."):
                resultado = validacion_logic.validar_tabla(tabla_seleccionada)
                if resultado:
                    st.session_state['ultima_validacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with col2:
        if st.button("🔍 Validar Todas las Tablas", key="btn_validar_todas"):
            with st.spinner("Validando todas las tablas..."):
                resultados = validacion_logic.validar_todas_las_tablas()
                if resultados:
                    st.session_state['ultima_validacion'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Información sobre validación
    st.info("""
    **¿Qué hace la validación?**
    - Verifica duplicados en emails y teléfonos de clientes
    - Revisa reservas con fechas pasadas
    - Valida duraciones de reservas
    - Comprueba precios negativos en canchas
    - Verifica montos negativos en pagos
    """)

def mostrar_tab_limpieza():
    """Muestra la pestaña de limpieza de datos."""
    st.header("🧹 Limpieza de Datos")
    st.write("Limpie datos problemáticos en las tablas del sistema.")
    
    # Advertencia importante
    st.warning("⚠️ **ADVERTENCIA**: La limpieza de datos es irreversible. Asegúrese de tener un backup antes de proceder.")
    
    # Confirmación para limpieza
    st.session_state['confirmar_limpieza'] = st.checkbox(
        "Confirmo que entiendo que la limpieza es irreversible",
        key="confirmar_limpieza_checkbox"
    )
    
    # Limpieza individual por tabla
    st.subheader("Limpieza por Tabla")
    tabla_seleccionada = st.selectbox(
        "Seleccione la tabla a limpiar:",
        validacion_logic.tablas_disponibles,
        key="tabla_limpieza"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Limpiar Tabla", key="btn_limpiar_tabla"):
            if st.session_state['confirmar_limpieza']:
                with st.spinner("Limpiando datos..."):
                    resultado = validacion_logic.limpiar_tabla(tabla_seleccionada)
                    if resultado:
                        st.session_state['ultima_limpieza'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                st.error("❌ Debe confirmar que entiende que la limpieza es irreversible.")
    
    with col2:
        st.session_state['confirmar_limpieza_total'] = st.checkbox(
            "Confirmo limpieza de TODAS las tablas",
            key="confirmar_limpieza_total_checkbox"
        )
        
        if st.button("🧹 Limpiar Todas las Tablas", key="btn_limpiar_todas"):
            if st.session_state['confirmar_limpieza'] and st.session_state['confirmar_limpieza_total']:
                with st.spinner("Limpiando todas las tablas..."):
                    resultados = validacion_logic.limpiar_todas_las_tablas()
                    if resultados:
                        st.session_state['ultima_limpieza'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                st.error("❌ Debe confirmar ambas opciones para proceder.")
    
    # Información sobre limpieza
    st.info("""
    **¿Qué hace la limpieza?**
    - Elimina clientes duplicados (mantiene el más reciente)
    - Cancela reservas con fechas pasadas
    - Corrige precios negativos en canchas
    - Corrige montos negativos en pagos
    """)

def mostrar_tab_backup():
    """Muestra la pestaña de backup de datos."""
    st.header("💾 Backup de Datos")
    st.write("Cree copias de seguridad de las tablas del sistema.")
    
    # Backup individual por tabla
    st.subheader("Backup por Tabla")
    tabla_seleccionada = st.selectbox(
        "Seleccione la tabla para crear backup:",
        validacion_logic.tablas_disponibles,
        key="tabla_backup"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Crear Backup", key="btn_backup_tabla"):
            with st.spinner("Creando backup..."):
                resultado = validacion_logic.crear_backup_tabla(tabla_seleccionada)
                if resultado:
                    st.session_state['ultimo_backup'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with col2:
        if st.button("💾 Backup de Todas las Tablas", key="btn_backup_todas"):
            with st.spinner("Creando backup de todas las tablas..."):
                resultados = validacion_logic.crear_backup_todas_las_tablas()
                if resultados:
                    st.session_state['ultimo_backup'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Información sobre backup
    st.info("""
    **¿Qué hace el backup?**
    - Crea una copia completa de la tabla seleccionada
    - El nombre del backup incluye la fecha y hora
    - Los backups se almacenan en la misma base de datos
    - Formato: tabla_backup_YYYYMMDD_HHMMSS
    """)

def mostrar_tab_estadisticas():
    """Muestra la pestaña de estadísticas de validación."""
    st.header("📈 Estadísticas de Validación")
    st.write("Información sobre el estado de validación del sistema.")
    
    # Obtener estadísticas
    estadisticas = validacion_logic.obtener_estadisticas_validacion()
    
    if estadisticas:
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Tablas", estadisticas['total_tablas'])
        
        with col2:
            st.metric("Última Validación", estadisticas['ultima_validacion'])
        
        with col3:
            st.metric("Última Limpieza", estadisticas['ultima_limpieza'])
        
        # Tablas disponibles
        st.subheader("Tablas Disponibles")
        for tabla in estadisticas['tablas_disponibles']:
            st.write(f"• {tabla}")
        
        # Último backup
        st.subheader("Último Backup")
        st.write(f"**Fecha:** {estadisticas['ultimo_backup']}")
        
        # Información adicional
        st.info("""
        **Recomendaciones:**
        - Ejecute validación al menos una vez por semana
        - Realice backup antes de cualquier limpieza
        - Monitoree regularmente la integridad de los datos
        """)
    else:
        st.error("❌ No se pudieron obtener las estadísticas de validación.")

def mostrar_vista_validacion_admin():
    """
    Vista simplificada para administradores.
    """
    st.title("🔧 Administración de Datos")
    
    # Verificar permisos
    if not st.session_state.get('is_admin', False):
        st.error("❌ Acceso denegado.")
        return
    
    # Operaciones rápidas
    st.subheader("Operaciones Rápidas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Validar Todo", key="btn_validar_rapido"):
            with st.spinner("Validando..."):
                validacion_logic.validar_todas_las_tablas()
    
    with col2:
        if st.button("💾 Backup Todo", key="btn_backup_rapido"):
            with st.spinner("Creando backup..."):
                validacion_logic.crear_backup_todas_las_tablas()
    
    with col3:
        if st.button("📊 Ver Estadísticas", key="btn_stats_rapido"):
            estadisticas = validacion_logic.obtener_estadisticas_validacion()
            if estadisticas:
                st.json(estadisticas) 