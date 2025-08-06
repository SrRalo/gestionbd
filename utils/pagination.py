"""
Módulo de utilidad para paginación en Streamlit
"""
import streamlit as st
import pandas as pd

def paginate_dataframe(df, page_key, registros_por_pagina=5):
    """
    Implementa paginación para un DataFrame de Streamlit.
    
    Args:
        df (pd.DataFrame): DataFrame a paginar
        page_key (str): Clave única para el estado de la página
        registros_por_pagina (int): Número de registros por página (default: 5)
    
    Returns:
        pd.DataFrame: DataFrame con los registros de la página actual
    """
    if df.empty:
        return df
    
    total_registros = len(df)
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
    
    # Controles de paginación
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Anterior", disabled=st.session_state.get(page_key, 1) <= 1):
            st.session_state[page_key] = max(1, st.session_state.get(page_key, 1) - 1)
            st.rerun()
    
    with col2:
        pagina_actual = st.session_state.get(page_key, 1)
        st.markdown(f"**Página {pagina_actual} de {total_paginas}**")
    
    with col3:
        if st.button("➡️ Siguiente", disabled=pagina_actual >= total_paginas):
            st.session_state[page_key] = min(total_paginas, pagina_actual + 1)
            st.rerun()
    
    # Calcular índices para la página actual
    inicio = (pagina_actual - 1) * registros_por_pagina
    fin = min(inicio + registros_por_pagina, total_registros)
    
    # Retornar registros de la página actual
    df_pagina = df.iloc[inicio:fin]
    
    # Mostrar información de paginación
    st.info(f"📊 Mostrando registros {inicio + 1}-{fin} de {total_registros} registros ({registros_por_pagina} por página)")
    
    return df_pagina

def reset_pagination(page_key):
    """
    Reinicia la paginación para una clave específica.
    
    Args:
        page_key (str): Clave de la página a reiniciar
    """
    if page_key in st.session_state:
        del st.session_state[page_key]

def get_pagination_info(df, page_key, registros_por_pagina=5):
    """
    Obtiene información de paginación sin mostrar controles.
    
    Args:
        df (pd.DataFrame): DataFrame a analizar
        page_key (str): Clave única para el estado de la página
        registros_por_pagina (int): Número de registros por página
    
    Returns:
        dict: Información de paginación
    """
    if df.empty:
        return {
            'total_registros': 0,
            'total_paginas': 0,
            'pagina_actual': 1,
            'inicio': 0,
            'fin': 0
        }
    
    total_registros = len(df)
    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
    pagina_actual = st.session_state.get(page_key, 1)
    inicio = (pagina_actual - 1) * registros_por_pagina
    fin = min(inicio + registros_por_pagina, total_registros)
    
    return {
        'total_registros': total_registros,
        'total_paginas': total_paginas,
        'pagina_actual': pagina_actual,
        'inicio': inicio,
        'fin': fin
    } 