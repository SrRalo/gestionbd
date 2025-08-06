# 🏟️ SportCourt Reservations

Sistema de gestión de reservas para canchas deportivas.

## 📋 Estado Actual

La aplicación ha sido simplificada y contiene únicamente:

- ✅ **Interfaz de Login**: Autenticación de usuarios
- ✅ **Dashboard Básico**: Vista principal con métricas básicas
- ✅ **Sistema de Autenticación**: Gestión de sesiones y roles
- ✅ **Conexión a Base de Datos**: PostgreSQL con psycopg2

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- PostgreSQL
- pip

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/SrRalo/gestionbd.git
   cd gestionbd
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar la base de datos**
   - Copia el archivo de ejemplo: `cp config/database_settings_example.py config/database_settings.py`
   - Edita `config/database_settings.py` con tus credenciales de base de datos
   - Configura `CONNECTION_TYPE` como 'local' o 'remote' según tu entorno

4. **Ejecutar la aplicación**
   ```bash
   streamlit run app.py
   ```

## 🔐 Autenticación

La aplicación utiliza autenticación basada en roles de PostgreSQL:

- **admin_reservas**: Administrador del sistema
- **operador_reservas**: Operador de reservas
- **consultor_reservas**: Usuario consultor

## 📁 Estructura del Proyecto

```
gestionbdfinal/
├── app.py                 # Aplicación principal
├── vistas/
│   ├── login_view.py      # Vista de login
│   └── dashboard_view.py  # Vista del dashboard
├── logica_negocio/
│   ├── auth_manager.py    # Gestión de autenticación
│   └── canchas_logic.py   # Lógica de canchas
├── capa_datos/
│   ├── database_connection.py
│   ├── data_access.py
│   ├── canchas_data.py
│   └── usuarios_data.py
└── README.md
```

## 🔄 Próximos Pasos

La aplicación está lista para ser expandida incrementalmente:

1. **Gestión de Usuarios**
2. **Gestión de Canchas**
3. **Sistema de Reservas**
4. **Gestión de Pagos**
5. **Reportes y Estadísticas**

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python
- **Base de Datos**: PostgreSQL
- **ORM**: psycopg2

## 📞 Soporte

Para soporte técnico, contacta al administrador del sistema. 