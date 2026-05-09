import pandas as pd
import streamlit as st

def detect_recurrences(df_consolidated: pd.DataFrame):
    """
    Detecta assinaturas baseadas em transações com mesmo título ou categoria 'Assinaturas'
    que aparecem em 3 ou mais meses distintos.
    """
    if df_consolidated.empty:
        return pd.DataFrame()
        
    df = df_consolidated.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.to_period('M')
    
    recurrences = df.groupby('title').agg(
        months_count=('month_year', 'nunique'),
        avg_amount=('amount', 'mean'),
        last_date=('date', 'max'),
        categoria=('categoria', 'first')
    ).reset_index()
    
    # Considera recorrente se aparece em >= 3 meses distintos ou se a categoria for 'Assinaturas'
    mask = (recurrences['months_count'] >= 3) | (recurrences['categoria'] == 'Assinaturas')
    fixed_costs = recurrences[mask].sort_values(by='avg_amount', ascending=False)
    
    return fixed_costs

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
