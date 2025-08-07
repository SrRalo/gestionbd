import streamlit as st
import pandas as pd
from datetime import datetime, date, time, timedelta
from logica_negocio.reservas_logic import ReservasLogic
from logica_negocio.clientes_logic import ClientesLogic
from logica_negocio.canchas_logic import CanchasLogic

class ReservasView:
    """
    Vista para la gestión de reservas.
    """
    
    def __init__(self):
        self.reservas_logic = ReservasLogic()
        self.clientes_logic = ClientesLogic()
        self.canchas_logic = CanchasLogic()
    
    def show(self):
        """Mostrar la vista principal de reservas"""
        st.markdown("## 📅 Gestión de Reservas")
        
        # Tabs para diferentes funcionalidades
        tab1, tab2, tab3 = st.tabs(["➕ Crear Reserva", "📋 Ver Reservas", "🔍 Buscar Reservas"])
        
        with tab1:
            self.show_crear_reserva_form()
        
        with tab2:
            self.show_lista_reservas()
        
        with tab3:
            self.show_buscar_reservas()
    
    def show_crear_reserva_form(self):
        """Mostrar formulario para crear una nueva reserva"""
        st.markdown("### ➕ Crear Nueva Reserva")
        st.markdown("*Complete todos los campos para crear una nueva reserva*")
        
        # Obtener datos para los menús desplegables
        clientes = self.obtener_clientes_para_select()
        canchas = self.obtener_canchas_para_select()
        
        if not clientes:
            st.error("❌ No hay clientes disponibles. Debe crear al menos un cliente primero.")
            return
        
        if not canchas:
            st.error("❌ No hay canchas disponibles. Debe crear al menos una cancha primero.")
            return
        
        with st.form("form_crear_reserva"):
            # Sección 1: Información básica
            st.markdown("**👤 Información del Cliente y Cancha**")
            col1, col2 = st.columns(2)
            
            with col1:
                # Menú desplegable para clientes
                cliente_options = {f"{cliente['nombre'] or ''} {cliente['apellido'] or ''} (ID: {cliente['id']})": cliente['id'] 
                                 for cliente in clientes}
                cliente_seleccionado = st.selectbox(
                    "Cliente *",
                    options=list(cliente_options.keys()),
                    help="Seleccione el cliente que realizará la reserva"
                )
                cliente_id = cliente_options[cliente_seleccionado] if cliente_seleccionado else None
            
            with col2:
                # Menú desplegable para canchas
                cancha_options = {f"{cancha['nombre']} - {cancha['tipo_cancha_nombre'] or 'Sin tipo'} (ID: {cancha['id']})": cancha['id']
                                for cancha in canchas}
                cancha_seleccionada = st.selectbox(
                    "Cancha *",
                    options=list(cancha_options.keys()),
                    help="Seleccione la cancha para la reserva"
                )
                cancha_id = cancha_options[cancha_seleccionada] if cancha_seleccionada else None
            
            st.markdown("---")
            
            # Sección 2: Fecha y horario
            st.markdown("**📅 Fecha y Horario**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Selector de fecha
                fecha_reserva = st.date_input(
                    "Fecha de Reserva *",
                    min_value=date.today(),
                    max_value=date.today() + timedelta(days=90),
                    value=date.today(),
                    help="Seleccione la fecha para la reserva"
                )
            
            with col2:
                # Selector de hora de inicio
                hora_inicio = st.time_input(
                    "Hora de Inicio *",
                    value=time(14, 0),
                    help="Seleccione la hora de inicio"
                )
            
            with col3:
                # Selector de duración
                duracion_opciones = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
                duracion = st.selectbox(
                    "Duración (horas) *",
                    options=duracion_opciones,
                    index=1,  # 1.0 hora por defecto
                    help="Seleccione la duración de la reserva"
                )
            
            # Calcular hora de fin automáticamente
            if hora_inicio and duracion:
                hora_fin = self.calcular_hora_fin(hora_inicio, duracion)
                st.info(f"⏰ **Hora de fin calculada:** {hora_fin.strftime('%H:%M')}")
            
            st.markdown("---")
            
            # Sección 3: Estado y observaciones
            st.markdown("**📝 Estado y Observaciones**")
            col1, col2 = st.columns(2)
            
            with col1:
                # Menú desplegable para estado
                estado_opciones = ["pendiente", "confirmada", "cancelada", "completada"]
                estado = st.selectbox(
                    "Estado *",
                    options=estado_opciones,
                    index=0,  # pendiente por defecto
                    help="Seleccione el estado inicial de la reserva"
                )
            
            with col2:
                # Campo de observaciones
                observaciones = st.text_area(
                    "Observaciones",
                    placeholder="Ej: Partido de fútbol, Entrenamiento, Torneo, etc.",
                    height=100,
                    help="Agregue cualquier observación o detalle adicional"
                )
            
            # Botón de envío
            submitted = st.form_submit_button("📅 Crear Reserva")
            
            if submitted:
                self.procesar_creacion_reserva(
                    cliente_id, cancha_id, fecha_reserva, 
                    hora_inicio, hora_fin, duracion, estado, observaciones
                )
    
    def calcular_hora_fin(self, hora_inicio, duracion):
        """Calcular la hora de fin basada en la hora de inicio y duración"""
        duracion_minutos = int(duracion * 60)
        hora_fin_minutos = hora_inicio.hour * 60 + hora_inicio.minute + duracion_minutos
        
        hora_fin_hora = hora_fin_minutos // 60
        hora_fin_minuto = hora_fin_minutos % 60
        
        return time(hora_fin_hora, hora_fin_minuto)
    
    def obtener_clientes_para_select(self):
        """Obtener lista de clientes para el menú desplegable"""
        try:
            clientes_tuples = self.clientes_logic.obtener_clientes_activos()
            if not clientes_tuples:
                return []
            
            # Convertir tuplas a diccionarios
            clientes = []
            for cliente_tuple in clientes_tuples:
                cliente_dict = {
                    'id': cliente_tuple[0],
                    'nombre': cliente_tuple[1],
                    'apellido': cliente_tuple[2],
                    'telefono': cliente_tuple[3],
                    'email': cliente_tuple[4],
                    'fecha_nacimiento': cliente_tuple[5],
                    'estado': cliente_tuple[6],
                    'fecha_registro': cliente_tuple[7],
                    'fecha_actualizacion': cliente_tuple[8]
                }
                clientes.append(cliente_dict)
            
            return clientes
        except Exception as e:
            st.error(f"Error al obtener clientes: {e}")
            return []
    
    def obtener_canchas_para_select(self):
        """Obtener lista de canchas para el menú desplegable"""
        try:
            canchas_tuples = self.canchas_logic.obtener_canchas_con_tipos()
            if not canchas_tuples:
                return []
            
            # Convertir tuplas a diccionarios
            canchas = []
            for cancha_tuple in canchas_tuples:
                cancha_dict = {
                    'id': cancha_tuple[0],
                    'nombre': cancha_tuple[1],
                    'tipo_deporte': cancha_tuple[2],
                    'capacidad': cancha_tuple[3],
                    'precio_hora': cancha_tuple[4],
                    'estado': cancha_tuple[5],
                    'horario_apertura': cancha_tuple[6],
                    'horario_cierre': cancha_tuple[7],
                    'descripcion': cancha_tuple[8],
                    'fecha_creacion': cancha_tuple[9],
                    'fecha_actualizacion': cancha_tuple[10],
                    'tipo_cancha_id': cancha_tuple[11],
                    'tipo_cancha_nombre': cancha_tuple[12],
                    'tipo_cancha_descripcion': cancha_tuple[13],
                    'precio_por_hora': cancha_tuple[14]
                }
                canchas.append(cancha_dict)
            
            return canchas
        except Exception as e:
            st.error(f"Error al obtener canchas: {e}")
            return []
    
    def procesar_creacion_reserva(self, cliente_id, cancha_id, fecha_reserva, 
                                hora_inicio, hora_fin, duracion, estado, observaciones):
        """Procesar la creación de la reserva"""
        # Validaciones básicas
        if not all([cliente_id, cancha_id, fecha_reserva, hora_inicio, hora_fin, duracion]):
            st.error("❌ Por favor complete todos los campos obligatorios")
            return
        
        try:
            # Crear la reserva usando la lógica de negocio
            reserva_id = self.reservas_logic.crear_reserva(
                cliente_id=cliente_id,
                cancha_id=cancha_id,
                fecha_reserva=fecha_reserva,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                observaciones=observaciones
            )
            
            if reserva_id:
                st.success(f"""
                ✅ **Reserva creada exitosamente!**
                
                **Detalles de la reserva:**
                - ID de Reserva: {reserva_id}
                - Cliente ID: {cliente_id}
                - Cancha ID: {cancha_id}
                - Fecha: {fecha_reserva.strftime('%d/%m/%Y')}
                - Hora: {hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}
                - Duración: {duracion} horas
                - Estado: {estado}
                """)
                
                # Limpiar el formulario
                st.rerun()
            else:
                st.error("❌ Error al crear la reserva. Verifique que la cancha esté disponible en el horario seleccionado.")
                
        except Exception as e:
            st.error(f"❌ Error al crear la reserva: {e}")
    
    def show_lista_reservas(self):
        """Mostrar lista de todas las reservas"""
        st.markdown("### 📋 Lista de Reservas")
        
        try:
            # Conexión directa a la base de datos
            from capa_datos.database_connection import get_db_connection
            conn = get_db_connection()
            
            if not conn:
                st.error("❌ No se pudo conectar a la base de datos")
                return
            
            # Consulta directa y simple
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM reservas ORDER BY fecha_reserva DESC, hora_inicio DESC")
                reservas_raw = cur.fetchall()
                
                # Obtener nombres de columnas
                column_names = [desc[0] for desc in cur.description]
            
            conn.close()
            
            if reservas_raw:
                # Convertir a lista de diccionarios
                reservas = []
                for row in reservas_raw:
                    reserva_dict = dict(zip(column_names, row))
                    reservas.append(reserva_dict)
                
                # Crear DataFrame para mejor visualización
                df = pd.DataFrame(reservas)
                
                # Renombrar columnas para mejor visualización
                df_renamed = df.rename(columns={
                    'id': 'ID',
                    'cliente_id': 'Cliente ID',
                    'cancha_id': 'Cancha ID',
                    'fecha_reserva': 'Fecha',
                    'hora_inicio': 'Hora Inicio',
                    'hora_fin': 'Hora Fin',
                    'duracion': 'Duración',
                    'estado': 'Estado',
                    'observaciones': 'Observaciones',
                    'fecha_creacion': 'Fecha Creación'
                })
                
                # Formatear columnas de fecha y hora
                if 'Fecha' in df_renamed.columns:
                    df_renamed['Fecha'] = pd.to_datetime(df_renamed['Fecha']).dt.strftime('%d/%m/%Y')
                
                if 'Hora Inicio' in df_renamed.columns:
                    # Convertir objetos time a string directamente
                    df_renamed['Hora Inicio'] = df_renamed['Hora Inicio'].apply(
                        lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else str(x)
                    )
                
                if 'Hora Fin' in df_renamed.columns:
                    # Convertir objetos time a string directamente
                    df_renamed['Hora Fin'] = df_renamed['Hora Fin'].apply(
                        lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else str(x)
                    )
                
                # Mostrar registros
                st.dataframe(df_renamed, use_container_width=True)
                
                # Estadísticas simples
                total_registros = len(reservas)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Reservas", total_registros)
                with col2:
                    confirmadas = len([r for r in reservas if r.get('estado', '').lower() == 'confirmada'])
                    st.metric("Confirmadas", confirmadas)
                with col3:
                    pendientes = len([r for r in reservas if r.get('estado', '').lower() == 'pendiente'])
                    st.metric("Pendientes", pendientes)
                with col4:
                    canceladas = len([r for r in reservas if r.get('estado', '').lower() == 'cancelada'])
                    st.metric("Canceladas", canceladas)
                    
                st.success(f"✅ Se encontraron {total_registros} reservas en la base de datos")
            else:
                st.info("📭 No hay reservas registradas")
                
        except Exception as e:
            st.error(f"Error al obtener reservas: {e}")
            st.error(f"Detalles del error: {str(e)}")
    
    def show_buscar_reservas(self):
        """Mostrar opciones de búsqueda de reservas"""
        st.markdown("### 🔍 Buscar Reservas")
        
        col1, col2 = st.columns(2)
        
        # Búsqueda por fecha
        with col1:
            fecha_busqueda = st.date_input(
                "Buscar por fecha",
                value=date.today()
            )
            
            if st.button("🔍 Buscar por Fecha", key="buscar_fecha_btn"):
                if fecha_busqueda:
                    self.reservas_filtradas = self.reservas_logic.obtener_reservas_por_fecha(fecha_busqueda)
                    st.success(f"✅ Se encontraron {len(self.reservas_filtradas)} reservas para la fecha {fecha_busqueda}")
                else:
                    st.warning("⚠️ Por favor selecciona una fecha para buscar")
        
        # Búsqueda por estado
        with col2:
            estado_busqueda = st.selectbox("Estado:", ["Todos", "pendiente", "confirmada", "cancelada", "completada"], key="estado_busqueda")
            if st.button("🔍 Buscar por Estado", key="buscar_estado_btn"):
                if estado_busqueda != "Todos":
                    self.reservas_filtradas = self.reservas_logic.obtener_reservas_por_estado(estado_busqueda)
                    st.success(f"✅ Se encontraron {len(self.reservas_filtradas)} reservas con estado '{estado_busqueda}'")
                else:
                    self.reservas_filtradas = self.reservas_logic.obtener_todas_las_reservas()
                    st.success("✅ Mostrando todas las reservas")
    
    def mostrar_reservas_por_fecha(self, fecha):
        """Mostrar reservas por fecha específica"""
        try:
            reservas = self.reservas_logic.obtener_reservas_por_fecha(fecha)
            
            if reservas:
                df = pd.DataFrame(reservas)
                st.markdown(f"**Reservas para {fecha.strftime('%d/%m/%Y')}:**")
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"📭 No hay reservas para {fecha.strftime('%d/%m/%Y')}")
                
        except Exception as e:
            st.error(f"Error al buscar reservas por fecha: {e}")
    
    def mostrar_reservas_por_estado(self, estado):
        """Mostrar reservas por estado específico"""
        try:
            if not estado:
                st.warning("⚠️ Por favor seleccione un estado para buscar")
                return
            
            # Obtener todas las reservas y filtrar por estado
            reservas = self.reservas_logic.obtener_reservas()
            reservas_filtradas = [r for r in reservas if r.get('estado', '').lower() == estado.lower()]
            
            if reservas_filtradas:
                # Crear DataFrame para mejor visualización
                df = pd.DataFrame(reservas_filtradas)
                
                # Renombrar columnas para mejor visualización
                df_renamed = df.rename(columns={
                    'id': 'ID',
                    'cliente_id': 'Cliente ID',
                    'cancha_id': 'Cancha ID',
                    'fecha_reserva': 'Fecha',
                    'hora_inicio': 'Hora Inicio',
                    'hora_fin': 'Hora Fin',
                    'duracion': 'Duración',
                    'estado': 'Estado',
                    'observaciones': 'Observaciones',
                    'fecha_creacion': 'Fecha Creación'
                })
                
                # Formatear columnas de fecha y hora
                if 'Fecha' in df_renamed.columns:
                    df_renamed['Fecha'] = pd.to_datetime(df_renamed['Fecha']).dt.strftime('%d/%m/%Y')
                
                if 'Hora Inicio' in df_renamed.columns:
                    df_renamed['Hora Inicio'] = df_renamed['Hora Inicio'].apply(
                        lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else str(x)
                    )
                
                if 'Hora Fin' in df_renamed.columns:
                    df_renamed['Hora Fin'] = df_renamed['Hora Fin'].apply(
                        lambda x: x.strftime('%H:%M') if hasattr(x, 'strftime') else str(x)
                    )
                
                st.markdown(f"**Reservas con estado '{estado}':**")
                st.dataframe(df_renamed, use_container_width=True)
                
                # Mostrar estadísticas
                st.info(f"📊 **Total de reservas con estado '{estado}': {len(reservas_filtradas)}**")
            else:
                st.info(f"📭 No hay reservas con estado '{estado}'")
                
        except Exception as e:
            st.error(f"Error al buscar reservas por estado: {e}") 