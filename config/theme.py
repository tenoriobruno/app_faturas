"""
Configurações visuais e de estilo para o dashboard.
Consolida CSS, paleta de cores e configurações do Plotly.
"""

# === ESTILIZAÇÃO CUSTOMIZADA (CSS) ===
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #D6E4F7 0%, #E8EEF8 50%, #D8E8F5 100%);
    min-height: 100vh;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
}

/* === TITLE === */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: #1A1D23 !important;
    margin-bottom: 0.25rem !important;
}

/* === SECTION HEADERS === */
h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #1A1D23 !important;
    margin-bottom: 0.75rem !important;
    margin-top: 0 !important;
}

/* === CARDS (st.metric) === */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 24px 28px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
    border: none;
    margin-bottom: 12px;
}

[data-testid="stMetricLabel"] p {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #8A92A6 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin: 0 !important;
}

[data-testid="stMetricValue"] {
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: #1A1D23 !important;
    font-family: 'Inter', sans-serif !important;
    line-height: 1.1 !important;
}

/* === SELECT BOX === */
[data-testid="stSelectbox"] {
    background: #FFFFFF !important;
    border-radius: 12px !important;
}

[data-testid="stSelectbox"] label {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    color: #8A92A6 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

[data-testid="stSelectbox"] > div {
    background: #FFFFFF !important;
}

[data-testid="stSelectbox"] > div > div {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
    color: #1A1D2E !important;
}

[data-testid="stSelectbox"] input {
    background: #FFFFFF !important;
    color: #1A1D2E !important;
}

/* Combobox overlay */
.stComboboxContainer {
    background: #FFFFFF !important;
}

[role="listbox"] {
    background: #FFFFFF !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 12px !important;
}

[role="option"] {
    background: #FFFFFF !important;
    color: #1A1D2E !important;
}

[role="option"]:hover {
    background: #F8FAFC !important;
}

[role="option"][aria-selected="true"] {
    background: #BFD4F7 !important;
    color: #1A1D2E !important;
}

/* === SUCCESS / INFO ALERTS === */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: none !important;
}

/* === CHART CONTAINERS === */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 16px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
}

/* === EXPANDER === */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border-radius: 16px !important;
    border: none !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.07);
    overflow: hidden;
}

/* === DATAFRAME === */
[data-testid="stDataFrame"] {
    background: #FFFFFF;
}

/* === DIVIDER SPACING === */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

/* === SUCCESS MSG === */
.stSuccess {
    background: #F0FDF4 !important;
    color: #166534 !important;
    border-radius: 12px !important;
    border-left: 4px solid #22C55E !important;
}

/* === CAPTION === */
[data-testid="stCaptionContainer"] {
    color: #64748B !important;
}
</style>
"""

CATEGORY_COLORS = {
    'Delivery': '#1E293B',
    'Alimentação': '#8A05BE',
    'Transporte': '#22C55E',
    'Compras': '#EF4444',
    'Saúde': '#F59E0B',
    'Assinaturas': '#3B82F6',
    'Moradia': '#EC4899',
    'Lazer': '#10B981',
    'Educação': '#6366F1',
    'Viagem': '#F97316',
    'Restaurante': '#7C6FF7',
    'Supermercado': '#52C2A0',
    'Serviço': '#6B9CF0',
    'Feira': '#F0A868',
    'Gasolina': '#5BBCD4',
    'Estorno': '#A78BFA',
    'Outros': '#94A3B8'
}

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#64748B', family='Inter', size=12),
    hoverlabel=dict(
        bgcolor='#FFFFFF',
        bordercolor='#E2E8F0',
        font=dict(color='#1A1D23', size=13, family='Inter')
    )
)
