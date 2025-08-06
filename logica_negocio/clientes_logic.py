import streamlit as st
import re
from datetime import date
from capa_datos.clientes_data import (
    insert_cliente_db, get_clientes_db, get_cliente_by_id_db, 
    update_cliente_db, delete_cliente_db, search_clientes_db,
    get_clientes_activos_db
)

class ClientesLogic:
    """
    Lógica de negocio para la gestión de clientes.
    """
    
    def __init__(self):
        self.conn = st.session_state.get('db_connection')
    
    def validar_email(self, email):
        """
        Valida el formato de un email.
        
        Args:
            email (str): Email a validar
        
        Returns:
            bool: True si el email es válido
        """
        if not email:
            return False
        
        # Patrón básico para validar email
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def validar_telefono(self, telefono):
        """
        Valida el formato de un teléfono.
        
        Args:
            telefono (str): Teléfono a validar
        
        Returns:
            bool: True si el teléfono es válido
        """
        if not telefono:
            return True  # El teléfono es opcional
        
        # Eliminar espacios, guiones y paréntesis
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', telefono)
        
        # Verificar que solo contenga dígitos y posiblemente un +
        if not re.match(r'^\+?[\d]+$', telefono_limpio):
            return False
        
        # Verificar longitud mínima (al menos 7 dígitos)
        if len(telefono_limpio.replace('+', '')) < 7:
            return False
        
        return True
    
    # def validar_documento(self, documento):
    #     """
    #     Valida el formato de un documento de identidad.
    #     
    #     Args:
    #         documento (str): Documento a validar
    #     
    #     Returns:
    #         bool: True si el documento es válido
    #     """
    #     if not documento:
    #         return True  # El documento es opcional
    #     
    #     # Eliminar espacios y guiones
    #     documento_limpio = re.sub(r'[\s\-]', '', documento)
    #     
    #     # Verificar que solo contenga dígitos y letras
    #     if not re.match(r'^[A-Za-z0-9]+$', documento_limpio):
    #         return False
    #     
    #     # Verificar longitud mínima (al menos 5 caracteres)
    #     if len(documento_limpio) < 5:
    #         return False
    #     
    #     return True
    
    def validar_fecha_nacimiento(self, fecha_nacimiento):
        """
        Valida una fecha de nacimiento.
        
        Args:
            fecha_nacimiento (date): Fecha de nacimiento a validar
        
        Returns:
            bool: True si la fecha es válida
        """
        if not fecha_nacimiento:
            return True  # La fecha de nacimiento es opcional
        
        # Verificar que no sea una fecha futura
        if fecha_nacimiento > date.today():
            return False
        
        # Verificar que la persona tenga al menos 1 año
        edad_minima = date.today().replace(year=date.today().year - 1)
        if fecha_nacimiento > edad_minima:
            return False
        
        # Verificar que la persona no tenga más de 120 años
        edad_maxima = date.today().replace(year=date.today().year - 120)
        if fecha_nacimiento < edad_maxima:
            return False
        
        return True
    
    def agregar_cliente(self, nombre, apellido, telefono, email, fecha_nacimiento):
        """
        Agrega un nuevo cliente con validaciones.
        
        Args:
            nombre (str): Nombre del cliente
            apellido (str): Apellido del cliente
            telefono (str): Teléfono del cliente
            email (str): Email del cliente
            fecha_nacimiento (date): Fecha de nacimiento
        
        Returns:
            int: ID del cliente creado o None si hay error
        """
        # Validaciones básicas
        if not nombre or not nombre.strip():
            st.error("El nombre es obligatorio.")
            return None
        
        if not apellido or not apellido.strip():
            st.error("El apellido es obligatorio.")
            return None
        
        if not email or not email.strip():
            st.error("El email es obligatorio.")
            return None
        
        # Validar formato de email
        if not self.validar_email(email):
            st.error("El formato del email no es válido.")
            return None
        
        # Validar teléfono
        if not self.validar_telefono(telefono):
            st.error("El formato del teléfono no es válido.")
            return None
        
        # Validar fecha de nacimiento
        if not self.validar_fecha_nacimiento(fecha_nacimiento):
            st.error("La fecha de nacimiento no es válida.")
            return None
        
        # Limpiar datos
        nombre = nombre.strip()
        apellido = apellido.strip()
        email = email.strip().lower()
        telefono = telefono.strip() if telefono else None
        
        # Verificar si el email ya existe
        clientes_existentes = self.buscar_clientes_por_email(email)
        if clientes_existentes:
            st.error(f"Ya existe un cliente con el email '{email}'.")
            return None
        
        # Insertar cliente
        try:
            cliente_id = insert_cliente_db(
                self.conn, nombre, apellido, telefono, email, 
                fecha_nacimiento
            )
            
            if cliente_id:
                st.success(f"Cliente '{nombre} {apellido}' agregado exitosamente con ID: {cliente_id}")
                return cliente_id
            else:
                st.error("Error al agregar el cliente.")
                return None
                
        except Exception as e:
            st.error(f"Error inesperado al agregar cliente: {e}")
            return None
    
    def obtener_clientes(self, solo_activos=False):
        """
        Obtiene la lista de clientes.
        
        Args:
            solo_activos (bool): Si True, solo retorna clientes activos
        
        Returns:
            list: Lista de clientes
        """
        try:
            if solo_activos:
                return get_clientes_activos_db(self.conn)
            else:
                return get_clientes_db(self.conn)
        except Exception as e:
            st.error(f"Error al obtener clientes: {e}")
            return []
    
    def obtener_cliente_por_id(self, cliente_id):
        """
        Obtiene un cliente específico por su ID.
        
        Args:
            cliente_id (int): ID del cliente
        
        Returns:
            dict: Datos del cliente o None si no existe
        """
        try:
            return get_cliente_by_id_db(self.conn, cliente_id)
        except Exception as e:
            st.error(f"Error al obtener cliente: {e}")
            return None
    
    def actualizar_cliente(self, cliente_id, nombre, apellido, telefono, email, fecha_nacimiento, estado):
        """
        Actualiza los datos de un cliente con validaciones.
        
        Args:
            cliente_id (int): ID del cliente a actualizar
            nombre (str): Nuevo nombre
            apellido (str): Nuevo apellido
            telefono (str): Nuevo teléfono
            email (str): Nuevo email
            fecha_nacimiento (date): Nueva fecha de nacimiento
            estado (str): Estado del cliente (Activo/Inactivo)
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        # Validaciones básicas
        if not nombre or not nombre.strip():
            st.error("El nombre es obligatorio.")
            return False
        
        if not apellido or not apellido.strip():
            st.error("El apellido es obligatorio.")
            return False
        
        if not email or not email.strip():
            st.error("El email es obligatorio.")
            return False
        
        # Validar formato de email
        if not self.validar_email(email):
            st.error("El formato del email no es válido.")
            return False
        
        # Validar teléfono
        if not self.validar_telefono(telefono):
            st.error("El formato del teléfono no es válido.")
            return False
        
        # Validar fecha de nacimiento
        if not self.validar_fecha_nacimiento(fecha_nacimiento):
            st.error("La fecha de nacimiento no es válida.")
            return False
        
        # Limpiar datos
        nombre = nombre.strip()
        apellido = apellido.strip()
        email = email.strip().lower()
        telefono = telefono.strip() if telefono else None
        
        # Verificar si el email ya existe en otro cliente
        clientes_existentes = self.buscar_clientes_por_email(email)
        for cliente in clientes_existentes:
            if cliente['id'] != cliente_id:
                st.error(f"Ya existe otro cliente con el email '{email}'.")
                return False
        
        # Actualizar cliente
        try:
            success = update_cliente_db(
                self.conn, cliente_id, nombre, apellido, telefono, 
                email, fecha_nacimiento, estado
            )
            
            if success:
                st.success(f"Cliente '{nombre} {apellido}' actualizado exitosamente.")
                return True
            else:
                st.error("Error al actualizar el cliente.")
                return False
                
        except Exception as e:
            st.error(f"Error inesperado al actualizar cliente: {e}")
            return False
    
    def eliminar_cliente(self, cliente_id):
        """
        Elimina un cliente.
        
        Args:
            cliente_id (int): ID del cliente a eliminar
        
        Returns:
            bool: True si la eliminación fue exitosa
        """
        try:
            # Obtener información del cliente antes de eliminar
            cliente = self.obtener_cliente_por_id(cliente_id)
            if not cliente:
                st.error("Cliente no encontrado.")
                return False
            
            success = delete_cliente_db(self.conn, cliente_id)
            
            if success:
                st.success(f"Cliente '{cliente['nombre']} {cliente['apellido']}' eliminado exitosamente.")
                return True
            else:
                st.error("Error al eliminar el cliente.")
                return False
                
        except Exception as e:
            st.error(f"Error inesperado al eliminar cliente: {e}")
            return False
    
    def buscar_clientes(self, termino_busqueda):
        """
        Busca clientes por nombre, apellido, email o documento.
        
        Args:
            termino_busqueda (str): Término de búsqueda
        
        Returns:
            list: Lista de clientes que coinciden con la búsqueda
        """
        try:
            if not termino_busqueda or not termino_busqueda.strip():
                return self.obtener_clientes()
            
            return search_clientes_db(self.conn, termino_busqueda.strip())
        except Exception as e:
            st.error(f"Error al buscar clientes: {e}")
            return []
    
    def buscar_clientes_por_email(self, email):
        """
        Busca clientes por email específico.
        
        Args:
            email (str): Email a buscar
        
        Returns:
            list: Lista de clientes con ese email
        """
        try:
            return search_clientes_db(self.conn, email)
        except Exception as e:
            st.error(f"Error al buscar clientes por email: {e}")
            return []
    
    # def buscar_clientes_por_documento(self, documento):
    #     """
    #     Busca clientes por documento específico.
    #     
    #     Args:
    #         documento (str): Documento a buscar
    #     
    #     Returns:
    #         list: Lista de clientes con ese documento
    #     """
    #     try:
    #         return search_clientes_db(self.conn, documento)
    #     except Exception as e:
    #         st.error(f"Error al buscar clientes por documento: {e}")
    #         return []
    
    def obtener_estadisticas_clientes(self):
        """
        Obtiene estadísticas básicas de clientes.
        
        Returns:
            dict: Estadísticas de clientes
        """
        try:
            clientes = self.obtener_clientes()
            clientes_activos = [c for c in clientes if c['estado'] == 'Activo']
            
            return {
                'total_clientes': len(clientes),
                'clientes_activos': len(clientes_activos),
                'clientes_inactivos': len(clientes) - len(clientes_activos)
            }
        except Exception as e:
            st.error(f"Error al obtener estadísticas de clientes: {e}")
            return {
                'total_clientes': 0,
                'clientes_activos': 0,
                'clientes_inactivos': 0
            }

    def get_all_clientes(self):
        """Obtener todos los clientes"""
        try:
            return self.obtener_clientes()
        except Exception as e:
            st.error(f"Error al obtener clientes: {e}")
            return []
    
    def get_cliente_by_id(self, cliente_id):
        """Obtener cliente por ID"""
        try:
            return self.obtener_cliente_por_id(cliente_id)
        except Exception as e:
            st.error(f"Error al obtener cliente por ID: {e}")
            return None
    
    def crear_cliente(self, datos_cliente):
        """Crear nuevo cliente con datos completos"""
        try:
            return self.agregar_cliente(
                nombre=datos_cliente['nombre'],
                apellido=datos_cliente['apellido'],
                telefono=datos_cliente.get('telefono', ''),
                email=datos_cliente['email'],
                fecha_nacimiento=datos_cliente.get('fecha_nacimiento')
            )
        except Exception as e:
            st.error(f"Error al crear cliente: {e}")
            return {'success': False, 'message': str(e)}
    
    def actualizar_cliente_completo(self, cliente_id, datos_actualizados):
        """Actualizar cliente"""
        try:
            return self.actualizar_cliente(
                cliente_id=cliente_id,
                nombre=datos_actualizados['nombre'],
                apellido=datos_actualizados['apellido'],
                telefono=datos_actualizados.get('telefono', ''),
                email=datos_actualizados['email'],
                fecha_nacimiento=datos_actualizados.get('fecha_nacimiento'),
                estado=datos_actualizados['estado']
            )
        except Exception as e:
            st.error(f"Error al actualizar cliente: {e}")
            return {'success': False, 'message': str(e)}
    
    def eliminar_cliente(self, cliente_id):
        """Eliminar cliente"""
        try:
            return self.eliminar_cliente(cliente_id)
        except Exception as e:
            st.error(f"Error al eliminar cliente: {e}")
            return {'success': False, 'message': str(e)}
    
    def get_clientes_filtrados(self, estado=None, search_term=None):
        """Obtener clientes con filtros"""
        try:
            clientes = self.obtener_clientes()
            
            # Aplicar filtros
            if estado:
                clientes = [c for c in clientes if c['estado'] == estado]
            
            if search_term:
                search_term = search_term.lower()
                clientes = [c for c in clientes 
                          if search_term in c['nombre'].lower() 
                          or search_term in c['apellido'].lower()
                          or search_term in c.get('email', '').lower()]
            
            return clientes
            
        except Exception as e:
            st.error(f"Error al obtener clientes filtrados: {e}")
            return []
    
    def get_actividad_clientes(self):
        """Obtener actividad de clientes (número de reservas)"""
        try:
            from logica_negocio.reservas_logic import ReservasLogic
            reservas_logic = ReservasLogic()
            
            clientes = self.obtener_clientes()
            result = []
            
            for cliente in clientes:
                # Obtener reservas del cliente
                reservas_cliente = reservas_logic.obtener_reservas_por_cliente(cliente['id'])
                
                result.append({
                    'nombre_completo': f"{cliente['nombre']} {cliente['apellido']}",
                    'reservas_totales': len(reservas_cliente),
                    'email': cliente.get('email', ''),
                    'estado': cliente['estado']
                })
            
            # Ordenar por número de reservas (descendente)
            result.sort(key=lambda x: x['reservas_totales'], reverse=True)
            
            return result
            
        except Exception as e:
            st.error(f"Error al obtener actividad de clientes: {e}")
            return []
    
    def get_reservas_activas_cliente(self, cliente_id):
        """Obtener reservas activas de un cliente"""
        try:
            from logica_negocio.reservas_logic import ReservasLogic
            reservas_logic = ReservasLogic()
            
            reservas_cliente = reservas_logic.obtener_reservas_por_cliente(cliente_id)
            
            # Filtrar solo reservas activas (confirmadas o pendientes)
            reservas_activas = [r for r in reservas_cliente 
                              if r['estado'] in ['confirmada', 'pendiente']]
            
            return reservas_activas
            
        except Exception as e:
            st.error(f"Error al obtener reservas activas del cliente: {e}")
            return []

# Instancia global de la lógica de clientes
clientes_logic = ClientesLogic() 