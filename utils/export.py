import pandas as pd
import streamlit as st

def render_export_button(df: pd.DataFrame, filename: str = "exportacao.csv"):
    """Renderiza um botão de download para o DataFrame fornecido."""
    if df.empty:
        return
        
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados (CSV)",
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )
