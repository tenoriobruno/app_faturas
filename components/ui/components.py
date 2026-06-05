import streamlit as st
from typing import Optional, Callable, Any, Sequence

def Button(
    label: str,
    on_click: Optional[Callable[[Any], Any]] = None,
    key: Optional[str] = None,
    **kwargs
):
    """Componente de botão reutilizável com estilo consistente."""
    # Adiciona atributos de acessibilidade básicos
    if 'aria-label' not in kwargs and 'help' in kwargs:
        kwargs['aria_label'] = kwargs['help']
    return st.button(label, on_click=on_click, key=key, **kwargs)

def Input(label: str, value: str = "", key: Optional[str] = None, **kwargs):
    """Componente de input reutilizável."""
    # Adiciona atributos de acessibilidade básicos
    if 'aria_label' not in kwargs:
        kwargs['aria_label'] = label
    return st.text_input(label, value=value, key=key, **kwargs)

def Selectbox(label: str, options: Sequence[str], key: Optional[str] = None, **kwargs):
    """Componente de selectbox reutilizável."""
    # Adiciona atributos de acessibilidade básicos
    if 'aria_label' not in kwargs:
        kwargs['aria_label'] = label
    return st.selectbox(label, options, key=key, **kwargs)