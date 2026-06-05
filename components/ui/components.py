import streamlit as st
from typing import Optional

def Button(
    label: str,
    on_click: Optional[callable] = None,
    key: Optional[str] = None,
    **kwargs
):
    """Componente de botão reutilizável com estilo consistente."""
    return st.button(label, on_click=on_click, key=key, **kwargs)

def Input(label: str, value: str = "", key: str = None):
    """Componente de input reutilizável."""
    return st.text_input(label, value=value, key=key)

def Selectbox(label: str, options: list, key: str = None):
    """Componente de selectbox reutilizável."""
    return st.selectbox(label, options, key=key)