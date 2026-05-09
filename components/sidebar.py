import streamlit as st
import pandas as pd
from typing import List

def render_sidebar(df: pd.DataFrame, categories: List[str]) -> pd.DataFrame:
    """Renderiza os filtros na sidebar e retorna o DataFrame filtrado."""
    st.sidebar.header("🔍 Filtros")
    
    # Busca textual
    search_text = st.sidebar.text_input("Buscar transação", "")
    
    # Filtro de Categoria
    selected_cats = st.sidebar.multiselect(
        "Categorias",
        options=categories,
        default=[]
    )
    
    # Filtro de Valor
    if len(df) > 0:
        min_val = float(df['amount'].min())
        max_val = float(df['amount'].max())
        
        if min_val < max_val:
            val_range = st.sidebar.slider(
                "Faixa de Valor (R$)",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val)
            )
        else:
            val_range = (min_val, max_val)
    else:
        val_range = (0.0, 0.0)

    # Aplicação dos filtros
    df_filtered = df.copy()
    
    if search_text:
        # Busca no titulo
        mask = df_filtered['title'].str.contains(search_text, case=False, na=False)
        df_filtered = df_filtered[mask]
        
    if selected_cats:
        df_filtered = df_filtered[df_filtered['categoria'].isin(selected_cats)]
        
    if len(df_filtered) > 0:
        df_filtered = df_filtered[
            (df_filtered['amount'] >= val_range[0]) & 
            (df_filtered['amount'] <= val_range[1])
        ]
    
    return df_filtered
