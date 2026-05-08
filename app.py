"""
Entry point do Dashboard Financeiro.
Orquestra o carregamento de múltiplos CSVs do Nubank, classificação automática
e renderização de visualizações interativas usando Streamlit e Plotly.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
import os
from dotenv import load_dotenv
from classifier.engine import classify_batch
from parsers.nubank import parse_nubank
from config.theme import CSS, CATEGORY_COLORS
from components.charts import render_donut, render_bar_history

st.set_page_config(page_title="Finanças", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.title("💰 Finanças Pessoais")

# === CARREGAMENTO DE DADOS ===
load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")
if not DATA_PATH:
    raise ValueError("DATA_PATH não definido no .env")
# Buscamos todos os arquivos .csv na pasta configurada
DATA_DIR = Path(DATA_PATH)
csv_files = sorted(list(DATA_DIR.glob("*.csv")), reverse=True)

if not csv_files:
    st.info(f"📁 Nenhum arquivo CSV encontrado na pasta `{DATA_PATH}`")
    st.stop()

@st.cache_data
def load_all_data(csv_files):
    """Carrega e classifica todos os CSVs, retornando um dicionário de DataFrames."""
    frames = {}
    for f in csv_files:
        try:
            df_temp = parse_nubank(str(f))
            df_temp = classify_batch(df_temp)
            # Filtramos transações de ajuste de saldo ou pagamento de fatura
            df_temp = df_temp[~df_temp['title'].str.lower().str.contains('saldo|pagamento', na=False)]
            frames[f.name] = df_temp
        except Exception:
            pass
    return frames

# Carregamento otimizado
all_data = load_all_data(tuple(csv_files))

if not all_data:
    st.error("Nenhum CSV válido encontrado")
    st.stop()

# Visão completa de todos os períodos
df_consolidated = pd.concat(all_data.values(), ignore_index=True)

# === FILE SELECTOR (Quick Fix 1: moved to top) ===
if len(csv_files) > 1:
    selected_file = st.selectbox(
        "Selecione o arquivo CSV:",
        csv_files,
        format_func=lambda x: x.name
    )
else:
    selected_file = csv_files[0]

try:
    # Recupera o DataFrame já processado do dicionário all_data
    df = all_data[selected_file.name]

    # Caption discreta com metadados do arquivo em vez de banner de sucesso (Quick Fix 3)
    df['date'] = pd.to_datetime(df['date'])
    min_date = df['date'].min().strftime('%d/%m/%Y')
    max_date = df['date'].max().strftime('%d/%m/%Y')
    st.caption(f"📅 {min_date} a {max_date} · {len(df)} transações · {selected_file.name}")

    # Layout de duas colunas: Esquerda (Gráfico de Composição), Direita (Métricas)
    col_left, col_right = st.columns([0.6, 0.4], gap="large")

    with col_right:
        st.subheader("📊 Resumo do Período")

        total_tx = len(df)
        valor_total = df['amount'].sum()
        ticket_medio = df['amount'].mean()
        top_cat = df.groupby('categoria')['amount'].sum().idxmax()

        st.metric("Transações", f"{total_tx}")
        st.metric("Valor Total", f"R$ {valor_total:,.2f}")
        st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
        st.metric("Maior Categoria", top_cat)
        
        outros_pct = (df['categoria'] == 'Outros').sum() / total_tx * 100 if total_tx > 0 else 0
        st.metric("% Outros", f"{outros_pct:.1f}%")

    with col_left:
        st.subheader("💸 Gastos por Categoria")
        render_donut(df)

    with st.expander("📋 Ver Dados"):
        edited_df = st.data_editor(
            df,
            column_config={
                "categoria": st.column_config.SelectboxColumn(
                    options=list(CATEGORY_COLORS.keys())
                )
            },
            use_container_width=True
        )

        changed_mask = df["categoria"] != edited_df["categoria"]
        if changed_mask.any():
            from classifier.engine import get_cache
            from utils.storage import save_cache
            from utils.normalize import normalize
            cache = get_cache()
            for _, row in edited_df[changed_mask].iterrows():
                desc = row.get('title', '') or row.get('description', '')
                normalized = normalize(str(desc))
                cache[normalized] = row["categoria"]
            save_cache(cache)
            load_all_data.clear()
            st.rerun()

except Exception as e:
    st.error(f"❌ Erro ao carregar o arquivo: {e}")

render_bar_history(df_consolidated)
