"""
Lógica de negocio para auditoría
"""
from capa_datos.auditoria_data import (
    get_auditoria_db,
    get_auditoria_por_fecha_db,
    get_auditoria_por_usuario_db,
    get_auditoria_por_tabla_db,
    get_auditoria_por_tipo_accion_db,
    get_estadisticas_auditoria_db,
    registrar_accion_auditoria
)

class AuditoriaLogic:
    """Clase para manejar la lógica de negocio de auditoría"""
    
    def __init__(self):
        """Inicializar la lógica de auditoría"""
        pass
    
    def registrar_accion(self, conn, usuario_id, tipo_accion, tabla, registro_id, detalles, resultado="SUCCESS"):
        """
        Registra una acción en la auditoría
        
        Args:
            conn: Conexión a la base de datos
            usuario_id (int): ID del usuario que realiza la acción
            tipo_accion (str): Tipo de acción (INSERT, UPDATE, DELETE, etc.)
            tabla (str): Nombre de la tabla afectada
            registro_id (int): ID del registro afectado
            detalles (str): Descripción de la acción
            resultado (str): Resultado de la acción
        
        Returns:
            bool: True si se registró correctamente
        """
        return registrar_accion_auditoria(conn, usuario_id, tipo_accion, tabla, registro_id, detalles, resultado)
    
    def obtener_auditoria(self):
        """
        Obtiene todos los registros de auditoría
        
        Returns:
            list: Lista de registros de auditoría
        """
        return get_auditoria_db()
    
    def obtener_auditoria_por_fecha(self, fecha_inicio, fecha_fin):
        """
        Obtiene registros de auditoría por rango de fechas
        
        Args:
            fecha_inicio (str): Fecha de inicio en formato YYYY-MM-DD
            fecha_fin (str): Fecha de fin en formato YYYY-MM-DD
        
        Returns:
            list: Lista de registros filtrados por fecha
        """
        return get_auditoria_por_fecha_db(fecha_inicio, fecha_fin)
    
    def obtener_auditoria_por_usuario(self, usuario_id):
        """
        Obtiene registros de auditoría por usuario
        
        Args:
            usuario_id (int): ID del usuario
        
        Returns:
            list: Lista de registros del usuario
        """
        return get_auditoria_por_usuario_db(usuario_id)
    
    def obtener_auditoria_por_tabla(self, tabla):
        """
        Obtiene registros de auditoría por tabla
        
        Args:
            tabla (str): Nombre de la tabla
        
        Returns:
            list: Lista de registros de la tabla
        """
        return get_auditoria_por_tabla_db(tabla)
    
    def obtener_auditoria_por_tipo_accion(self, tipo_accion):
        """
        Obtiene registros de auditoría por tipo de acción
        
        Args:
            tipo_accion (str): Tipo de acción (INSERT, UPDATE, DELETE, etc.)
        
        Returns:
            list: Lista de registros del tipo de acción
        """
        return get_auditoria_por_tipo_accion_db(tipo_accion)
    
    def obtener_estadisticas(self):
        """
        Obtiene estadísticas de auditoría
        
        Returns:
            dict: Diccionario con estadísticas
        """
        return get_estadisticas_auditoria_db()
    
    def obtener_tablas_disponibles(self):
        """
        Obtiene las tablas disponibles en auditoría
        
        Returns:
            list: Lista de nombres de tablas únicas
        """
        registros = self.obtener_auditoria()
        tablas = set()
        for registro in registros:
            if registro.get('tabla'):
                tablas.add(registro['tabla'])
        return sorted(list(tablas))
    
    def obtener_tipos_accion_disponibles(self):
        """
        Obtiene los tipos de acción disponibles en auditoría
        
        Returns:
            list: Lista de tipos de acción únicos
        """
        registros = self.obtener_auditoria()
        acciones = set()
        for registro in registros:
            if registro.get('tipo_accion'):
                acciones.add(registro['tipo_accion'])
        return sorted(list(acciones))
    
    def obtener_usuarios_disponibles(self):
        """
        Obtiene los usuarios disponibles en auditoría
        
        Returns:
            list: Lista de usuarios únicos
        """
        registros = self.obtener_auditoria()
        usuarios = set()
        for registro in registros:
            if registro.get('usuario_nombre'):
                usuarios.add(registro['usuario_nombre'])
        return sorted(list(usuarios)) 