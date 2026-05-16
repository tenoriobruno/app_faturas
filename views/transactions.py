import streamlit as st
import pandas as pd

def render_transactions(df: pd.DataFrame, load_all_data_func):
    st.subheader("📋 Ver Dados Brutos")
    edited_df = st.data_editor(
        df,
        column_config={
            "categoria": st.column_config.SelectboxColumn(
                "Categoria",
                help="Selecione a categoria",
                width="medium",
                options=[
                    'Delivery', 'Alimentação', 'Transporte', 'Compras',
                    'Saúde', 'Assinaturas', 'Moradia', 'Lazer',
                    'Educação', 'Viagem', 'Restaurante', 'Supermercado',
                    'Serviço', 'Feira', 'Gasolina', 'Outros'
                ]
            )
        },
        disabled=["date", "title", "amount", "tipo_transacao", "parcela_atual", "total_parcelas"],
        hide_index=True,
        use_container_width=True
    )

    if not df.equals(edited_df):
        from data.repository import cache_repo
        from utils.normalize import normalize
        cache = cache_repo.load()
        diff = edited_df[df['categoria'] != edited_df['categoria']]
        for _, row in diff.iterrows():
            norm_title = normalize(row['title'])
            if norm_title:
                cache[norm_title] = {"categoria": row['categoria'], "source": "user"}
        cache_repo.save(cache)
        st.success("✅ Classificações manuais salvas com sucesso!")
        load_all_data_func.clear()
        st.rerun()
