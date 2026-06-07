import streamlit as st
import pandas as pd
from typing import List

_FILTER_KEYS = [
    "filter_search", "filter_categories", "filter_val_range",
    "filter_date_range", "filter_tipos", "filter_hide_outros", "filter_only_outros",
]


def render_sidebar(df: pd.DataFrame, categories: List[str]) -> pd.DataFrame:
    """Renderiza os filtros na sidebar (agrupados) e retorna o DataFrame filtrado."""
    st.sidebar.markdown(
        '<div style="margin-bottom:8px;padding:0 4px;">'
        '<span style="font-weight:700;font-size:1rem;letter-spacing:0.03em;color:var(--text-secondary);'
        'text-transform:uppercase;">Filtros</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    min_val = float(df['amount'].min()) if len(df) > 0 else 0.0
    max_val = float(df['amount'].max()) if len(df) > 0 else 0.0
    min_d = df['date'].min().date() if len(df) > 0 else None
    max_d = df['date'].max().date() if len(df) > 0 else None
    default_tipos = ["gasto", "estorno"]

    # --- Grupo: Busca rápida ---
    with st.sidebar.expander("🔎 Busca rápida", expanded=True):
        search_text = st.text_input("Buscar transação", "", key="filter_search")
        selected_cats = st.multiselect("Categorias", options=categories, default=[], key="filter_categories")

    # --- Grupo: Filtros avançados ---
    with st.sidebar.expander("⚙️ Filtros avançados", expanded=False):
        if len(df) > 0 and min_val < max_val:
            val_range = st.slider(
                "Faixa de Valor (R$)",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                key="filter_val_range",
            )
        else:
            val_range = (min_val, max_val)

        if len(df) > 0:
            date_range = st.date_input("Período", (min_d, max_d), min_value=min_d, max_value=max_d, key="filter_date_range")
        else:
            date_range = ()

        tipos = st.multiselect("Tipo", ["gasto", "estorno", "ajuste"], default=default_tipos, key="filter_tipos")

        col1, col2 = st.columns(2)
        hide_outros = col1.checkbox("Ocultar Outros", key="filter_hide_outros")
        only_outros = col2.checkbox("Só Outros", key="filter_only_outros")

    # --- Contador de filtros ativos + botão de limpar ---
    active = 0
    if search_text:
        active += 1
    if selected_cats:
        active += 1
    if len(df) > 0 and min_val < max_val and val_range != (min_val, max_val):
        active += 1
    if len(df) > 0 and date_range and tuple(date_range) != (min_d, max_d):
        active += 1
    if tipos != default_tipos:
        active += 1
    if hide_outros:
        active += 1
    if only_outros:
        active += 1

    col_badge, col_clear = st.sidebar.columns([0.6, 0.4])
    with col_badge:
        if active > 0:
            st.caption(f"🔘 {active} filtro(s) ativo(s)")
        else:
            st.caption("Nenhum filtro ativo")
    with col_clear:
        if st.button("✖️ Limpar tudo", key="clear_all_filters", disabled=(active == 0)):
            for k in _FILTER_KEYS:
                st.session_state.pop(k, None)
            st.rerun()

    from utils.filters import apply_filters
    return apply_filters(df, search_text, selected_cats, val_range, date_range, tipos, hide_outros, only_outros)
