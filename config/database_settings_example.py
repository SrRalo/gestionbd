# =====================================================
# CONFIGURACIÓN DE BASE DE DATOS - ARCHIVO DE EJEMPLO
# =====================================================
# Copia este archivo como 'database_settings.py' y configura tus credenciales

# Tipo de conexión: 'local' o 'remote'
CONNECTION_TYPE = 'local'

# Configuración para conexión LOCAL
LOCAL_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'sportcourt_reservations',
    'user': 'tu_usuario',
    'password': 'tu_password'  
}

# Configuración para conexión REMOTA 
REMOTE_CONFIG = {
    'host': 'tu_host_remoto',
    'port': 'tu_puerto',
    'database': 'tu_base_datos',
    'user': 'tu_usuario',
    'password': 'tu_password'
}

def get_database_config():
    """
    Obtiene la configuración de la base de datos según el tipo de conexión.
    
    Returns:
        dict: Configuración de la base de datos
    """
    if CONNECTION_TYPE == 'local':
        return LOCAL_CONFIG
    elif CONNECTION_TYPE == 'remote':
        return REMOTE_CONFIG
    else:
        raise ValueError(f"Tipo de conexión no válido: {CONNECTION_TYPE}")

def get_connection_info():
    """
    Obtiene información de la conexión actual.
    
    Returns:
        str: Información de la conexión
    """
    config = get_database_config()
    return f"{CONNECTION_TYPE.upper()}: {config['host']}:{config['port']}/{config['database']}" 