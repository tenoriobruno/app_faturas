# Updated header component with visible dark‑mode toggle
import streamlit as st
from config.settings import settings


def render_header():
    """Render the app header with title and a dark‑mode toggle.

    The toggle updates ``st.session_state.dark_mode`` and triggers a rerun.
    """
    # Ensure dark_mode default is set
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = settings.DEFAULT_DARK_MODE

    # Layout: title on the left, toggle on the right
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("""
        <h1 style='margin:0;'>Finanças Pessoais</h1>
        """, unsafe_allow_html=True)
    with col2:
        # Use a simple button to act as toggle, showing sun/moon based on state
        button_label = "🌙" if st.session_state.dark_mode else "☀️"
        if st.button(button_label, key="dark_mode_button"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
