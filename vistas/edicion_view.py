import streamlit as st
import pandas as pd
from datetime import time
from logica_negocio.canchas_logic import CanchasLogic

class EdicionView:
    """
    Vista para editar registros de canchas y tipos de cancha.
    """
    
    def __init__(self):
        self.canchas_logic = CanchasLogic()
    
    def show(self):
        """Mostrar la vista de edición completa"""
        
        st.markdown("## ✏️ Edición de Registros")
        
        # Pestañas para diferentes tipos de edición
        tab1, tab2 = st.tabs(["🏟️ Editar Canchas", "📋 Editar Tipos de Cancha"])
        
        with tab1:
            self.show_edicion_canchas()
        
        with tab2:
            self.show_edicion_tipos_cancha()
    
    def obtener_canchas_para_edicion(self):
        """Obtener lista de canchas convertida a diccionarios para edición"""
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
    
    def obtener_tipos_cancha_para_edicion(self):
        """Obtener lista de tipos de cancha convertida a diccionarios para edición"""
        try:
            tipos_tuples = self.canchas_logic.obtener_tipos_cancha()
            if not tipos_tuples:
                return []
            
            # Convertir tuplas a diccionarios
            tipos = []
            for tipo_tuple in tipos_tuples:
                tipo_dict = {
                    'id': tipo_tuple[0],
                    'nombre': tipo_tuple[1],
                    'descripcion': tipo_tuple[2],
                    'precio_por_hora': tipo_tuple[3],
                    'estado': tipo_tuple[4],
                    'fecha_creacion': tipo_tuple[5],
                    'fecha_actualizacion': tipo_tuple[6]
                }
                tipos.append(tipo_dict)
            
            return tipos
        except Exception as e:
            st.error(f"Error al obtener tipos de cancha: {e}")
            return []
    
    def show_edicion_canchas(self):
        """Mostrar interfaz para editar canchas"""
        st.markdown("### 🏟️ Gestión de Canchas")
        
        # Obtener canchas
        canchas = self.obtener_canchas_para_edicion()
        
        if not canchas:
            st.warning("No hay canchas disponibles para editar.")
            return
        
        # Crear DataFrame para la tabla
        df = pd.DataFrame(canchas)
        
        # Mostrar tabla con botones de acción
        st.markdown("#### 📊 Canchas Existentes")
        
        # Crear columnas para la tabla
        col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 1, 1, 1, 1, 2])
        
        with col1:
            st.write("**Nombre**")
        with col2:
            st.write("**Tipo Deporte**")
        with col3:
            st.write("**Capacidad**")
        with col4:
            st.write("**Precio/Hora**")
        with col5:
            st.write("**Estado**")
        with col6:
            st.write("**ID**")
        with col7:
            st.write("**Acciones**")
        
        # Mostrar cada cancha con botones de acción
        for idx, cancha in enumerate(canchas):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 2, 1, 1, 1, 1, 2])
            
            with col1:
                st.write(cancha.get('nombre', 'N/A'))
            with col2:
                st.write(cancha.get('tipo_deporte', 'N/A'))
            with col3:
                st.write(cancha.get('capacidad', 'N/A'))
            with col4:
                st.write(f"${cancha.get('precio_hora', 0):.2f}")
            with col5:
                estado = cancha.get('estado', 'N/A')
                if estado == 'Activa':
                    st.success(estado)
                elif estado == 'Inactiva':
                    st.error(estado)
                else:
                    st.warning(estado)
            with col6:
                st.write(cancha.get('id', 'N/A'))
            with col7:
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button(f"✏️ Editar", key=f"edit_cancha_{idx}"):
                        st.session_state.editing_cancha = cancha
                        st.session_state.show_edit_cancha_form = True
                with col_delete:
                    if st.button(f"🗑️ Eliminar", key=f"delete_cancha_{idx}"):
                        if self.eliminar_cancha(cancha.get('id')):
                            st.success("Cancha eliminada exitosamente!")
                            st.rerun()
        
        # Formulario de edición
        if st.session_state.get('show_edit_cancha_form', False) and st.session_state.get('editing_cancha'):
            self.show_formulario_edicion_cancha(st.session_state.editing_cancha)
    
    def show_formulario_edicion_cancha(self, cancha):
        """Mostrar formulario para editar una cancha"""
        st.markdown("---")
        st.markdown(f"### ✏️ Editar Cancha: {cancha.get('nombre', 'N/A')}")
        
        with st.form(f"form_editar_cancha_{cancha.get('id')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre", value=cancha.get('nombre', ''), key=f"edit_nombre_{cancha.get('id')}")
                tipo_deporte = st.selectbox(
                    "Tipo de Deporte",
                    ["Fútbol", "Basketball", "Tennis", "Voleibol", "Otro"],
                    index=["Fútbol", "Basketball", "Tennis", "Voleibol", "Otro"].index(cancha.get('tipo_deporte', 'Fútbol')),
                    key=f"edit_tipo_deporte_{cancha.get('id')}"
                )
                capacidad = st.number_input("Capacidad", min_value=1, value=cancha.get('capacidad', 50), key=f"edit_capacidad_{cancha.get('id')}")
                precio_hora = st.number_input("Precio por Hora ($)", min_value=0.0, value=float(cancha.get('precio_hora', 50.0)), step=0.5, key=f"edit_precio_{cancha.get('id')}")
            
            with col2:
                estado = st.selectbox(
                    "Estado",
                    ["Activa", "Inactiva", "Mantenimiento"],
                    index=["Activa", "Inactiva", "Mantenimiento"].index(cancha.get('estado', 'Activa')),
                    key=f"edit_estado_{cancha.get('id')}"
                )
                
                # Convertir horarios de string a time
                horario_apertura_str = cancha.get('horario_apertura', '06:00:00')
                horario_cierre_str = cancha.get('horario_cierre', '22:00:00')
                
                try:
                    hora_apertura = time.fromisoformat(horario_apertura_str)
                    hora_cierre = time.fromisoformat(horario_cierre_str)
                except:
                    hora_apertura = time(6, 0)
                    hora_cierre = time(22, 0)
                
                horario_apertura = st.time_input("Horario de Apertura", value=hora_apertura, key=f"edit_apertura_{cancha.get('id')}")
                horario_cierre = st.time_input("Horario de Cierre", value=hora_cierre, key=f"edit_cierre_{cancha.get('id')}")
            
            descripcion = st.text_area("Descripción", value=cancha.get('descripcion', ''), key=f"edit_descripcion_{cancha.get('id')}")
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Guardar Cambios"):
                    if self.actualizar_cancha(
                        cancha.get('id'), nombre, tipo_deporte, capacidad, precio_hora,
                        estado, horario_apertura.strftime("%H:%M:%S"), 
                        horario_cierre.strftime("%H:%M:%S"), descripcion, cancha.get('tipo_cancha_id', 1)
                    ):
                        st.success("✅ Cancha actualizada exitosamente!")
                        st.session_state.show_edit_cancha_form = False
                        st.session_state.editing_cancha = None
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar la cancha")
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_edit_cancha_form = False
                    st.session_state.editing_cancha = None
                    st.rerun()
    
    def show_edicion_tipos_cancha(self):
        """Mostrar interfaz para editar tipos de cancha"""
        st.markdown("### 📋 Gestión de Tipos de Cancha")
        
        # Obtener tipos de cancha
        tipos_cancha = self.obtener_tipos_cancha_para_edicion()
        
        if not tipos_cancha:
            st.warning("No hay tipos de cancha disponibles para editar.")
            return
        
        # Mostrar tabla con botones de acción
        st.markdown("#### 📊 Tipos de Cancha Existentes")
        
        # Crear columnas para la tabla
        col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 1, 1, 1, 2])
        
        with col1:
            st.write("**Nombre**")
        with col2:
            st.write("**Descripción**")
        with col3:
            st.write("**Precio/Hora**")
        with col4:
            st.write("**Activo**")
        with col5:
            st.write("**ID**")
        with col6:
            st.write("**Acciones**")
        
        # Mostrar cada tipo de cancha con botones de acción
        for idx, tipo in enumerate(tipos_cancha):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 3, 1, 1, 1, 2])
            
            with col1:
                st.write(tipo.get('nombre', 'N/A'))
            with col2:
                st.write(tipo.get('descripcion', 'N/A')[:50] + "..." if len(tipo.get('descripcion', '')) > 50 else tipo.get('descripcion', 'N/A'))
            with col3:
                st.write(f"${tipo.get('precio_por_hora', 0):.2f}")
            with col4:
                if tipo.get('estado', 'Activo') == 'Activo':
                    st.success("✅ Activo")
                else:
                    st.error("❌ Inactivo")
            with col5:
                st.write(tipo.get('id', 'N/A'))
            with col6:
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button(f"✏️ Editar", key=f"edit_tipo_{idx}"):
                        st.session_state.editing_tipo = tipo
                        st.session_state.show_edit_tipo_form = True
                with col_delete:
                    if st.button(f"🗑️ Eliminar", key=f"delete_tipo_{idx}"):
                        if self.eliminar_tipo_cancha(tipo.get('id')):
                            st.success("Tipo de cancha eliminado exitosamente!")
                            st.rerun()
        
        # Formulario de edición
        if st.session_state.get('show_edit_tipo_form', False) and st.session_state.get('editing_tipo'):
            self.show_formulario_edicion_tipo_cancha(st.session_state.editing_tipo)
    
    def show_formulario_edicion_tipo_cancha(self, tipo):
        """Mostrar formulario para editar un tipo de cancha"""
        st.markdown("---")
        st.markdown(f"### ✏️ Editar Tipo de Cancha: {tipo.get('nombre', 'N/A')}")
        
        with st.form(f"form_editar_tipo_{tipo.get('id')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre", value=tipo.get('nombre', ''), key=f"edit_tipo_nombre_{tipo.get('id')}")
                precio_por_hora = st.number_input("Precio por Hora ($)", min_value=0.0, value=float(tipo.get('precio_por_hora', 50.0)), step=0.5, key=f"edit_tipo_precio_{tipo.get('id')}")
            
            with col2:
                activo = st.checkbox("Activo", value=tipo.get('estado', 'Activo') == 'Activo', key=f"edit_tipo_activo_{tipo.get('id')}")
            
            descripcion = st.text_area("Descripción", value=tipo.get('descripcion', ''), key=f"edit_tipo_descripcion_{tipo.get('id')}")
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.form_submit_button("💾 Guardar Cambios"):
                    if self.actualizar_tipo_cancha(
                        tipo.get('id'), nombre, descripcion, precio_por_hora, activo
                    ):
                        st.success("✅ Tipo de cancha actualizado exitosamente!")
                        st.session_state.show_edit_tipo_form = False
                        st.session_state.editing_tipo = None
                        st.rerun()
                    else:
                        st.error("❌ Error al actualizar el tipo de cancha")
            
            with col_cancel:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.show_edit_tipo_form = False
                    st.session_state.editing_tipo = None
                    st.rerun()
    
    def actualizar_cancha(self, cancha_id, nombre, tipo_deporte, capacidad, precio_hora, 
                         estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id):
        """Actualizar una cancha"""
        return self.canchas_logic.actualizar_cancha(
            cancha_id, nombre, tipo_deporte, capacidad, precio_hora,
            estado, horario_apertura, horario_cierre, descripcion, tipo_cancha_id
        )
    
    def actualizar_tipo_cancha(self, tipo_id, nombre, descripcion, precio_por_hora, activo):
        """Actualizar un tipo de cancha"""
        return self.canchas_logic.actualizar_tipo_cancha(tipo_id, nombre, descripcion, precio_por_hora, activo)
    
    def eliminar_cancha(self, cancha_id):
        """Eliminar una cancha"""
        return self.canchas_logic.eliminar_cancha(cancha_id)
    
    def eliminar_tipo_cancha(self, tipo_id):
        """Eliminar un tipo de cancha"""
        return self.canchas_logic.eliminar_tipo_cancha(tipo_id) 