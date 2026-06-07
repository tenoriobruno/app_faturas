"""
Entry point do Dashboard Financeiro.
Orquestra o carregamento de múltiplos CSVs do Nubank, classificação automática
e roteia as visualizações para as abas (views).
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import os
from config.settings import settings
from utils.logger import get_logger
from data.repository import cache_repo

# Diretório onde os CSVs são armazenados – usado em todo o app
DATA_DIR = Path(settings.DATA_PATH)


from classifier.engine import classify_batch
from parsers import parse_csv
from config.theme import apply_theme
from config.categories import CATEGORY_COLORS
from components.header import render_header
from views.comparison import create_month_comparison

st.set_page_config(page_title="App Faturas", page_icon="💰", layout="wide")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = settings.DEFAULT_DARK_MODE

apply_theme()
render_header()

# Verifica se o arquivo de categorias foi alterado após o cache
if cache_repo.invalidate_if_stale(settings.CATEGORIES_PATH):
    st.info("⚙️ Cache de categorias atualizado por mudanças no categories.json.")

# Sidebar Upload
st.sidebar.header("📁 Upload de Faturas")
uploaded_file = st.sidebar.file_uploader("Novo arquivo (.csv)", type=["csv"])
if uploaded_file is not None:
    (DATA_DIR / uploaded_file.name).write_bytes(uploaded_file.getbuffer())
    st.sidebar.success(f"Arquivo {uploaded_file.name} salvo!")
    st.cache_data.clear()
    st.rerun()

csv_files = sorted(list(DATA_DIR.glob("*.csv")), reverse=True)
if not csv_files:
    st.info(f"📁 Nenhum arquivo CSV encontrado na pasta `{DATA_DIR}`")
    st.stop()

@st.cache_data
def load_all_data(files):
    frames = {}
    for f in files:
        try:
            df = classify_batch(parse_csv(str(f)))
            frames[f.name] = df
        except Exception as e:
            get_logger(__name__).error(f"Erro ao carregar {f.name}: {e}")
    return frames

all_data = load_all_data(tuple(csv_files))
if not all_data:
    st.error("Nenhum CSV válido encontrado")
    st.stop()

df_consolidated = pd.concat(all_data.values(), ignore_index=True)

selected_file = st.sidebar.selectbox("Selecione o arquivo CSV:", csv_files, format_func=lambda x: x.name) if len(csv_files) > 1 else csv_files[0]
df = all_data[selected_file.name].copy()
df['date'] = pd.to_datetime(df['date'])

from components.sidebar import render_sidebar
from utils.export import render_export_button

df_filtered = render_sidebar(df, list(CATEGORY_COLORS.keys()))
st.sidebar.divider()
render_export_button(df_filtered, filename=f"faturas_{selected_file.name}")

if len(df_filtered) > 0:
    st.caption(f"📅 {df_filtered['date'].min().strftime('%d/%m/%Y')} a {df_filtered['date'].max().strftime('%d/%m/%Y')} · {len(df_filtered)} transações · {selected_file.name}")
else:
    st.caption("Nenhuma transação encontrada.")

tabs = st.tabs(["Visão Geral", "Transações", "Comparação Mês a Mês", "Recorrências", "Parcelas Futuras"])

with tabs[0]:
    from views.overview import render_overview
    render_overview(df_filtered, df_consolidated, csv_files, selected_file, all_data)

with tabs[1]:
    from views.transactions import render_transactions
    render_transactions(df_filtered, load_all_data)

with tabs[2]:
    from views.comparison import create_month_comparison
    create_month_comparison(df_consolidated)

with tabs[3]:
    from views.recurrences import render_recurrences
    render_recurrences(df_consolidated)

with tabs[4]:
    from views.installments import render_installments
    render_installments(df_consolidated)
