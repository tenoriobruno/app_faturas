import streamlit as st
import pandas as pd
from core.recurrences import detect_recurrences
from data.repository import IgnoredRecurrencesRepository

def render_recurrences(df_consolidated: pd.DataFrame):
    st.subheader("🔁 Despesas Fixas e Assinaturas")

    fixed_costs = detect_recurrences(df_consolidated)

    if fixed_costs.empty:
        st.info("Nenhuma despesa fixa ou assinatura detectada.")
        return

    # Prepare and display data
    total_fixed = fixed_costs['avg_amount'].sum()
    st.metric("Estimativa de Custo Fixo Mensal", f"R$ {total_fixed:,.2f}")

    fixed_costs_renamed = fixed_costs[['title', 'categoria', 'avg_amount', 'months_count']].rename(
        columns={
            'title': 'Serviço/Conta',
            'categoria': 'Categoria',
            'avg_amount': 'Valor Médio (R$)',
            'months_count': 'Meses Ativos'
        }
    )
    fixed_costs_renamed['Valor Médio (R$)'] = fixed_costs_renamed['Valor Médio (R$)'].apply(lambda x: f"R$ {x:,.2f}")

    # Display each row with "Ignorar" button
    ignored_repo = IgnoredRecurrencesRepository()
    for idx, row in fixed_costs_renamed.iterrows():
        cols = st.columns([3, 2, 2, 2, 1])
        cols[0].write(row['Serviço/Conta'])
        cols[1].write(row['Categoria'])
        cols[2].write(row['Valor Médio (R$)'])
        cols[3].write(row['Meses Ativos'])
        if cols[4].button("Ignorar", key=f"ignore_{idx}_{row['Serviço/Conta']}"):
            ignored_repo.add_recurrence(row['Serviço/Conta'])
            st.success(f"'{row['Serviço/Conta']}' foi adicionada à lista de recorrências ignoradas.")
            st.cache_data.clear()
            st.rerun()
