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

st.sidebar.header("📁 Upload de Faturas")
uploaded_file = st.sidebar.file_uploader("Novo arquivo Nubank (.csv)", type=["csv"])
if uploaded_file is not None:
    file_path = DATA_DIR / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"Arquivo {uploaded_file.name} salvo!")
    st.cache_data.clear()
    st.rerun()

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
            frames[f.name] = df_temp
        except Exception as e:
            # Captura log seguro e limpo
            from utils.logger import get_logger
            get_logger(__name__).error(f"Erro ao carregar {f.name}: {e}")
    return frames

# Carregamento otimizado
all_data = load_all_data(tuple(csv_files))

if not all_data:
    st.error("Nenhum CSV válido encontrado")
    st.stop()

# Visão completa de todos os períodos
df_consolidated = pd.concat(all_data.values(), ignore_index=True)

# === FILE SELECTOR ===
if len(csv_files) > 1:
    selected_file = st.sidebar.selectbox(
        "Selecione o arquivo CSV:",
        csv_files,
        format_func=lambda x: x.name
    )
else:
    selected_file = csv_files[0]

try:
    # Recupera o DataFrame já processado do dicionário all_data
    df = all_data[selected_file.name]

    # Aplica filtros da sidebar
    from components.sidebar import render_sidebar
    df['date'] = pd.to_datetime(df['date'])
    df = render_sidebar(df, list(CATEGORY_COLORS.keys()))

    from utils.export import render_export_button
    st.sidebar.divider()
    render_export_button(df, filename=f"faturas_{selected_file.name}")

    # Caption discreta com metadados do arquivo em vez de banner de sucesso (Quick Fix 3)
    if len(df) > 0:
        min_date = df['date'].min().strftime('%d/%m/%Y')
        max_date = df['date'].max().strftime('%d/%m/%Y')
        st.caption(f"📅 {min_date} a {max_date} · {len(df)} transações · {selected_file.name}")
    else:
        st.caption(f"Nenhuma transação encontrada com os filtros atuais.")

    tabs = st.tabs(["Visão Geral", "Transações", "Recorrências", "Parcelas Futuras"])
    
    with tabs[0]:
        # Layout de duas colunas: Esquerda (Gráfico de Composição), Direita (Métricas)
        col_left, col_right = st.columns([0.6, 0.4], gap="large")

        with col_right:
            st.subheader("📊 Resumo do Período")

            # Busca o CSV anterior cronologicamente para calcular o Delta
            prev_df = None
            try:
                idx = csv_files.index(selected_file)
                if idx + 1 < len(csv_files):
                    prev_file = csv_files[idx + 1]
                    prev_df = all_data[prev_file.name]
            except ValueError:
                pass

            df_gastos = df[df['tipo_transacao'] == 'gasto']
            total_tx = len(df_gastos)
            valor_total = df_gastos['amount'].sum() if total_tx > 0 else 0
            ticket_medio = df_gastos['amount'].mean() if total_tx > 0 else 0
            top_cat = df_gastos.groupby('categoria')['amount'].sum().idxmax() if total_tx > 0 else "N/A"

            delta_tx, delta_valor, delta_ticket = None, None, None
            if prev_df is not None:
                prev_gastos = prev_df[prev_df['tipo_transacao'] == 'gasto']
                prev_tx = len(prev_gastos)
                prev_valor = prev_gastos['amount'].sum() if prev_tx > 0 else 0
                prev_ticket = prev_gastos['amount'].mean() if prev_tx > 0 else 0
                
                delta_tx = total_tx - prev_tx
                delta_valor = valor_total - prev_valor
                delta_ticket = ticket_medio - prev_ticket

            st.metric("Transações (Gastos)", f"{total_tx}", delta=f"{delta_tx}" if delta_tx is not None else None, delta_color="normal")
            st.metric("Valor Total", f"R$ {valor_total:,.2f}", delta=f"R$ {delta_valor:,.2f}" if delta_valor is not None else None, delta_color="inverse")
            st.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}", delta=f"R$ {delta_ticket:,.2f}" if delta_ticket is not None else None, delta_color="inverse")
            st.metric("Maior Categoria", top_cat)
            
            outros_pct = (df['categoria'] == 'Outros').sum() / len(df) * 100 if len(df) > 0 else 0
            st.metric("% Não-classificado", f"{outros_pct:.1f}%")

        with col_left:
            st.subheader("💸 Gastos por Categoria")
            render_donut(df_gastos)

        st.divider()
        from components.budget import render_budget
        render_budget(df)
        st.divider()
        render_bar_history(df_consolidated)

    with tabs[1]:
        st.subheader("📋 Ver Dados Brutos")
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

    with tabs[2]:
        from analysis.recurrences import render_recurrences
        render_recurrences(df_consolidated)

    with tabs[3]:
        from analysis.installments import render_installments
        render_installments(df_consolidated)

except Exception as e:
    st.error(f"❌ Erro ao carregar a interface: {e}")
