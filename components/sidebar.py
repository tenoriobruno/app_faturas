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
        val_range = st.sidebar.slider(
            "Faixa de Valor (R$)",
            min_value=min_val,
            max_value=max_val,
            value=(min_val, max_val)
        ) if min_val < max_val else (min_val, max_val)
    else:
        val_range = (0.0, 0.0)
        
    # Date Range
    if len(df) > 0:
        min_d = df['date'].min().date()
        max_d = df['date'].max().date()
        date_range = st.sidebar.date_input("Período", (min_d, max_d), min_value=min_d, max_value=max_d)
    else:
        date_range = ()
        
    # Tipos
    tipos = st.sidebar.multiselect("Tipo", ["gasto", "estorno", "ajuste"], default=["gasto", "estorno"])
    
    col1, col2 = st.sidebar.columns(2)
    hide_outros = col1.checkbox("Ocultar Outros")
    only_outros = col2.checkbox("Só Outros")

    from utils.filters import apply_filters
    return apply_filters(df, search_text, selected_cats, val_range, date_range, tipos, hide_outros, only_outros)
