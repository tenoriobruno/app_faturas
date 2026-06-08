"""
Configurações visuais e de estilo para o dashboard.
Editorial‑finance aesthetic, glassmorphism, font imports, CSS variables, apply_theme().
"""
def apply_theme():
    import streamlit as st
    st.markdown(CSS, unsafe_allow_html=True)
    if st.session_state.get("dark_mode", False):
        st.markdown(CSS_DARK, unsafe_allow_html=True)


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

:root {
    --font-heading: 'DM Sans', system-ui, -apple-system, sans-serif;
    --font-body: 'DM Sans', system-ui, -apple-system, sans-serif;
    --bg-page: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(61,90,128,0.05), transparent),
               radial-gradient(ellipse 50% 40% at 80% 100%, rgba(61,90,128,0.03), transparent),
               #F2F2F7;
    --bg-card: rgba(255, 255, 255, 0.78);
    --bg-card-solid: #FFFFFF;
    --border-card: rgba(206, 208, 212, 0.45);
    --border-card-accent: rgba(61, 90, 128, 0.18);
    --text-primary: #1C1E21;
    --text-secondary: #65676B;
    --accent: #3D5A80;
    --accent-soft: rgba(61, 90, 128, 0.08);
    --accent-glow: rgba(61, 90, 128, 0.15);
    --shadow-card: 0 1px 3px rgba(0,0,0,0.04), 0 8px 32px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.02);
    --shadow-elevated: 0 1px 3px rgba(0,0,0,0.04), 0 16px 48px rgba(0,0,0,0.08), 0 8px 24px rgba(0,0,0,0.04);
    --track-bg: rgba(0, 0, 0, 0.06);
    --input-bg: #FFFFFF;
    --divider: rgba(0, 0, 0, 0.06);
    --tab-inactive: rgba(0,0,0,0.04);
    --success: #2E7D32;
    --warning: #E65100;
    --danger: #C62828;
    --anomaly-bg: rgba(230, 81, 0, 0.08);
    --sidebar-bg: rgba(255,255,255,0.85);
}

/* ===================== RESET / BASE ===================== */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stVerticalBlock"] {
    background: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* Every Streamlit block wrapper inherits the background */
[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > section,
[data-testid="stMain"] > .block-container,
.main > div, section > div {
    background: transparent !important;
}

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stHeader"] { background: transparent !important; }

.block-container {
    padding: 1.75rem 2.5rem !important;
    max-width: 1440px;
    background: transparent !important;
}

/* ===================== TYPOGRAPHY ===================== */
h1, h2, h3 {
    font-family: var(--font-heading) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: var(--text-primary) !important;
}
h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em;
}
h2 { font-size: 1.35rem !important; font-weight: 600 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }

p, label, span, li, .stCaptionContainer, .stMarkdown {
    font-family: var(--font-body) !important;
    color: var(--text-primary) !important;
}

/* ===================== GLASS CARD ===================== */
.glass-card {
    background: var(--bg-card);
    backdrop-filter: blur(16px) saturate(1.4);
    -webkit-backdrop-filter: blur(16px) saturate(1.4);
    border-radius: 16px;
    border: 1px solid var(--border-card);
    box-shadow: var(--shadow-card);
    padding: 22px 26px;
    margin-bottom: 18px;
    transition: transform 0.25s cubic-bezier(0.22, 1, 0.36, 1),
                box-shadow 0.25s cubic-bezier(0.22, 1, 0.36, 1),
                background 0.3s ease, border 0.3s ease;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-elevated);
    border-color: var(--border-card-accent);
}
.glass-card h1, .glass-card h2, .glass-card h3,
.glass-card p, .glass-card span {
    margin: 0;
}

/* ===================== METRIC CARDS ===================== */
[data-testid="stMetric"] {
    background: var(--bg-card-solid) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    box-shadow: var(--shadow-card) !important;
    border: 1px solid var(--border-card) !important;
    margin-bottom: 10px !important;
    transition: all 0.22s cubic-bezier(0.22, 1, 0.36, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    background: var(--accent);
    border-radius: 0 2px 2px 0;
    opacity: 0.6;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-elevated) !important;
    border-color: var(--border-card-accent) !important;
}
[data-testid="stMetricLabel"] p {
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    margin: 0 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    font-family: var(--font-body) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.65rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    line-height: 1.15 !important;
    font-family: var(--font-body) !important;
}
[data-testid="stMetricDelta"] svg { display: none; }
[data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
    font-weight: 500 !important;
}

/* ===================== CHARTS ===================== */
[data-testid="stPlotlyChart"] {
    background: transparent !important;
    border-radius: 12px;
    padding: 4px;
    box-shadow: none;
    border: none;
}
.js-plotly-plot .plot-container {
    border-radius: 12px;
}

/* ===================== EXPANDER ===================== */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    backdrop-filter: blur(12px);
    border-radius: 14px !important;
    border: 1px solid var(--border-card) !important;
    box-shadow: var(--shadow-card) !important;
    overflow: hidden;
    transition: all 0.22s ease !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-card-accent) !important;
}

/* ===================== TABS ===================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: var(--tab-inactive);
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 1.25rem;
}
button[data-baseweb="tab"] {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.84rem !important;
    font-family: var(--font-body) !important;
    border-radius: 10px !important;
    padding: 6px 16px !important;
    transition: all 0.18s ease;
    border: none !important;
    background: transparent !important;
}
button[data-baseweb="tab"]:hover {
    background: rgba(0,0,0,0.04) !important;
    color: var(--text-primary) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
}
[data-testid="stTabs"] [role="tabpanel"] {
    padding-top: 0.5rem;
}

/* ===================== DIVIDER ===================== */
.stMarkdown hr, [data-testid="stVerticalBlockBorder"] {
    border-color: var(--divider) !important;
    margin: 1.25rem 0 !important;
}

/* ===================== SIDEBAR ===================== */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-right: 1px solid var(--border-card);
}
[data-testid="stSidebar"] > div {
    background: transparent !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1.25rem !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

/* ===================== INPUTS ===================== */
.stSelectbox > div > div,
.stSelectbox input,
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: var(--input-bg) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
.stSelectbox div[role="listbox"] {
    background-color: var(--input-bg) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-elevated) !important;
}
.stSelectbox div[role="option"] {
    background-color: transparent !important;
    color: var(--text-primary) !important;
    padding: 8px 12px;
    transition: background 0.12s ease;
}
.stSelectbox div[role="option"]:hover {
    background-color: var(--accent-soft) !important;
}
.stSelectbox div[role="option"][aria-selected="true"] {
    background-color: var(--accent-soft) !important;
    color: var(--accent) !important;
    font-weight: 600;
}

/* SLIDER */
.stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] > div {
    background-color: var(--track-bg) !important;
}
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* CHECKBOX */
.stCheckbox label {
    font-family: var(--font-body) !important;
}
.stCheckbox input:checked ~ div {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background-color: var(--input-bg) !important;
    border: 1px dashed var(--border-card) !important;
    border-radius: 12px;
    transition: border-color 0.18s ease;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploader"] section {
    color: var(--text-primary) !important;
}

/* BUTTON */
.stButton button {
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    transition: all 0.18s ease !important;
    border: 1px solid var(--border-card) !important;
}
.stButton button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
.stButton button:focus-visible,
button[data-baseweb="tab"]:focus-visible {
    outline: none !important;
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

/* DATA TABLE / EDITOR */
[data-testid="stDataFrame"], [data-testid="stTable"] {
    background: transparent !important;
}
[data-testid="stDataFrame"] [data-testid="stDataFrameContainer"] {
    border-radius: 12px !important;
    border: 1px solid var(--border-card) !important;
    overflow: hidden;
    background: var(--bg-card-solid) !important;
}
[data-testid="stDataFrame"] th {
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    color: var(--text-secondary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    background: var(--tab-inactive) !important;
}
[data-testid="stDataFrame"] td {
    font-family: var(--font-body) !important;
    font-size: 0.84rem !important;
}

/* CAPTION */
[data-testid="stCaptionContainer"] {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
}

.stDeployButton { display: none !important; }

/* ===================== PROGRESS ===================== */
.stProgress > div > div > div {
    background-color: var(--accent) !important;
}
.stProgress > div > div {
    background-color: var(--track-bg) !important;
}

/* ===================== RESPONSIVE ===================== */
@media (max-width: 1024px) {
    .block-container { padding: 1.25rem 1rem !important; }
    .glass-card { padding: 18px 20px; }
}
@media (max-width: 768px) {
    .block-container { padding: 1rem 0.75rem !important; }
    .glass-card { padding: 14px 14px; border-radius: 12px; }
    h1 { font-size: 1.4rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.35rem !important; }
    [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
    [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        width: 100% !important; min-width: 100% !important;
    }
    .stTabs [data-baseweb="tab-list"] { flex-wrap: wrap; }
}
</style>
"""

CSS_DARK = """
<style>
:root {
    --bg-page: radial-gradient(ellipse 90% 55% at 50% -10%, rgba(123,156,196,0.08), transparent),
               radial-gradient(ellipse 60% 40% at 80% 90%, rgba(123,156,196,0.04), transparent),
               #0B0F1A;
    --bg-card: rgba(22, 28, 45, 0.82);
    --bg-card-solid: #181E2E;
    --border-card: rgba(48, 54, 75, 0.55);
    --border-card-accent: rgba(123, 156, 196, 0.22);
    --text-primary: #F0F2F5;
    --text-secondary: #8B949E;
    --accent: #7B9CC4;
    --accent-soft: rgba(123, 156, 196, 0.1);
    --accent-glow: rgba(123, 156, 196, 0.18);
    --shadow-card: 0 1px 3px rgba(0,0,0,0.2), 0 8px 32px rgba(0,0,0,0.35);
    --shadow-elevated: 0 1px 3px rgba(0,0,0,0.2), 0 16px 48px rgba(0,0,0,0.45), 0 8px 24px rgba(0,0,0,0.2);
    --track-bg: rgba(255, 255, 255, 0.08);
    --input-bg: #1A2035;
    --divider: rgba(255, 255, 255, 0.06);
    --tab-inactive: rgba(255,255,255,0.04);
    --success: #66BB6A;
    --warning: #FFA726;
    --danger: #EF5350;
    --anomaly-bg: rgba(255, 167, 38, 0.1);
    --sidebar-bg: rgba(13, 17, 28, 0.92);
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stVerticalBlock"] {
    background: var(--bg-page) !important;
    color: var(--text-primary) !important;
}

h1, h2, h3, h4, h5, h6, p, label, span, div, li, .stMarkdown, .stCaptionContainer {
    color: var(--text-primary) !important;
}

/* DARK SIDEBAR */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right-color: var(--border-card) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }

/* DARK METRIC */
[data-testid="stMetric"] {
    background: var(--bg-card-solid) !important;
    border-color: var(--border-card) !important;
    box-shadow: var(--shadow-card) !important;
}
[data-testid="stMetric"]::before { background: var(--accent) !important; }
[data-testid="stMetricLabel"] p { color: var(--text-secondary) !important; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; }

/* DARK CHARTS */
[data-testid="stPlotlyChart"] {
    background: transparent !important;
}

/* DARK GLASS CARD */
.glass-card {
    background: var(--bg-card) !important;
    border-color: var(--border-card) !important;
    box-shadow: var(--shadow-card) !important;
}
.glass-card:hover {
    border-color: var(--border-card-accent) !important;
    box-shadow: var(--shadow-elevated) !important;
}

/* DARK EXPANDER */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border-color: var(--border-card) !important;
}

/* DARK TABS */
.stTabs [data-baseweb="tab-list"] {
    background: var(--tab-inactive) !important;
}
button[data-baseweb="tab"] {
    color: var(--text-secondary) !important;
}
button[data-baseweb="tab"]:hover {
    background: rgba(255,255,255,0.05) !important;
    color: var(--text-primary) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--accent-soft) !important;
    color: var(--accent) !important;
}

/* DARK INPUTS */
.stSelectbox > div > div,
.stSelectbox input,
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background-color: var(--input-bg) !important;
    border-color: var(--border-card) !important;
    color: var(--text-primary) !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput input:focus,
.stNumberInput input:focus,
.stDateInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
.stSelectbox div[role="listbox"] {
    background-color: var(--input-bg) !important;
}
.stSelectbox div[role="option"] {
    color: var(--text-primary) !important;
}
.stSelectbox div[role="option"]:hover,
.stSelectbox div[role="option"][aria-selected="true"] {
    background-color: var(--accent-soft) !important;
    color: var(--accent) !important;
}

/* DARK DATA FRAME */
[data-testid="stDataFrame"] [data-testid="stDataFrameContainer"] {
    background: var(--bg-card-solid) !important;
    border-color: var(--border-card) !important;
}
[data-testid="stDataFrame"] th {
    color: var(--text-secondary) !important;
    background: var(--tab-inactive) !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text-primary) !important;
}
[data-testid="stDataFrame"] [data-testid="stDataFrameDataCell"] {
    background: transparent !important;
}

/* DARK FILE UPLOADER */
[data-testid="stFileUploader"] {
    background-color: var(--input-bg) !important;
    border-color: var(--border-card) !important;
}

/* DARK BUTTON */
.stButton button {
    color: var(--text-primary) !important;
    background: var(--input-bg) !important;
    border-color: var(--border-card) !important;
}
.stButton button:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}

/* DARK CHECKBOX */
.stCheckbox input:checked ~ div {
    background-color: var(--accent) !important;
    border-color: var(--accent) !important;
}

/* DARK DIVIDER */
.stMarkdown hr, [data-testid="stVerticalBlockBorder"] {
    border-color: var(--divider) !important;
}

/* DARK CAPTION */
[data-testid="stCaptionContainer"] {
    color: var(--text-secondary) !important;
}

/* DARK PROGRESS */
.stProgress > div > div > div {
    background-color: var(--accent) !important;
}
.stProgress > div > div {
    background-color: var(--track-bg) !important;
}

/* DARK MOBILE RESPONSIVENESS */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column !important;
    }
}
</style>
"""

def get_plotly_layout(dark_mode: bool = False):
    """Return base Plotly layout dict adapted to theme."""
    if dark_mode:
        return dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8B949E', family='DM Sans, system-ui, sans-serif', size=12),
            hoverlabel=dict(
                bgcolor='#181E2E',
                bordercolor='#30364B',
                font=dict(color='#F0F2F5', size=13, family='DM Sans, system-ui, sans-serif')
            ),
            xaxis=dict(
                gridcolor='rgba(255,255,255,0.06)',
                linecolor='rgba(0,0,0,0)',
                tickfont=dict(color='#8B949E', size=12)
            ),
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.06)',
                linecolor='rgba(0,0,0,0)',
                tickfont=dict(color='#8B949E', size=12)
            ),
            )
    else:
        return dict(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#65676B', family='DM Sans, system-ui, sans-serif', size=12),
            hoverlabel=dict(
                bgcolor='#FFFFFF',
                bordercolor='#CED0D4',
                font=dict(color='#1C1E21', size=13, family='DM Sans, system-ui, sans-serif')
            ),
            xaxis=dict(
                gridcolor='rgba(0,0,0,0.06)',
                linecolor='rgba(0,0,0,0)',
                tickfont=dict(color='#65676B', size=12)
            ),
            yaxis=dict(
                gridcolor='rgba(0,0,0,0.06)',
                linecolor='rgba(0,0,0,0)',
                tickfont=dict(color='#65676B', size=12)
            ),
        )