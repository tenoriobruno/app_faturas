import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config.theme import CATEGORY_COLORS, PLOT_LAYOUT

def render_donut(df: pd.DataFrame):
    """Renderiza o gráfico de donut para distribuição de gastos por categoria."""
    category_spend = df.groupby('categoria')['amount'].sum().sort_values(ascending=False)
    pie_colors = [CATEGORY_COLORS.get(cat, '#94A3B8') for cat in category_spend.index]

    fig_pie = go.Figure(data=[go.Pie(
        labels=category_spend.index,
        values=category_spend.values,
        textposition='auto',
        textinfo='label+percent',
        textfont=dict(size=11, family='Inter'),
        insidetextfont=dict(color='white'),
        hovertemplate='<b>%{label}</b><br>R$ %{value:,.2f}<br>%{percent}<extra></extra>',
        marker=dict(
            colors=pie_colors,
            line=dict(color='#FFFFFF', width=2)
        ),
        hole=0.45
    )])

    fig_pie.update_layout(
        **PLOT_LAYOUT,
        margin=dict(t=16, b=16, l=16, r=120),
        height=400,
        showlegend=True,
        legend=dict(
            orientation='v',
            x=1.02,
            y=0.5,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=11, color='#64748B')
        )
    )

    st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

def render_bar_history(df_consolidated: pd.DataFrame):
    """Renderiza o gráfico de barras empilhadas para histórico mensal."""
    df = df_consolidated.copy()
    df = df[df['tipo_transacao'] == 'gasto']
    df['date'] = pd.to_datetime(df['date'])
    df['month_year'] = df['date'].dt.strftime('%b/%y').str.lower()

    monthly_category = df.groupby(['date', 'month_year', 'categoria'])['amount'].sum().reset_index()
    monthly_pivot = monthly_category.pivot_table(
        index='month_year', columns='categoria', values='amount', aggfunc='sum'
    ).fillna(0)

    month_order = df.drop_duplicates('month_year').sort_values('date')['month_year'].tolist()
    monthly_pivot = monthly_pivot.reindex(month_order)

    monthly_totals = monthly_pivot.sum(axis=1)

    fig_bar = go.Figure()
    seen_legend = set()
    for month in monthly_pivot.index:
        month_values = monthly_pivot.loc[month]
        cat_order = month_values.sort_values(ascending=False).index
        for category in cat_order:
            val = month_values.get(category, 0)
            pct = 0
            if monthly_totals.loc[month] and monthly_totals.loc[month] != 0:
                pct = round((val / monthly_totals.loc[month]) * 100, 1)
            text_label = f'{pct:.0f}%' if pct >= 10 else ''

            showlegend = category not in seen_legend
            if showlegend:
                seen_legend.add(category)

            fig_bar.add_trace(go.Bar(
                x=[month],
                y=[val],
                name=category,
                legendgroup=category,
                showlegend=showlegend,
                marker_color=CATEGORY_COLORS.get(category, '#94A3B8'),
                marker_line_width=0,
                text=[text_label],
                textposition='inside',
                textfont=dict(size=10, color='white', family='Inter'),
                hovertemplate='<b>%{fullData.name}</b><br>%{x}<br>R$ %{y:,.2f}<extra></extra>'
            ))

    rolling = monthly_totals.rolling(3, min_periods=1).mean()
    fig_bar.add_trace(go.Scatter(
        x=monthly_pivot.index,
        y=rolling,
        name='Média Móvel 3m',
        mode='lines+markers',
        line=dict(color='#1A1D23', width=2, dash='dot'),
        marker=dict(size=6)
    ))

    fig_bar.update_layout(
        **PLOT_LAYOUT,
        barmode='stack',
        xaxis_title='',
        yaxis_title='R$',
        xaxis=dict(
            gridcolor='rgba(0,0,0,0)',
            linecolor='rgba(0,0,0,0)',
            tickfont=dict(color='#94A3B8', size=12)
        ),
        yaxis=dict(
            gridcolor='rgba(0,0,0,0.06)',
            linecolor='rgba(0,0,0,0)',
            tickfont=dict(color='#94A3B8', size=12),
            tickprefix='R$ '
        ),
        hovermode='x unified',
        height=340,
        showlegend=True,
        legend=dict(
            orientation='h',
            y=-0.22,
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(0,0,0,0)',
            font=dict(size=11, color='#64748B')
        ),
        margin=dict(t=16, b=60, l=50, r=16),
        bargap=0.25,
        bargroupgap=0.1
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")
