# Plano Resumido — app_faturas

Ordem S1→S8. Ambíguo=pare. Python 3.11, `pathlib.Path`, `utf-8`, keys únicos, nunca `except: pass`.

**Árvore:** `app.py` + `classifier/{engine,local_rules,ai_classifier}.py` + `parsers/nubank.py` + `utils/{normalize,storage,filters,loader,logger}.py` + `components/{charts,budget}.py` + `analysis/{recurrences,metrics,installments}.py` + `views/{overview,transactions,recurrences,installments}.py` + `config/{theme,settings}.py` + `tests/*` + `cache/categories_cache.json` + `categories.json` + `budget.json` + `.env`(DATA_PATH, ANTHROPIC_API_KEY).

---

## S1 — Fix bugs

- `engine.py`: remover `save_cache()` de `classify()`. `classify_batch` salva 1x ao final se `len(cache)` aumentou (`before=len(get_cache())` antes/depois apply).
- `categories.json`: `"Outros"→{"keywords":[],"regex":[]}`.
- `parsers/nubank.py`: não filtrar `amount>0`. `tipo_transacao`: `>0→gasto`, `<0→estorno`, `==0→ajuste`. Remover só `ajuste` AND title `~r'saldo|pagamento'`. Ordem: ler→renomear→validar→to_numeric→tipo_transacao→filtrar ajustes→dedup(date,title,amount)→col categoria. Return `[date,title,amount,tipo_transacao,categoria]`.
- `app.py` log: `logging.basicConfig(level=WARNING, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')`. `except: pass`→`log.warning(...); continue`.
- `app.py` try global: remover linhas 69-128. `if name not in all_data: st.error; st.stop; df=all_data[name]`.
- **Validar:** app roda, cache escrito 1x, estornos visíveis.

---

## S2 — AI Classifier

### `classifier/ai_classifier.py` (novo)

`classify_ai_batch(descriptions, available_categories)→list[str]`. Vazio→`[]`. `len>20`→chunks 20 recursivo. Anthropic `"claude-haiku-3-5-20251001"`, `max_tokens=500`, `temperature=0`. Parse: strip, remover ` ``` ` e ` ```json ` fences, `json.loads`, validar `list[str]`. Inválido→`"Outros"`. Len errado→preencher+warning.

**System:** `Classificador transações BR. APENAS JSON array strings, mesma ordem.`  
**User:** `Categorias: {cats}\nTransações:\n1. {d1}\n...\nResponda JSON array de N.`

### `engine.py`

```python
def classify_local_only(description):
    n = normalize(description)
    if not n: return None, None
    c = get_cache()
    if n in c: return c[n]["categoria"], n
    return classify_local(n), n
```

Nova `classify_batch`: `classify_local_only` em mask. `None`→`to_ai_list`. Não-vazio E `ANTHROPIC_API_KEY`: `ratio=len(to_ai)/len(df)`, `>0.15`→warning mas segue.

### `utils/storage.py` cache com source

`{"uber trip":{"categoria":"Transporte","source":"local"}}`. `load_cache()` migra str→dict. Leituras `cache[k]["categoria"]`. Source∈`{local,ai,user}`. Edit tabela→`user`.

**Validar:** cache tem `source`, ratio<15%, edit marca `user`.

---

## S3 — Sidebar + filtros

### `app.py` sidebar (carregar df antes)

```python
with st.sidebar:
    selected_file = st.selectbox("Fatura", csv_files, format_func=lambda x: x.name, key="csv")
    cats = st.multiselect("Categorias", all_cats, default=all_cats, key="cat")
    amt = st.slider("Faixa R$", min_v, max_v, (min_v,max_v), key="amt")
    dates = st.date_input("Período", (d_min,d_max), key="date")
    tipos = st.multiselect("Tipo", ["gasto","estorno"], default=["gasto"], key="tipo")
    search = st.text_input("Buscar", key="search")
    hide_o = st.checkbox("Ocultar Outros", key="hide")
    only_o = st.checkbox("Só Outros", key="only")
```

### `utils/filters.py` (novo)

```python
def apply_filters(df, cats, amount_range, date_range, tipos, search, hide_outros, only_outros):
    out = df.copy()
    out = out[out['categoria'].isin(cats)]
    out = out[(out['amount']>=amount_range[0]) & (out['amount']<=amount_range[1])]
    if len(date_range)==2:
        out = out[(out['date'].dt.date>=date_range[0]) & (out['date'].dt.date<=date_range[1])]
    out = out[out['tipo_transacao'].isin(tipos)]
    if search: out = out[out['title'].str.contains(search, case=False, na=False)]
    if hide_outros: out = out[out['categoria']!='Outros']
    if only_outros: out = out[out['categoria']=='Outros']
    return out
```

Remover seletor antigo. `df_filtered` em tudo. `render_bar_history` filtra só cats+tipos.

### `theme.py` CSS: sidebar bg `#FFF`, h3 uppercase `.85rem` `#8A92A6`.

**Validar:** sidebar reage.

---

## S4 — Recorrências

### `analysis/recurrences.py` (novo)

`detect_recurrences(df)→DataFrame` cols `normalized_title|count|avg|min|max|categoria|last_date|predicted_next_date|status`.

Algoritmo: `normalize(title)`→`normalized_title`. Filtrar `tipo=="gasto"`. Groupby: count, avg/min/max, `variance_pct=(max-min)/avg*100`, categoria=mode, last_date=max, `date_diffs`=diffs consecutivos. Recorrente se `count>=3` AND `variance_pct<=10` AND `mean(diffs)∈[25,35]` AND `std(diffs)<=5`. `predicted>=today-7d` → `"ativa"`, senão `"inativa"`.

### `app.py` 3 abas

`st.tabs(["Visão Geral","Transações","Recorrentes"])`. Aba rec: `st.metric("Custo mensal", sum(avg))` + `st.dataframe`. `R$ X,XX`, `DD/MM/YYYY`, status via `column_config`.

**Validar:** Netflix/Spotify "ativa", predicted~30d.

---

## S5 — Orçamento

`budget.json` raiz: `{"Delivery":500,...,"Gasolina":300}` (14 cats placeholder).

### `storage.py`

```python
BUDGET_PATH = Path("budget.json")
def load_budget(): return json.loads(BUDGET_PATH.read_text(encoding='utf-8')) if BUDGET_PATH.exists() else {}
def save_budget(b): BUDGET_PATH.write_text(json.dumps(b, ensure_ascii=False, indent=2), encoding='utf-8')
```

### `components/budget.py` (novo)

```python
def render_budget_section(df):
    budget = load_budget()
    if not budget: st.info("Defina abaixo.")
    spend = df.groupby('categoria')['amount'].sum().to_dict()
    st.subheader("Orçamento do mês")
    for cat, limit in sorted(budget.items()):
        spent = spend.get(cat, 0.0)
        pct = min(spent/limit, 1.0) if limit>0 else 0
        color = "#E74C3C" if pct>=1.0 else "#2ECC71"
        c1,c2,c3 = st.columns([2,5,2])
        c1.text(cat)
        c2.markdown(
            f'<div style="background:#e0e0e0;border-radius:10px">'
            f'<div style="width:{pct*100}%;background:{color};height:14px;border-radius:10px"></div></div>',
            unsafe_allow_html=True
        )
        c3.text(f"R$ {spent:,.0f} / R$ {limit:,.0f}")
    with st.expander("Editar"):
        edits = {c: st.number_input(c, 0.0, value=float(v), step=50.0, key=f"b_{c}") for c,v in budget.items()}
        if st.button("Salvar"): save_budget(edits); st.success("Salvo."); st.rerun()
```

Chamar em Visão Geral abaixo dos KPIs. **Validar:** persiste, vermelho se estoura.

---

## S6 — KPIs delta + média móvel

### `app.py` `col_right`

```python
total_tx = len(df_filtered)
gastos = df_filtered[df_filtered['tipo_transacao']=='gasto']
valor = gastos['amount'].sum()
ticket = gastos['amount'].mean() or 0
d_t = compute_delta_vs_previous(df_c, selected_file.name, 'amount_sum')
d_n = compute_delta_vs_previous(df_c, selected_file.name, 'count')
pct_o = (df_filtered['categoria']=='Outros').sum()/total_tx*100 if total_tx else 0
st.metric("Transações", total_tx, delta=f"{d_n:+.0f}" if d_n else None)
st.metric("Valor Total", f"R$ {valor:,.2f}", delta=f"R$ {d_t:+,.2f}" if d_t else None)
st.metric("Ticket Médio", f"R$ {ticket:,.2f}")
st.metric("% Não-classificado", f"{pct_o:.1f}%")
```

### `analysis/metrics.py` (novo)

```python
def compute_delta_vs_previous(df_c, filename, metric):
    df = df_c.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    m = re.search(r'(\d{4})-(\d{2})-\d{2}', filename)
    if not m: return None
    cur = pd.Period(f"{m.group(1)}-{m.group(2)}", freq='M')
    prev = cur - 1
    c, p = df[df['month']==cur], df[df['month']==prev]
    if p.empty: return None
    if metric=='amount_sum': return c['amount'].sum() - p['amount'].sum()
    if metric=='count': return len(c) - len(p)
```

### `charts.py`

Antes de `st.plotly_chart` adicionar Scatter: `rolling = monthly_totals.rolling(3, min_periods=1).mean()` com `line=dict(color='#1A1D23', width=2, dash='dot')`, name `'Média móvel 3m'`.

**Validar:** delta exibido só se mês anterior existe.

---

## S7 — Parcelas

### `utils/normalize.py`

```python
def extract_installment(text):
    if not isinstance(text, str): return text, None, None
    m = re.search(r'\b(\d{1,2})/(\d{1,2})\b', text)
    if not m: return text, None, None
    cur, total = int(m.group(1)), int(m.group(2))
    if total<=1 or cur>total or total>24: return text, None, None
    cleaned = re.sub(r'\s+', ' ', re.sub(r'\b\d{1,2}/\d{1,2}\b', '', text)).strip()
    return cleaned, cur, total
```

### `parsers/nubank.py`

Após dedup: aplicar `extract_installment` em `title`, criar colunas `title_clean`, `parcela_atual`, `parcela_total`, `is_parcelada=parcela_total.notna()`. Return inclui todas.

### `analysis/installments.py` (novo)

```python
def group_installments(df_c):
    df = df_c[df_c['is_parcelada']].copy()
    if df.empty: return pd.DataFrame()
    g = df.groupby(['title_clean','amount','parcela_total']).agg(
        pagas=('parcela_atual','nunique'),
        primeira=('date','min'),
        ultima=('date','max'),
        categoria=('categoria', lambda x: x.mode().iloc[0] if not x.mode().empty else 'Outros')
    ).reset_index()
    g['restantes'] = g['parcela_total'] - g['pagas']
    g['total_compra'] = g['amount'] * g['parcela_total']
    g['valor_pendente'] = g['amount'] * g['restantes']
    return g.sort_values('valor_pendente', ascending=False)
```

### `app.py` aba Parcelas

Metric `gasto futuro travado`, loop `st.progress(pagas/total)` + caption.

**Validar:** agrupadas, `pagas` incrementa.

---

## S8 — Refactor + testes + views

- `config/settings.py` → `class Settings`: `ROOT_DIR, DATA_PATH, CACHE_PATH, BUDGET_PATH, CATEGORIES_PATH, ANTHROPIC_API_KEY, AI_MODEL="claude-haiku-3-5-20251001", AI_MAX_TOKENS=500, AI_BATCH_SIZE=20, AI_MAX_RATIO=0.15, LOG_LEVEL`. `settings=Settings()`. Substituir paths hardcoded.
- `utils/logger.py` → `get_logger(name)` com StreamHandler format `'%(asctime)s [%(levelname)s] %(name)s: %(message)s'`, level `settings.LOG_LEVEL`. `st.error` só user-facing.
- Testes (`pytest>=8.0.0`):
  - `test_normalize`: uber→`"uber trip"`, `ifood*pedido`, `mercpago*loja123`, `01/12` removida, `""/None`.
  - `test_installment`: Netflix `01/12→(N,1,12)`, Uber→None, `len==3` dedup, 1 estorno.
  - `test_nubank_parser`: `fixtures/sample.csv` (4 linhas: 2 uber iguais, 1 ifood, 1 estorno -45), `len==3` dedup, 1 estorno.
  - Rodar: `pytest tests/ -v`.
- Views `views/{overview,transactions,recurrences,installments}.py` com `render(...)` migrando abas sem mudar comportamento.
- `utils/loader.py`: `@st.cache_data def load_all_data(csv_paths)` → dict `{name: classify_batch(parse_nubank(path))}`, `except` loga e segue.
- `app.py` reduzido:

```python
import streamlit as st, pandas as pd
from config.theme import CSS
from config.settings import settings
from utils.loader import load_all_data
from utils.filters import apply_filters, render_sidebar_filters
from views import overview, transactions, recurrences, installments

st.set_page_config(page_title="Finanças", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.title("Finanças Pessoais")

csv_files = sorted(list(settings.DATA_PATH.glob("*.csv")), reverse=True)
if not csv_files: st.info("Nenhum CSV"); st.stop()

all_data = load_all_data(tuple(sorted(str(f) for f in csv_files)))
if not all_data: st.error("Nenhum válido"); st.stop()

df_c = pd.concat(all_data.values(), ignore_index=True)
selected_file, filters = render_sidebar_filters(csv_files, df_c)
df_f = apply_filters(all_data[selected_file.name], **filters)

tabs = st.tabs(["Visão Geral","Transações","Recorrentes","Parcelas"])
with tabs[0]: overview.render(df_f, df_c, selected_file)
with tabs[1]: transactions.render(df_f)
with tabs[2]: recurrences.render(df_c)
with tabs[3]: installments.render(df_c)
```

`render_sidebar_filters` em `utils/filters.py` retorna `(selected_file, filters_dict)`.

**Validar:** `pytest -v` verde, app roda, `.env` ausente→`st.error`, `app.py`<50 linhas.

---

## Checklist final

- S1 — bugs corrigidos
- S2 — AI + source + ratio<15%
- S3 — 6 filtros no sidebar
- S4 — Netflix "ativa", predicted~30d
- S5 — budget persiste, vermelho se estoura
- S6 — delta + média móvel 3m
- S7 — parcelas agrupadas, progress bar
- S8 — testes verdes + app<50 linhas

**Report por seção:** `Seção N | Status | Arquivos alterados | Testes X/Y | Problemas`

> Nota: `settings.py` e `logger.py` podem entrar já na S1.
