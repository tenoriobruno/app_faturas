import streamlit as st
from typing import Optional, Callable, Any, Sequence

def Button(
    label: str,
    on_click: Optional[Callable[[Any], Any]] = None,
    key: Optional[str] = None,
    help_text: Optional[str] = None,
    **kwargs
):
    """Componente de botão reutilizável com estilo consistente."""
    return st.button(label, on_click=on_click, key=key, help=help_text, **kwargs)

def Input(label: str, value: str = "", key: Optional[str] = None, help_text: Optional[str] = None, **kwargs):
    """Componente de input reutilizável."""
    return st.text_input(label, value=value, key=key, help=help_text, **kwargs)

def Selectbox(label: str, options: Sequence[str], key: Optional[str] = None, help_text: Optional[str] = None, **kwargs):
    """Componente de selectbox reutilizável."""
    return st.selectbox(label, options, key=key, help=help_text, **kwargs)