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
    st.info(
        f"📁 **Nenhum arquivo CSV encontrado em `{DATA_DIR}`.**\n\n"
        "Use o campo **'Novo arquivo (.csv)'** na barra lateral, acima, para enviar "
        "uma fatura exportada do Nubank ou Itaú."
    )
    st.stop()

@st.cache_data
def load_all_data(files):
    frames = {}
    errors = {}
    for f in files:
        try:
            df = classify_batch(parse_csv(str(f)))
            frames[f.name] = df
        except Exception as e:
            get_logger(__name__).error(f"Erro ao carregar {f.name}: {e}")
            errors[f.name] = str(e)
    return frames, errors

all_data, load_errors = load_all_data(tuple(csv_files))

if load_errors:
    nomes = ", ".join(f"`{n}`" for n in load_errors)
    st.warning(
        f"⚠️ Não consegui ler {len(load_errors)} arquivo(s): {nomes}.\n\n"
        "Verifique se são exports de fatura do Nubank/Itaú em CSV (encoding UTF-8 ou Latin-1) "
        "e não, por exemplo, planilhas com outro layout. Detalhes no log da aplicação."
    )

if not all_data:
    st.error(
        "❌ **Nenhum arquivo CSV válido encontrado.**\n\n"
        "Os arquivos da pasta não puderam ser processados — confira o formato "
        "(deve ser export de fatura Nubank ou Itaú) e tente enviar novamente."
    )
    st.stop()

df_consolidated = pd.concat(all_data.values(), ignore_index=True)

selected_file = st.sidebar.selectbox("Selecione o arquivo CSV:", csv_files, format_func=lambda x: x.name) if len(csv_files) > 1 else csv_files[0]
df = all_data[selected_file.name].copy()
df['date'] = pd.to_datetime(df['date'])

from components.sidebar import render_sidebar
from components.budget import render_budget_sidebar_summary

render_budget_sidebar_summary(df)
df_filtered = render_sidebar(df, list(CATEGORY_COLORS.keys()))

if len(df_filtered) > 0:
    periodo_txt = (
        f"📅 <strong>{df_filtered['date'].min().strftime('%d/%m/%Y')} a {df_filtered['date'].max().strftime('%d/%m/%Y')}</strong>"
        f" &nbsp;·&nbsp; 📄 {selected_file.name} &nbsp;·&nbsp; {len(df_filtered)} transações"
    )
else:
    periodo_txt = f"📄 {selected_file.name} &nbsp;·&nbsp; Nenhuma transação encontrada."

st.markdown(
    f'<div class="glass-card" style="padding:10px 16px;margin-bottom:16px;font-size:0.92rem;">{periodo_txt}</div>',
    unsafe_allow_html=True,
)

# Resumo rápido — visível antes de entrar em qualquer aba
from core.metrics import calculate_overview_metrics
from core.anomalies import detect_anomalies
from components.metrics import metric_card

_prev_df = None
try:
    _idx = csv_files.index(selected_file)
    if _idx + 1 < len(csv_files):
        _prev_df = all_data[csv_files[_idx + 1].name]
except ValueError:
    pass

_summary = calculate_overview_metrics(df_filtered, _prev_df)
_anomalies = detect_anomalies(df_filtered, df_consolidated)

from data.repository import budget_repo as _budget_repo
from core.projections import calculate_linear_projection as _calc_projection

_budgets = _budget_repo.load() or {"global": 0, "categories": {}}
_global_budget = _budgets.get("global", 0)
_budget_status_txt = "Não configurado"
if _global_budget > 0:
    _projection = _calc_projection(df_filtered, _global_budget, _budgets.get("categories", {}))
    if _projection['global_warning']:
        _budget_status_txt = "🚨 Estourado" if not _projection['is_current_month'] else "⚠️ Risco de estourar"
    else:
        _budget_status_txt = "✅ Sob controle"

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    metric_card(
        "Gasto no Período",
        f"R$ {_summary['valor_total']:,.2f}",
        delta=f"R$ {_summary['delta_valor']:+,.2f}" if _summary['delta_valor'] is not None else None,
        delta_color="inverse",
        help_text="Comparado ao mês/fatura anterior",
    )
with col_s2:
    metric_card("Maior Categoria", _summary['top_cat'])
with col_s3:
    if _anomalies:
        metric_card("Alertas de Anomalia", f"⚠️ {len(_anomalies)} categoria(s)")
    else:
        metric_card("Alertas de Anomalia", "✅ Tudo certo")
with col_s4:
    metric_card("🎯 Orçamento", _budget_status_txt)

tabs = st.tabs(["Visão Geral", "Transações", "Comparação Mês a Mês", "Recorrências", "Parcelas Futuras"])

with tabs[0]:
    from views.overview import render_overview
    render_overview(df_filtered, df_consolidated, csv_files, selected_file, all_data)

with tabs[1]:
    from views.transactions import render_transactions
    render_transactions(df_filtered, load_all_data, export_filename=f"faturas_{selected_file.name}")

with tabs[2]:
    from views.comparison import create_month_comparison
    create_month_comparison(df_consolidated)

with tabs[3]:
    from views.recurrences import render_recurrences
    render_recurrences(df_consolidated)

with tabs[4]:
    from views.installments import render_installments
    render_installments(df_consolidated)
