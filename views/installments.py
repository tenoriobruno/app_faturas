import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from config.theme import PLOT_LAYOUT
from core.installments import calculate_future_installments

def render_installments(df_consolidated: pd.DataFrame):
    st.subheader("🗓️ Dívidas Ativas e Faturas Futuras")
    
    if df_consolidated.empty:
        st.info("Nenhum dado disponível para análise de parcelas.")
        return

    # Garante que a data está em formato datetime para comparação
    df_temp = df_consolidated.copy()
    df_temp['date'] = pd.to_datetime(df_temp['date'])
    last_data_date = df_temp['date'].max()
    
    parceladas = calculate_future_installments(df_consolidated)
    
    if parceladas.empty:
        st.info("Nenhuma parcela futura detectada.")
        return
        
    # Primeiro passamos para calcular o saldo devedor e coletar dados do gráfico
    total_remaining_debt = 0
    future_data = []
    
    for _, row in parceladas.iterrows():
        faltam = row['total_parcelas'] - row['parcela_atual']
        if faltam > 0:
            for i in range(1, int(faltam) + 1):
                # Calcula a data estimada da próxima parcela
                future_month_date = pd.to_datetime(row['date']) + pd.DateOffset(months=i)
                
                # Só projeta se o mês for posterior à última data de transação conhecida (fatura corrente)
                if future_month_date > last_data_date:
                    total_remaining_debt += row['amount']
                    future_data.append({
                        'title': row['title'],
                        'amount': row['amount'],
                        'future_month': future_month_date.to_period('M')
                    })
    
    # Exibe métrica de resumo
    st.metric("Saldo Devedor Estimado (Futuro)", f"R$ {total_remaining_debt:,.2f}", help="Soma de todas as parcelas que ainda vencerão após a data da última fatura carregada.")
    st.divider()

    # Exibe lista de dívidas ativas
    st.write("**Detalhamento por Item:**")
    for _, row in parceladas.iterrows():
        faltam = row['total_parcelas'] - row['parcela_atual']
        if faltam > 0:
            pagas = row['parcela_atual']
            total = row['total_parcelas']
            pct = float(pagas) / float(total)
            st.write(f"**{row['title']}** (R$ {row['amount']:.2f}/mês) - {pagas}/{total} pagas")
            st.progress(pct)
            
    if future_data:
        st.write("---")
        st.write("**Projeção de Impacto nas Próximas Faturas:**")
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
