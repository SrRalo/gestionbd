import streamlit as st
import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from vistas.login_view import LoginView
from vistas.dashboard_view import DashboardView
from vistas.reservas_view import ReservasView
from vistas.pagos_view import PagosView
from vistas.validacion_view import mostrar_vista_validacion
from logica_negocio.auth_manager import AuthManager
from capa_datos.database_connection import get_db_connection

# Configuración de la página
st.set_page_config(
    page_title="Reservas de Canchas Deportivas",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .role-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Función principal de la aplicación"""
    
    # Inicializar session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    # Inicializar variables para edición
    if 'show_edit_cancha_form' not in st.session_state:
        st.session_state.show_edit_cancha_form = False
    if 'show_edit_tipo_form' not in st.session_state:
        st.session_state.show_edit_tipo_form = False
    if 'editing_cancha' not in st.session_state:
        st.session_state.editing_cancha = None
    if 'editing_tipo' not in st.session_state:
        st.session_state.editing_tipo = None
    
    # Inicializar variable de navegación
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Header principal
    st.markdown('<h1 class="main-header">🏟️ Reservas de Canchas Deportivas</h1>', unsafe_allow_html=True)
    
    # Verificar autenticación
    if not st.session_state.authenticated:
        show_login()
    else:
        show_authenticated_content()

def show_login():
    """Mostrar la vista de login"""
    login_view = LoginView()
    login_view.show()
    
    # Verificar si el login fue exitoso
    if st.session_state.authenticated:
        st.success("¡Inicio de sesión exitoso!")
        st.rerun()

def show_authenticated_content():
    """Muestra el contenido para usuarios autenticados"""
    
    # Sidebar con navegación
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">📋 Menú Principal</h2>', unsafe_allow_html=True)
        
        # Mostrar información del usuario
        if st.session_state.current_user:
            username = st.session_state.current_user.get("username", "Usuario")
            st.markdown(f'<div class="role-badge">👤 {username}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="role-badge">🔑 {st.session_state.user_role}</div>', unsafe_allow_html=True)
        
        # Opciones de navegación
        page = st.selectbox(
            "Seleccione una opción:",
            ["🏠 Dashboard", "📅 Reservas", "💰 Pagos", "📊 Reportes", "🔧 Validación", "🚪 Cerrar Sesión"],
            index=0
        )
        
        # Botón de cerrar sesión
        if st.button("🚪 Cerrar Sesión", key="sidebar_logout_btn"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.session_state.is_admin = False
            st.rerun()
    
    # Mostrar página seleccionada
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "📅 Reservas":
        show_reservas()
    elif page == "💰 Pagos":
        show_pagos()
    elif page == "📊 Reportes":
        show_reportes()
    elif page == "🔧 Validación":
        show_validacion()
    elif page == "🚪 Cerrar Sesión":
        st.session_state.authenticated = False
        st.session_state.current_user = None
        st.session_state.user_role = None
        st.session_state.is_admin = False
        st.rerun()

def show_dashboard():
    """Mostrar el dashboard usando la vista correspondiente"""
    dashboard_view = DashboardView()
    dashboard_view.show()

def show_reservas():
    """Mostrar la vista de reservas"""
    reservas_view = ReservasView()
    reservas_view.show()

def show_pagos():
    """Mostrar la vista de pagos"""
    pagos_view = PagosView()
    pagos_view.show()

def show_reportes():
    """Mostrar la vista de reportes"""
    st.markdown("## 📊 Reportes y Auditoría")
    
    # Pestañas para diferentes tipos de reportes
    tab1, tab2 = st.tabs(["📋 Auditoría del Sistema", "📈 Reportes Generales"])
    
    with tab1:
        # Importar y mostrar la vista de auditoría
        from vistas.auditoria_view import AuditoriaView
        auditoria_view = AuditoriaView()
        auditoria_view.show()
    
    with tab2:
        # Importar y mostrar la vista de reportes generales
        from vistas.reportes_generales_view import ReportesGeneralesView
        reportes_view = ReportesGeneralesView()
        reportes_view.show()

def show_validacion():
    """Muestra la vista de validación y limpieza de datos"""
    mostrar_vista_validacion()

if __name__ == "__main__":
    main() 