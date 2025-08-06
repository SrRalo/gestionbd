import streamlit as st
import hashlib
from logica_negocio.auth_manager import AuthManager

class LoginView:
    def __init__(self):
        self.auth_manager = AuthManager()
    
    def show(self):
        """Mostrar la vista de login"""
        st.markdown('<h2>🔐 Iniciar Sesión</h2>', unsafe_allow_html=True)
        
        # Centrar el formulario
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.form("login_form"):
                st.markdown("---")
                
                # Campos del formulario
                username = st.text_input("👤 Usuario:", placeholder="Ingresa tu usuario")
                password = st.text_input("🔒 Contraseña:", type="password", placeholder="Ingresa tu contraseña")
                
                # Botón de envío
                submitted = st.form_submit_button("🚀 Iniciar Sesión", type="primary", use_container_width=True)
                
                if submitted:
                    self.handle_login(username, password)
                
                st.markdown("---")
                
    
    def handle_login(self, username, password):
        """Manejar el proceso de login"""
        if not username or not password:
            st.error("❌ Por favor completa todos los campos")
            return
        
        try:
            # Intentar autenticar usando el método correcto
            result = self.auth_manager.autenticar_usuario(username, password)
            
            if result and result.get('success'):
                # Login exitoso - guardar información completa del usuario
                st.session_state.authenticated = True
                st.session_state.current_user = {
                    'username': username,
                    'rol_principal': result['rol_principal'],
                    'roles': result['roles'],
                    'info_usuario': result['info_usuario']
                }
                st.session_state.user_role = result['rol_principal']
                st.session_state.user_info = result['info_usuario']
                st.session_state.db_connection = result['connection']
                
                # Establecer permisos de administrador
                st.session_state.is_admin = result['rol_principal'] == 'admin_reservas'
                
                st.success("✅ ¡Inicio de sesión exitoso!")
                st.rerun()
                
            else:
                # Login fallido
                st.error("❌ Credenciales incorrectas o error de conexión")
                
        except Exception as e:
            st.error(f"❌ Error durante el inicio de sesión: {str(e)}") 