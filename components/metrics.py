import streamlit as st

def metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal", help_text: str = None):
    """Renderiza um card de métrica estilizado com suporte a glass‑morphism."""
    
    # Define a cor do delta de acordo com o delta_color
    delta_html = ""
    if delta:
        color_style = "var(--accent)"
        if delta_color == "inverse":
            if delta.startswith("-"):
                color_style = "#2ECC71" # verde (bom se for queda de gastos)
            else:
                color_style = "#E74C3C" # vermelho (ruim se for aumento de gastos)
        elif delta_color == "normal":
            if delta.startswith("-"):
                color_style = "#E74C3C"
            else:
                color_style = "#2ECC71"
        
        delta_html = f'<div style="font-size: 0.85rem; font-weight: 600; color: {color_style}; margin-top: 4px;">{delta}</div>'
    
    help_html = f' title="{help_text}"' if help_text else ""
    
    st.markdown(
        f'<div class="glass-card" style="padding: 16px 20px; min-height: 100px;"{help_html}>'
        f'<div style="font-size: 0.82rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.02em;">{label}</div>'
        f'<div style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); line-height: 1.2; margin-top: 4px;">{value}</div>'
        f'{delta_html}'
        f'</div>',
        unsafe_allow_html=True
    )
