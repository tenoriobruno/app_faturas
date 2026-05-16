import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.theme import PLOT_LAYOUT
from core.installments import calculate_future_installments

def render_installments(df_consolidated: pd.DataFrame):
    st.subheader("🗓️ Dívidas Ativas e Faturas Futuras")
    
    parceladas = calculate_future_installments(df_consolidated)
    
    if parceladas.empty:
        st.info("Nenhuma parcela futura detectada.")
        return
        
    for _, row in parceladas.iterrows():
        faltam = row['total_parcelas'] - row['parcela_atual']
        if faltam > 0:
            pagas = row['parcela_atual']
            total = row['total_parcelas']
            pct = float(pagas) / float(total)
            st.write(f"**{row['title']}** (R$ {row['amount']:.2f}/mês) - {pagas}/{total} pagas")
            st.progress(pct)
            
    future_data = []
    for _, row in parceladas.iterrows():
        faltam = row['total_parcelas'] - row['parcela_atual']
        if faltam > 0:
            for i in range(1, int(faltam) + 1):
                future_month = row['date'] + pd.DateOffset(months=i)
                future_data.append({
                    'title': row['title'],
                    'amount': row['amount'],
                    'future_month': future_month.to_period('M')
                })
                
    if future_data:
        future_df = pd.DataFrame(future_data)
        monthly_debt = future_df.groupby('future_month')['amount'].sum().reset_index()
        monthly_debt['future_month_str'] = monthly_debt['future_month'].dt.strftime('%b/%Y')
        
        fig = go.Figure(data=[go.Bar(
            x=monthly_debt['future_month_str'],
            y=monthly_debt['amount'],
            marker_color='#EF4444',
            text=monthly_debt['amount'].apply(lambda x: f"R$ {x:,.2f}"),
            textposition='auto'
        )])
        
        fig.update_layout(
            **PLOT_LAYOUT,
            xaxis_title='',
            yaxis_title='R$',
            height=300,
            margin=dict(t=20, b=40, l=40, r=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
