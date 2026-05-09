"""
Configurações visuais e de estilo para o dashboard.
Consolida CSS, paleta de cores e configurações do Plotly.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
}

#MainMenu, footer, header {
    visibility: hidden;
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
    font-family: 'Segoe UI', sans-serif !important;
    font-weight: 700 !important;
    margin-bottom: 0.25rem !important;
    color: #1C1E21 !important;
}

/* === SECTION HEADERS === */
h2, h3 {
    font-family: 'Segoe UI', sans-serif !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
    margin-top: 0 !important;
    color: #1C1E21 !important;
}

/* === CARDS (st.metric) === */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    border: 1px solid #CED0D4;
    margin-bottom: 12px;
}

[data-testid="stMetricLabel"] p {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #65676B !important;
    margin: 0 !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: #1C1E21 !important;
    line-height: 1.1 !important;
}

/* === CHART CONTAINERS === */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    border: 1px solid #CED0D4;
}

/* === EXPANDER === */
[data-testid="stExpander"] {
    background: #FFFFFF;
    border-radius: 8px !important;
    border: 1px solid #CED0D4 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    overflow: hidden;
}

/* === TABS === */
button[data-baseweb="tab"] {
    color: #65676B !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #0866FF !important;
}

/* === DIVIDER SPACING === */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

/* === CAPTION === */
[data-testid="stCaptionContainer"] {
    color: #65676B !important;
}
</style>
"""

# Paleta Refinada Premium
CATEGORY_COLORS = {
    'Delivery': '#4B4F56',       
    'Alimentação': '#8B5CF6',    
    'Transporte': '#00A400',     # FB WhatsApp Green
    'Compras': '#FA383E',        # FB Notification Red
    'Saúde': '#F59E0B',          
    'Assinaturas': '#0866FF',    # FB Blue
    'Moradia': '#E1306C',        # Instagram Pink
    'Lazer': '#14B8A6',          
    'Educação': '#6366F1',       
    'Viagem': '#F97316',         
    'Restaurante': '#A855F7',    
    'Supermercado': '#06B6D4',   
    'Serviço': '#0EA5E9',        
    'Feira': '#EAB308',          
    'Gasolina': '#F43F5E',       
    'Estorno': '#84CC16',        
    'Outros': '#8D949E'          
}

PLOT_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#65676B', family='Segoe UI, sans-serif', size=12),
    hoverlabel=dict(
        bgcolor='#FFFFFF',
        bordercolor='#CED0D4',
        font=dict(color='#1C1E21', size=13, family='Segoe UI, sans-serif')
    )
)
