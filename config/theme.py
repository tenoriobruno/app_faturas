"""
Configurações visuais e de estilo para o dashboard.
Consolida CSS, paleta de cores e configurações do Plotly.
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --font-main: 'Inter', system-ui, -apple-system, sans-serif;
    --bg-page: #F0F2F5;
    --bg-card: rgba(255, 255, 255, 0.72);
    --bg-card-solid: #FFFFFF;
    --border-card: rgba(206, 208, 212, 0.6);
    --text-primary: #1C1E21;
    --text-secondary: #65676B;
    --accent: #0866FF;
    --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.08), 0 1px 4px rgba(0, 0, 0, 0.06);
}

html, body, [class*="css"] {
    font-family: var(--font-main);
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
    font-family: var(--font-main) !important;
    font-weight: 700 !important;
    margin-bottom: 0.25rem !important;
    color: var(--text-primary) !important;
}

/* === SECTION HEADERS === */
h2, h3 {
    font-family: var(--font-main) !important;
    font-weight: 600 !important;
    margin-bottom: 0.75rem !important;
    margin-top: 0 !important;
    color: var(--text-primary) !important;
}

/* === GLASS CARD === */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 14px;
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-card);
    padding: 20px 24px;
    margin-bottom: 16px;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* === CARDS (st.metric) === */
[data-testid="stMetric"] {
    background: var(--bg-card-solid);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-card);
    margin-bottom: 12px;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

[data-testid="stMetricLabel"] p {
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    margin: 0 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    line-height: 1.1 !important;
    font-family: var(--font-main) !important;
}

/* === CHART CONTAINERS === */
[data-testid="stPlotlyChart"] {
    background: var(--bg-card-solid);
    border-radius: 12px;
    padding: 16px;
    box-shadow: var(--shadow-card);
    border: 1px solid var(--border-card);
}

/* === EXPANDER === */
[data-testid="stExpander"] {
    background: var(--bg-card-solid);
    border-radius: 12px !important;
    border: 1px solid var(--border-card) !important;
    box-shadow: var(--shadow-card);
    overflow: hidden;
}

/* === TABS === */
button[data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-family: var(--font-main) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
}

/* === DIVIDER SPACING === */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}

/* === CAPTION === */
[data-testid="stCaptionContainer"] {
    color: var(--text-secondary) !important;
}

/* === SELECT BOX STYLING === */
.stDeployButton { display: none !important; }

.stSelectbox {
  background-color: white !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
}

.stSelectbox > div > div {
  background-color: white !important;
  color: var(--text-primary) !important;
}

.stSelectbox div[role="listbox"] {
  background-color: white !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px !important;
}

.stSelectbox div[role="option"] {
  background-color: white !important;
  color: var(--text-primary) !important;
  padding: 8px 12px;
}

.stSelectbox div[role="option"]:hover {
  background-color: #F8FAFC !important;
}

.stSelectbox input {
  background-color: white !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
  border-radius: 12px !important;
  color: var(--text-primary) !important;
}

/* === RESPONSIVE: tablet (≤1024px) === */
@media (max-width: 1024px) {
    .block-container {
        padding: 1.5rem 1.25rem !important;
    }

    .glass-card {
        padding: 16px 18px;
    }
}

/* === RESPONSIVE: mobile (≤768px) === */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.75rem !important;
    }

    .glass-card {
        padding: 14px 14px;
        border-radius: 10px;
    }

    h1 {
        font-size: 1.4rem !important;
    }

    [data-testid=\"stMetricValue\"] {
        font-size: 1.4rem !important;
    }

    /* Empilha colunas do Streamlit verticalmente */
    [data-testid=\"stHorizontalBlock\"] {
        flex-direction: column !important;
    }

    [data-testid=\"stHorizontalBlock\"] > [data-testid=\"stVerticalBlock\"] {
        width: 100% !important;
        min-width: 100% !important;
    }
}
</style>
"""

CSS_DARK = """
<style>
/* ===== DARK MODE: variáveis e overrides ===== */
:root {
    --bg-page: #0E1117;
    --bg-card: rgba(28, 35, 51, 0.8);
    --bg-card-solid: #1C2333;
    --border-card: rgba(48, 54, 61, 0.7);
    --text-primary: #FAFAFA;
    --text-secondary: #8B949E;
    --accent: #58A6FF;
    --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.3), 0 1px 4px rgba(0, 0, 0, 0.2);
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stVerticalBlock"], .main, .block-container {
    background-color: #0E1117 !important;
    color: #FAFAFA !important;
}

[data-testid="stSidebar"] {
    background-color: #161B22 !important;
}
[data-testid="stSidebar"] * {
    color: #FAFAFA !important;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #FAFAFA !important;
}

[data-testid="stMetric"] {
    background: #1C2333 !important;
    border-color: #30363D !important;
}
[data-testid="stMetricLabel"] p {
    color: #8B949E !important;
}
[data-testid="stMetricValue"] {
    color: #FAFAFA !important;
}

[data-testid="stPlotlyChart"] {
    background: #1C2333 !important;
    border-color: #30363D !important;
}

[data-testid="stExpander"] {
    background: #1C2333 !important;
    border-color: #30363D !important;
}

[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: #1C2333 !important;
}

button[data-baseweb="tab"] {
    color: #8B949E !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #58A6FF !important;
}

.stSelectbox > div > div, .stSelectbox input {
    background-color: #1C2333 !important;
    color: #FAFAFA !important;
    border-color: #30363D !important;
}

[data-testid="stCaptionContainer"] {
    color: #8B949E !important;
}

.glass-card {
    background: rgba(28, 35, 51, 0.8) !important;
    border-color: rgba(48, 54, 61, 0.7) !important;
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
    font=dict(color='#65676B', family='Inter, system-ui, sans-serif', size=12),
    hoverlabel=dict(
        bgcolor='#FFFFFF',
        bordercolor='#CED0D4',
        font=dict(color='#1C1E21', size=13, family='Inter, system-ui, sans-serif')
    )
)
