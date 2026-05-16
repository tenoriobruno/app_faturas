import streamlit as st
import pandas as pd
from core.recurrences import detect_recurrences

def render_recurrences(df_consolidated: pd.DataFrame):
    st.subheader("🔁 Despesas Fixas e Assinaturas")
    
    fixed_costs = detect_recurrences(df_consolidated)
    
    if fixed_costs.empty:
        st.info("Nenhuma despesa fixa ou assinatura detectada.")
        return
        
    total_fixed = fixed_costs['avg_amount'].sum()
    st.metric("Estimativa de Custo Fixo Mensal", f"R$ {total_fixed:,.2f}")
    
    st.dataframe(
        fixed_costs[['title', 'categoria', 'avg_amount', 'months_count']].rename(
            columns={
                'title': 'Serviço/Conta',
                'categoria': 'Categoria',
                'avg_amount': 'Valor Médio (R$)',
                'months_count': 'Meses Ativos'
            }
        ),
        use_container_width=True,
        hide_index=True
    )
