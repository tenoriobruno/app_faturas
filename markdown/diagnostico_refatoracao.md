# 🏗️ Diagnóstico Completo — Refatoração app_fatura

> Análise realizada em 02/05/2026. Codebase: 6 módulos Python, 1 CSS, 1 JSON de config, ~1.600 transações em 12 CSVs.

---

## INVENTÁRIO DO PROJETO

```
app.py              399 linhas  ← 170 são CSS inline, ~230 são lógica+gráficos
parsers/nubank.py    35 linhas  ← limpo, funcional
classifier/engine.py 24 linhas  ← simples demais (sem cache, sem AI)
classifier/local_rules.py 35 linhas ← funcional
utils/normalize.py   19 linhas  ← funcional
assets/styles.css    42 linhas  ← duplica CSS que já está inline no app.py
categories.json     127 linhas  ← 10 categorias, ~40 keywords
cache/               vazio     ← cache planejado mas nunca implementado
utils/storage.py     ausente   ← planejado no PLAN.md mas nunca criado
classifier/ai_classifier.py  ausente ← planejado mas nunca criado
```

**Total de código efetivo:** ~550 linhas (excluindo CSS inline).

---

## 1. PROBLEMAS ESTRUTURAIS

### 🔴 app.py é um monolito de 399 linhas com 3 responsabilidades misturadas

O arquivo faz tudo: define CSS (170 linhas), processa dados, e renderiza UI. Isso dificulta qualquer mudança — alterar um gráfico exige navegar por CSS, lógica de dados e Plotly config no mesmo arquivo.

**Refatoração proposta:**

```
app.py                  → ~80 linhas (orquestração pura)
config/theme.py         → CSS + CATEGORY_COLORS + PLOT_LAYOUT
config/constants.py     → DATA_DIR, caminhos, configurações
components/charts.py    → funções render_donut(), render_bar_history()
components/metrics.py   → função render_summary_cards()
components/data_table.py → função render_data_table()
```

### 🔴 Processamento duplicado: cada CSV é parseado e classificado 2x

O loop consolidado (linhas 190-198) processa **todos** os CSVs. Logo depois (linhas 248-251), o CSV selecionado é processado **novamente**. Com 12 CSVs e ~1.600 linhas totais, isso significa ~3.200 classificações por reload.

**Refatoração proposta:** Processar tudo uma vez e filtrar:

```python
# Processar todos uma vez
df_all = load_and_classify_all(csv_files)
df_consolidated = pd.concat(df_all.values(), ignore_index=True)

# Filtrar pelo selecionado
df = df_all[selected_file.name]
```

### 🔴 Cache planejado mas nunca implementado

O PLAN.md descreve `utils/storage.py` com cache em `cache/categories_cache.json`. O `engine.py` deveria consultar cache antes de classificar. Nada disso foi implementado — a pasta `cache/` está vazia e `storage.py` não existe. Cada reload reclassifica tudo do zero.

### 🟡 CSS existe em 2 lugares

- `app.py` linhas 10-178: CSS inline completo (170 linhas)
- `assets/styles.css`: 42 linhas de CSS que **nunca são carregadas** (não há `st.markdown` lendo esse arquivo)

O `styles.css` é código morto. O CSS inline polui o `app.py`.

### 🟡 AI classifier nunca foi implementado

O PLAN.md e CLAUDE.md descrevem `classifier/ai_classifier.py` com Claude Haiku como fallback. O arquivo não existe. Tudo que não casa com keyword/regex vai para "Outros" — e "Outros" representa **50.9%** das transações.

### 🟠 `categories.json` tem apenas ~40 keywords para classificar ~1.600 transações

Com apenas 40 keywords em 10 categorias, a cobertura é inevitavelmente baixa. O catch-all `"Outros"` com regex `".*"` garante que nada fica sem categoria, mas a metade das transações acaba nele.

### 🟠 Import não utilizado no parsers/nubank.py

`from pathlib import Path` é importado mas nunca usado.

### 🟠 Rename redundante no parsers/nubank.py

O rename mapeia `'date': 'date'`, `'title': 'title'`, `'amount': 'amount'` — identidades que não fazem nada.

---

## 2. REFATORAÇÃO PROPOSTA

### Fase 1: Separar responsabilidades do app.py

| Arquivo | Responsabilidade | Linhas estimadas |
|---------|-----------------|------------------|
| `app.py` | Orquestração, page config, layout | ~80 |
| `config/theme.py` | CSS string, CATEGORY_COLORS, PLOT_LAYOUT | ~180 |
| `components/charts.py` | `render_donut(df, colors)`, `render_bar_history(df, colors)` | ~120 |
| `components/metrics.py` | `render_summary(df)` | ~30 |
| `components/data_table.py` | `render_data_table(df)` | ~15 |

**Benefício:** Alterar qualquer gráfico sem tocar no CSS ou na lógica de dados.

### Fase 2: Implementar cache de classificação

```python
# utils/storage.py
import json
from pathlib import Path

CACHE_PATH = Path("cache/categories_cache.json")

def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}

def save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2))
```

```python
# classifier/engine.py (com cache)
from utils.storage import load_cache, save_cache

_cache = None

def get_cache():
    global _cache
    if _cache is None:
        _cache = load_cache()
    return _cache

def classify(description: str) -> str:
    normalized = normalize(description)
    cache = get_cache()
    if normalized in cache:
        return cache[normalized]
    result = classify_local(normalized) or "Outros"
    cache[normalized] = result
    save_cache(cache)
    return result
```

**Benefício:** Após primeira execução, classificações ficam instantâneas. Re-runs não reprocessam.

### Fase 3: Eliminar processamento duplicado

```python
# app.py — processar uma vez, usar duas vezes
@st.cache_data
def load_all_data(csv_files):
    frames = {}
    for f in csv_files:
        df = parse_nubank(str(f))
        df = classify_batch(df)
        df = df[~df['title'].str.lower().str.contains('saldo|pagamento', na=False)]
        frames[f.name] = df
    return frames

all_data = load_all_data(tuple(csv_files))
df_consolidated = pd.concat(all_data.values(), ignore_index=True)
df = all_data[selected_file.name]
```

**Benefício:** Processamento 50% mais rápido. `st.cache_data` evita reprocessar entre interações.

### Fase 4: Expandir categories.json

As categorias atuais cobrem ~50% das transações. Para chegar a ~85%:

| Categoria | Keywords faltando (exemplos comuns do Nubank) |
|-----------|----------------------------------------------|
| Compras | amazon, mercado livre, shopee, aliexpress, shein, magalu, americanas, casas bahia |
| Assinaturas | chatgpt, claude, openai, prime, globoplay, disney, hbo, max, paramount |
| Moradia | aluguel, condominio, energia, enel, sabesp, claro, vivo, tim, internet |
| Lazer | cinema, teatro, steam, playstation, xbox, academia, smartfit |
| Educação | udemy, coursera, alura, escola, faculdade, livraria |
| Viagem | booking, airbnb, latam, gol, azul, hotel, pousada, decolar |
| Delivery | rappi, zé delivery, aiqfome |
| Supermercado | atacadao, assai, big, dia, natural da terra |

**Benefício:** Reduzir "Outros" de 50% para ~15-20%.

---

## 3. FEATURES NOVAS (priorizadas por impacto/esforço)

### 🟢 Baixo esforço, alto impacto

#### F1: Edição manual de categoria com aprendizado

**O que faz:** Na tabela de dados, o usuário clica na categoria de uma transação e escolhe outra. A nova associação é salva no cache, e todas as transações futuras com a mesma descrição normalizada herdam a categoria.

**Por que importa:** Resolve o problema de "Outros" progressivamente. Após 2-3 meses de uso, o cache cobre 90%+ das transações.

**Esforço:** ~40 linhas. Trocar `st.dataframe` por `st.data_editor` com coluna `categoria` como selectbox.

```python
edited_df = st.data_editor(
    df,
    column_config={
        "categoria": st.column_config.SelectboxColumn(
            options=list(CATEGORY_COLORS.keys())
        )
    }
)
# Detectar mudanças e salvar no cache
```

---

#### F2: Comparação mês anterior (delta nos cards)

**O que faz:** Cada card de métrica mostra seta verde/vermelha comparando com o período anterior.

```
VALOR TOTAL           TICKET MÉDIO
R$ 4.028,05           R$ 31.72
▼ 12% vs anterior     ▲ 5% vs anterior
```

**Esforço:** ~20 linhas. O `st.metric` já suporta `delta`:

```python
st.metric("Valor Total", f"R$ {valor_total:,.2f}", delta=f"{pct_change:+.1f}%")
```

---

#### F3: Exportar CSV classificado

**O que faz:** Botão "📥 Exportar" gera CSV com as classificações aplicadas.

**Esforço:** ~5 linhas.

```python
st.download_button("📥 Exportar CSV", df.to_csv(index=False), "fatura_classificada.csv")
```

---

### 🟡 Médio esforço, alto impacto

#### F4: Top 5 maiores gastos do período

**O que faz:** Lista as 5 transações mais caras do mês, com nome e valor. Dá visibilidade imediata a gastos extraordinários.

**Esforço:** ~15 linhas. Exibir como subheader + markdown list ou mini-tabela.

---

#### F5: Meta de gasto mensal

**O que faz:** Usuário define um limite mensal (ex: R$ 4.000). O dashboard mostra uma barra de progresso visual indicando % consumido.

**Esforço:** ~25 linhas. `st.progress` customizado + valor no `config.json`.

```python
meta = 4000
pct = min(valor_total / meta, 1.0)
st.progress(pct, text=f"R$ {valor_total:,.0f} / R$ {meta:,.0f}")
```

---

#### F6: Tendência por categoria (sparklines)

**O que faz:** Ao lado de cada categoria no resumo, mostra mini-gráfico de tendência dos últimos 6 meses. O usuário vê "Delivery subiu 30% nos últimos 3 meses" sem precisar interpretar o gráfico de barras empilhadas.

**Esforço:** ~50 linhas. Plotly sparklines inline via `go.Scatter` minimalista.

---

### 🔴 Alto esforço, alto impacto

#### F7: AI Classifier (implementar o que falta do PLAN.md)

**O que faz:** Para transações que não casam com keyword/regex, envia para Claude Haiku classificar. Resultado é cacheado.

**Esforço:** ~60 linhas (classifier + prompt + error handling).

**Impacto:** Reduz "Outros" para <5% em vez de 50%.

---

#### F8: Multi-banco (parsers para Itaú, Bradesco, Inter)

**O que faz:** Além do Nubank, aceita CSVs de outros bancos. Cada parser normaliza para o mesmo formato.

**Esforço:** ~30 linhas por banco (parser específico).

---

## 4. PLANO DE EXECUÇÃO (ordem recomendada)

```
SPRINT 1 — Fundações (1 sessão)
├── [R1] Extrair CSS do app.py → config/theme.py
├── [R2] Extrair gráficos → components/charts.py
├── [R3] Implementar cache (utils/storage.py)
├── [R4] Eliminar processamento duplicado (@st.cache_data)
└── [R5] Limpar imports mortos e renames redundantes

SPRINT 2 — Classificação (1 sessão)
├── [F4] Expandir categories.json (~100 keywords)
├── [F1] st.data_editor com aprendizado
└── [R6] Monitorar % de "Outros" — meta: < 20%

SPRINT 3 — Features de valor (1 sessão)
├── [F2] Delta vs mês anterior nos cards
├── [F3] Botão exportar CSV
├── [F5] Top 5 maiores gastos
└── [F6] Meta de gasto mensal

SPRINT 4 — Avançado (opcional)
├── [F7] AI Classifier com Claude Haiku
├── [F8] Sparklines por categoria
└── [F9] Multi-banco
```

---

## 5. MÉTRICAS DE SUCESSO

| Métrica | Atual | Meta Sprint 2 | Meta Sprint 4 |
|---------|-------|---------------|---------------|
| % "Outros" | 50.9% | < 20% | < 5% |
| Linhas no app.py | 399 | < 100 | < 100 |
| Tempo de reload | ~3s (estimado) | < 1s (cache) | < 1s |
| Features planejadas implementadas | 3/10 do PLAN.md | 6/10 | 10/10 |
| Cache hit rate | 0% (não existe) | > 60% | > 85% |

---

## 6. DÍVIDAS TÉCNICAS

| Dívida | Onde | Severidade |
|--------|------|------------|
| CSS inline + CSS externo morto | app.py + assets/styles.css | Média |
| Processamento 2x por CSV | app.py linhas 190-198 + 248-251 | Alta |
| Cache inexistente | engine.py, storage.py ausente | Alta |
| AI classifier inexistente | classifier/ai_classifier.py ausente | Média |
| Import não usado | parsers/nubank.py (`Path`) | Baixa |
| Rename identidade | parsers/nubank.py (`'date': 'date'`) | Baixa |
| `month_order` reutilizado como nome de variável | app.py linhas 328 e 340 | Baixa |
| Sem `@st.cache_data` | app.py (reprocessa a cada interação) | Alta |
| Estornos não são filtrados (só amount > 0) | parsers/nubank.py | Média |
| `.stSuccess` CSS órfão (banner removido) | app.py linhas 170-176 | Baixa |
