import streamlit as st
import pandas as pd
from data.repository import cache_repo
from utils.normalize import normalize
from config.settings import settings

def render_transactions(df: pd.DataFrame, load_all_data_func):
    st.subheader("📋 Ver Dados Brutos")
    # Campo de busca para filtrar por categoria ou descrição
    search_query = st.text_input("🔍 Filtrar tabela (por descrição ou categoria):", "", key="table_search_query")
    
    if search_query:
        mask = (
            df['title'].str.contains(search_query, case=False, na=False) |
            df['categoria'].str.contains(search_query, case=False, na=False)
        )
        df_display = df[mask]
    else:
        df_display = df

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
        cache = cache_repo.load()
        diff = edited_df[df_display['categoria'] != edited_df['categoria']]
        for _, row in diff.iterrows():
            norm_title = normalize(row['title'])
            if norm_title:
                cache[norm_title] = {"categoria": row['categoria'], "source": "user"}
        cache_repo.save(cache)
        st.success("✅ Classificações manuais salvas com sucesso!")
        load_all_data_func.clear()
        st.rerun()
