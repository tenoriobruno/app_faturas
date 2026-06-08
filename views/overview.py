import streamlit as st
import pandas as pd
from components.charts import render_donut, render_bar_history
from components.budget import render_budget
from components.metrics import metric_card
from core.anomalies import detect_anomalies


def render_overview(df: pd.DataFrame, df_consolidated: pd.DataFrame, csv_files: list, selected_file, all_data: dict):
    col_left, col_right = st.columns([0.6, 0.4], gap="large")

    with col_right:
        st.markdown(
            '<div style="margin-bottom:12px;">'
            '<span style="font-weight:700;font-size:1.05rem;">📊 Resumo do Período</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        prev_df = None
        try:
            idx = csv_files.index(selected_file)
            if idx + 1 < len(csv_files):
                prev_file = csv_files[idx + 1]
                prev_df = all_data[prev_file.name]
        except ValueError:
            pass

        from core.metrics import calculate_overview_metrics
        metrics = calculate_overview_metrics(df, prev_df)

        metric_card("Transações (Gastos)", f"{metrics['total_tx']}", delta=f"{metrics['delta_tx']:+d}" if metrics['delta_tx'] is not None else None, delta_color="normal")
        metric_card("Valor Total", f"R$ {metrics['valor_total']:,.2f}", delta=f"R$ {metrics['delta_valor']:+,.2f}" if metrics['delta_valor'] is not None else None, delta_color="inverse")
        metric_card("Ticket Médio", f"R$ {metrics['ticket_medio']:,.2f}", delta=f"R$ {metrics['delta_ticket']:+,.2f}" if metrics['delta_ticket'] is not None else None, delta_color="inverse")
        metric_card("Maior Categoria", metrics['top_cat'])
        if metrics['top_cat'] != "N/A":
            if st.button(f"🔍 Ver transações de {metrics['top_cat']}", key="quick_filter_top_cat"):
                st.session_state['quick_filter_category'] = metrics['top_cat']
                st.toast(f"Filtro aplicado! Abra a aba 'Transações' para ver os resultados.", icon="🔍")
                st.rerun()

        metric_card("% Não-classificado", f"{metrics['outros_pct']:.1f}%")

    with col_left:
        df_gastos = df[df['tipo_transacao'] == 'gasto']
        st.markdown(
            '<div style="margin-bottom:12px;">'
            '<span style="font-weight:700;font-size:1.05rem;">💸 Gastos por Categoria</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        render_donut(df_gastos)

    st.divider()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight:700;font-size:1.05rem;margin-bottom:16px;">📈 Histórico Mensal de Gastos</div>', unsafe_allow_html=True)
    render_bar_history(df_consolidated)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    anomalies = detect_anomalies(df, df_consolidated)
    if anomalies:
        with st.expander(f"⚠️ Alertas de Anomalias ({len(anomalies)} categoria(s) fora do padrão)", expanded=True):
            for a in anomalies:
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(
                        f'<div style="padding:12px;background:var(--anomaly-bg);'
                        f'border-left:4px solid #E74C3C;border-radius:4px;">'
                        f'<span style="font-weight:700;font-size:0.9rem;">{a["category"]}</span><br>'
                        f'<span style="color:var(--text-secondary);font-size:0.8rem;">'
                        f'{a["excess_pct"]:.0f}% acima</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col2:
                    st.markdown(
                        f'<div style="padding:12px;">'
                        f'<span style="font-size:0.85rem;color:var(--text-secondary);">Este mês</span><br>'
                        f'<span style="font-weight:600;font-size:1rem;">R$ {a["current_spend"]:,.2f}</span><br>'
                        f'<span style="font-size:0.75rem;color:var(--text-secondary);">'
                        f'Histórico: R$ {a["avg_spend"]:,.2f}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
    else:
        with st.expander("✅ Alertas de Anomalias — tudo certo", expanded=False):
            st.caption("Nenhum gasto fora do padrão detectado neste período.")

    render_budget(df)
