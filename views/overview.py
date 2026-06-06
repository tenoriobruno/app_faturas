import streamlit as st
import pandas as pd
from components.charts import render_donut, render_bar_history
from components.budget import render_budget
from components.metrics import metric_card

def render_overview(df: pd.DataFrame, df_consolidated: pd.DataFrame, csv_files: list, selected_file, all_data: dict):
    # Layout de duas colunas: Esquerda (Gráfico de Composição), Direita (Métricas)
    col_left, col_right = st.columns([0.6, 0.4], gap="large")

    with col_right:
        st.markdown(
            '<div style="margin-bottom:12px;">'
            '<span style="font-weight:700;font-size:1.05rem;">📊 Resumo do Período</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Busca o CSV anterior cronologicamente para calcular o Delta
        prev_df = None
        try:
            idx = csv_files.index(selected_file)
            if idx + 1 < len(csv_files):
                prev_file = csv_files[idx + 1]
                prev_df = all_data[prev_file.name]
        except ValueError:
            pass

        df_gastos = df[df['tipo_transacao'] == 'gasto']
        total_tx = len(df_gastos)
        valor_total = df_gastos['amount'].sum() if total_tx > 0 else 0
        ticket_medio = df_gastos['amount'].mean() if total_tx > 0 else 0
        top_cat = df_gastos.groupby('categoria')['amount'].sum().idxmax() if total_tx > 0 else "N/A"

        delta_tx, delta_valor, delta_ticket = None, None, None
        if prev_df is not None:
            prev_gastos = prev_df[prev_df['tipo_transacao'] == 'gasto']
            prev_tx = len(prev_gastos)
            prev_valor = prev_gastos['amount'].sum() if prev_tx > 0 else 0
            prev_ticket = prev_gastos['amount'].mean() if prev_tx > 0 else 0

            delta_tx = total_tx - prev_tx
            delta_valor = valor_total - prev_valor
            delta_ticket = ticket_medio - prev_ticket

        # Renderiza métricas usando o novo componente de métricas customizadas estilizadas
        metric_card("Transações (Gastos)", f"{total_tx}", delta=f"{delta_tx:+d}" if delta_tx is not None else None, delta_color="normal")
        metric_card("Valor Total", f"R$ {valor_total:,.2f}", delta=f"R$ {delta_valor:+,.2f}" if delta_valor is not None else None, delta_color="inverse")
        metric_card("Ticket Médio", f"R$ {ticket_medio:,.2f}", delta=f"R$ {delta_ticket:+,.2f}" if delta_ticket is not None else None, delta_color="inverse")
        metric_card("Maior Categoria", top_cat)

        outros_pct = (df['categoria'] == 'Outros').sum() / len(df) * 100 if len(df) > 0 else 0
        metric_card("% Não-classificado", f"{outros_pct:.1f}%")

    with col_left:
        st.markdown(
            '<div style="margin-bottom:12px;">'
            '<span style="font-weight:700;font-size:1.05rem;">💸 Gastos por Categoria</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        # O gráfico de donut já renderiza dentro de st.plotly_chart com bordas/sombras
        render_donut(df_gastos)

    st.divider()
    render_budget(df)
    st.divider()
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight:700;font-size:1.05rem;margin-bottom:16px;">📈 Histórico Mensal de Gastos</div>', unsafe_allow_html=True)
    render_bar_history(df_consolidated)
    st.markdown('</div>', unsafe_allow_html=True)

