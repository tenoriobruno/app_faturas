import streamlit as st
import pandas as pd
from components.charts import render_donut, render_bar_history
from components.budget import render_budget
from components.metrics import metric_card
from core.anomalies import detect_anomalies
from core.projections import calculate_linear_projection
from data.repository import budget_repo


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

    _render_month_health(df, df_consolidated)

    render_budget(df, df_consolidated)


def _render_month_health(df: pd.DataFrame, df_consolidated: pd.DataFrame):
    """Painel unificado: categorias que estouraram o orçamento e/ou estão fora
    do padrão histórico (anomalias). Marca quando as duas coisas coincidem —
    sinal mais forte de atenção."""
    anomalies = detect_anomalies(df, df_consolidated)
    anomaly_by_cat = {a['category']: a for a in anomalies}

    budgets = budget_repo.load() or {"global": 0, "categories": {}}
    cat_budgets = budgets.get("categories", {})
    projection = calculate_linear_projection(df, budgets.get("global", 0), cat_budgets)
    over_budget_by_cat = {c: p for c, p in projection['cat_projections'].items() if p['spent_pct'] >= 100}

    health_cats = sorted(set(anomaly_by_cat) | set(over_budget_by_cat))

    if not health_cats:
        with st.expander("✅ Saúde do Mês — tudo certo", expanded=False):
            st.caption("Nenhuma categoria fora do padrão ou acima do orçamento neste período.")
        return

    with st.expander(f"🩺 Saúde do Mês ({len(health_cats)} categoria(s) pedem atenção)", expanded=True):
        for cat in health_cats:
            anomaly = anomaly_by_cat.get(cat)
            over = over_budget_by_cat.get(cat)

            tags = []
            if over:
                tags.append('<span style="background:#E74C3C;color:white;font-size:0.7rem;font-weight:700;'
                            'padding:2px 8px;border-radius:10px;">💰 ESTOUROU LIMITE</span>')
            if anomaly:
                tags.append('<span style="background:#F39C12;color:white;font-size:0.7rem;font-weight:700;'
                            'padding:2px 8px;border-radius:10px;">📈 FORA DO PADRÃO</span>')
            border_color = "#E74C3C" if (over and anomaly) else ("#E74C3C" if over else "#F39C12")

            details = []
            if over:
                details.append(f'Orçamento: R$ {over["spent"]:,.2f} / R$ {over["limit"]:,.2f} ({over["spent_pct"]:.0f}%)')
            if anomaly:
                details.append(f'Histórico médio: R$ {anomaly["avg_spend"]:,.2f} &nbsp;·&nbsp; {anomaly["excess_pct"]:.0f}% acima do normal')

            st.markdown(
                f'<div style="padding:12px 16px;background:var(--anomaly-bg);'
                f'border-left:4px solid {border_color};border-radius:4px;margin-bottom:8px;">'
                f'<span style="font-weight:700;font-size:0.92rem;">{cat}</span> &nbsp;'
                f'{" ".join(tags)}<br>'
                f'<span style="color:var(--text-secondary);font-size:0.8rem;">{" &nbsp;|&nbsp; ".join(details)}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
