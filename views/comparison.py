import streamlit as st
import pandas as pd
import plotly.express as px

def create_month_comparison(df):
    """Create month-over-month comparison table with variations."""
    st.subheader("📊 Comparação Mês a Mês")

    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)

    if df.empty or 'month' not in df.columns or 'categoria' not in df.columns:
        st.info("Sem dados suficientes para comparação.")
        return

    # Create monthly pivot table by category
    monthly_totals = df.pivot_table(
        values='amount',
        index='categoria',
        columns='month',
        aggfunc='sum',
        fill_value=0
    )

    # Sort columns chronologically
    monthly_totals = monthly_totals.reindex(sorted(monthly_totals.columns), axis=1)

    if len(monthly_totals.columns) < 2:
        st.info("É preciso de pelo menos 2 meses de dados para comparar.")
        return

    # Calculate variations (R$ and %)
    last_month = monthly_totals.columns[-1]
    prev_month = monthly_totals.columns[-2]

    comparison_data = []
    for cat in monthly_totals.index:
        last_val = monthly_totals.loc[cat, last_month]
        prev_val = monthly_totals.loc[cat, prev_month]
        delta = last_val - prev_val
        delta_pct = (delta / prev_val * 100) if prev_val != 0 else 0
        comparison_data.append({
            'Categoria': cat,
            f'{prev_month} (R$)': prev_val,
            f'{last_month} (R$)': last_val,
            'Variação (R$)': delta,
            'Variação (%)': delta_pct
        })

    comp_df = pd.DataFrame(comparison_data)

    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        total_last = comp_df[f'{last_month} (R$)'].sum()
        st.metric("Gasto Total (Mês Atual)", f"R$ {total_last:,.2f}")
    with col2:
        total_prev = comp_df[f'{prev_month} (R$)'].sum()
        total_delta = total_last - total_prev
        total_delta_pct = (total_delta / total_prev * 100) if total_prev != 0 else 0
        st.metric("Variação vs Mês Anterior", f"R$ {total_delta:+,.2f}", f"{total_delta_pct:+.1f}%")

    # Chart
    st.subheader("Gastos por Categoria")
    fig = px.bar(
        monthly_totals.T,
        barmode='group',
        title=f"Gastos por Categoria ({monthly_totals.columns[0]} a {monthly_totals.columns[-1]})",
        labels={'value': 'Valor (R$)', 'month': 'Mês', 'categoria': 'Categoria'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Detailed table with styling
    st.subheader("Dados Detalhados")
    styled_df = comp_df.style.format({
        f'{prev_month} (R$)': 'R$ {:,.2f}',
        f'{last_month} (R$)': 'R$ {:,.2f}',
        'Variação (R$)': 'R$ {:+,.2f}',
        'Variação (%)': '{:+.1f}%'
    })

    # Color negative variations in red, positive in green
    def highlight_variation(val):
        if isinstance(val, str) and ('R$' in val or '%' in val):
            return ''
        if val > 0:
            return 'color: #e74c3c'
        elif val < 0:
            return 'color: #27ae60'
        return ''

    styled_df = styled_df.applymap(highlight_variation, subset=['Variação (R$)', 'Variação (%)'])
    st.dataframe(styled_df, use_container_width=True, hide_index=True)
