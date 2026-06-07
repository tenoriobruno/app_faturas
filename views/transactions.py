import streamlit as st
import pandas as pd
from data.repository import cache_repo
from utils.normalize import normalize
from config.settings import settings

def render_transactions(df: pd.DataFrame, load_all_data_func):
    st.subheader("📋 Ver Dados Brutos")

    quick_cat = st.session_state.get('quick_filter_category')
    if quick_cat:
        col_info, col_clear = st.columns([0.85, 0.15])
        with col_info:
            st.info(f"🔍 Filtrado rapidamente pela categoria **{quick_cat}** (clique vindo da Visão Geral).")
        with col_clear:
            if st.button("✖️ Limpar filtro", key="clear_quick_filter"):
                del st.session_state['quick_filter_category']
                st.rerun()
        df = df[df['categoria'] == quick_cat]

    # Busca/filtros unificados na barra lateral (evita dois campos fazendo a mesma coisa)
    df_display = df
    st.caption(f"📋 {len(df_display)} transações · Use os filtros na barra lateral para refinar (texto, categoria, valor, data, tipo).")

    edited_df = st.data_editor(
        df_display,
        column_config={
            "categoria": st.column_config.SelectboxColumn(
                "Categoria",
                help="Selecione a categoria",
                width="medium",
                options=settings.get_category_names()
            )
        },
        disabled=["date", "title", "amount", "tipo_transacao", "parcela_atual", "total_parcelas"],
        hide_index=True,
        use_container_width=True
    )

    if not df_display.equals(edited_df):
        from services.classification import save_manual_corrections
        diff = edited_df[df_display['categoria'] != edited_df['categoria']]
        save_manual_corrections(diff, df_display)
        st.success("✅ Classificações manuais salvas com sucesso!")
        load_all_data_func.clear()
        st.rerun()
