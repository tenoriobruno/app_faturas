# Diagnóstico Técnico — app_faturas

> **Gerado em:** 06/06/2026 | **Analista:** Senior Code Architect Mode  
> **Premissa de leitura:** Este documento foi escrito para um desenvolvedor com **zero contexto** sobre o projeto. Cada referência de arquivo usa o caminho completo a partir da raiz do repositório. Cada item é auto-explicativo.

---

## Contexto do Projeto (leia isto primeiro)

O `app_faturas` é um **dashboard financeiro pessoal** escrito em Python usando o framework **Streamlit**. Ele não é um SaaS — é de uso exclusivamente pessoal. O objetivo principal é:

1. Receber exportações de fatura em `.csv` do Nubank (cartão de crédito)  
2. Classificar automaticamente as transações em categorias (Delivery, Transporte, Supermercado, etc.)  
3. Exibir gráficos, métricas e projeções de parcelas futuras em um dashboard web

**Stack:** Python 3.11+, Streamlit 1.31.1, Pandas 2.1.3, Plotly 5.17.0, python-dotenv 1.0.0  
**Ponto de entrada:** `app.py` — comando de execução: `streamlit run app.py`

---

## 1. Architecture State — Estado atual da arquitetura e acoplamento

### 1.1 Visão geral

O projeto segue uma **arquitetura em camadas bem definida no papel**, mas com **acoplamento direto excessivo na prática**:

```
CSV do Nubank
    │
    ▼
parsers/nubank.py          ← Parsing + limpeza + extração de parcelas (3 responsabilidades)
    │
    ▼
classifier/engine.py       ← Orquestra: normalize → cache lookup → local_rules → fallback
    │         │
    │    classifier/local_rules.py   ← Keyword + regex match contra categories.json
    │         │
    │    data/repository.py          ← Lê e escreve cache JSON
    │
    ▼
app.py                     ← Entry point Streamlit: wiring + lógica de negócio inline + UI
    │
    ├── views/overview.py        ← Cálculo de métricas + renderização
    ├── views/transactions.py    ← Edição + persistência de cache + renderização
    ├── views/recurrences.py     ← Renderização
    ├── views/installments.py    ← Cálculo + renderização + Plotly inline
    │
    ├── components/charts.py     ← Gráficos Plotly
    ├── components/budget.py     ← Cálculo de orçamento + edição + persistência + renderização
    ├── components/sidebar.py    ← Filtros
    ├── components/metrics.py    ← Card de métrica HTML
    ├── components/header.py     ← Header + toggle dark mode
    │
    ├── core/installments.py     ← Pure logic: calcula parcelas futuras
    ├── core/recurrences.py      ← Pure logic: detecta recorrências
    │
    ├── utils/normalize.py       ← Normalização de texto
    ├── utils/filters.py         ← Filtro de DataFrame
    ├── utils/export.py          ← Download CSV
    └── utils/logger.py          ← Logger
```

### 1.2 Problemas de acoplamento identificados

#### A. `app.py` é um Coordenador-Deus
**Arquivo:** `app.py` (102 linhas)

`app.py` deveria ser apenas o entry point do Streamlit, mas acumula:
- Lógica de invalidação de cache (linhas 27–34): verifica `st_mtime` do `categories.json` vs `cache_path`
- Upload e persistência de arquivos no disco (linhas 39–43)
- Carregamento e consolidação de todos os CSVs (linhas 45–67)
- Seleção do arquivo ativo (linha 69)
- Conversão de tipo da coluna `date` (linha 71)
- Orquestração das views e componentes

Qualquer alteração na lógica de loading/cache implica mudar o entry point.

#### B. `views/transactions.py` conhece o repositório de cache
**Arquivo:** `views/transactions.py` (linhas 37–43)

Uma view (camada de apresentação) importa diretamente `data/repository.py` e `utils/normalize.py` para persistir edições manuais de categoria no cache. Uma view **nunca deveria escrever em repositórios diretamente** — isso é responsabilidade da camada de negócio.

#### C. `views/overview.py` calcula métricas de negócio
**Arquivo:** `views/overview.py` (linhas 29–44)

A view calcula `total_tx`, `valor_total`, `ticket_medio`, `top_cat`, `delta_tx`, `delta_valor`, etc. — lógica puramente analítica que pertence a uma função de serviço/core, não a uma view.

#### D. `components/budget.py` faz 3 coisas ao mesmo tempo
**Arquivo:** `components/budget.py` (70 linhas)

Lê orçamento do repositório, calcula percentuais, renderiza barras de progresso HTML, **e** contém o formulário de edição com `st.number_input` e `budget_repo.save()`. Um único componente faz: apresentação + cálculo + persistência.

#### E. Import tardio dentro de função cacheada
**Arquivo:** `app.py` (linha 58)

```python
@st.cache_data
def load_all_data(files):
    ...
    from utils.logger import get_logger  # ← import dentro da função
```

Import dentro de função viola o princípio de legibilidade e pode causar comportamento inesperado quando a função é cacheada pelo Streamlit entre reruns.

#### F. `classifier/local_rules.py` lê o arquivo JSON a cada chamada
**Arquivo:** `classifier/local_rules.py` (linhas 10–13 e 27)

`classify_local()` chama `load_categories()` em cada invocação individual. Em um batch de N transações, o arquivo `categories.json` é lido N vezes do disco. O `classify_batch()` em `engine.py` já poderia passar o dict carregado uma vez.

#### G. Cache global mutável em módulo de classificação
**Arquivo:** `classifier/engine.py` (linhas 11–17)

```python
_cache = None

def get_cache():
    global _cache
    if _cache is None:
        _cache = cache_repo.load()
    return _cache
```

Este singleton mutable em nível de módulo (`_cache`) é problemático com o Streamlit, que pode reusar workers entre sessões. O cache carregado numa sessão pode vazar dados entre reruns de forma não determinística.

---

## 2. Dead Code — Arquivos e linhas exatas de código morto

### 2.1 `components/ui/` — Diretório inteiro é dead code

**Arquivos:**
- `components/ui/__init__.py`
- `components/ui/components.py`

**Evidência:** `components/ui/components.py` define três wrappers `Button`, `Input`, `Selectbox` que são thin wrappers sobre `st.button`, `st.text_input`, `st.selectbox` sem nenhuma lógica adicional. **Nenhum arquivo no projeto importa esse módulo.** O `RESUMO_FASE1.md` cita sua criação como entrega da Fase 1, mas os componentes nunca foram integrados.

**Como verificar:** Rode `grep -r "from components.ui" .` e `grep -r "import components.ui" .` — retorna vazio.

### 2.2 `config/settings.py` — Atributo `GEMINI_API_KEY` nunca usado

**Arquivo:** `config/settings.py` (linha 16)

```python
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
```

O projeto tem `google-generativeai==0.8.3` no `requirements.txt`, mas **nenhum arquivo importa ou usa `GEMINI_API_KEY`** ou qualquer módulo do `google.generativeai`. O comentário em `classifier/engine.py` linha 60 confirma: `# Fallback para categoria indeterminada (LLM desativado)`. A integração AI foi removida mas o atributo e a dependência ficaram.

**Impacto:** Dependência fantasma no `requirements.txt` aumenta o tamanho do ambiente desnecessariamente (~50MB do pacote `google-generativeai`).

### 2.3 `requirements.txt` — Dependência morta

**Arquivo:** `requirements.txt` (linha 5)

```
google-generativeai==0.8.3
```

Consequência direta do item 2.2. Esta dependência nunca é importada em nenhum arquivo Python do projeto.

### 2.4 `categories.json` — Categoria "Outros" com regex `.*` é morta e perigosa

**Arquivo:** `categories.json` (linhas 221–226)

```json
"Outros": {
    "keywords": [],
    "regex": [".*"]
}
```

O regex `.*` casa com **qualquer string**, o que faria toda transação cair em "Outros" se o código de `local_rules.py` chegasse até essa categoria. No entanto, `classify_local()` em `classifier/local_rules.py` (linha 42) retorna `None` quando nenhuma outra regra casa, e o fallback para "Outros" é aplicado no `engine.py` (linha 61–63). O regex `.*` em `categories.json` nunca é alcançado na prática porque o código aplica o fallback antes de checar a categoria "Outros". É código morto e confuso.

### 2.5 `config/settings.py` — Atributo `DEFAULT_DARK_MODE` não é configurável por env

**Arquivo:** `config/settings.py` (linha 14)

```python
DEFAULT_DARK_MODE = False
```

Este valor está hardcoded e não lê nenhuma variável de ambiente. O único uso é em `components/header.py` linha 13. Se um usuário quiser o dark mode como padrão permanente, não há como configurar via `.env`. A settings class tem o padrão de usar `os.getenv()` para outras variáveis mas não para esta.

### 2.6 Arquivos de planejamento na raiz e em `markdown/` — Não são código, mas são ruído

**Arquivos:**
- `novo_plano_gpt.md` (raiz)
- `prompt_qwen3.md` (raiz)
- `markdown/PLAN.md`
- `markdown/Status.md`
- `markdown/agy_frontend-designer.md`
- `markdown/ajuste_grafico_rosca.md`
- `markdown/diagnostico_dashboard.md`
- `markdown/diagnostico_refatoracao.md`
- `markdown/fase1_planejamento.md`
- `markdown/fase2_execucao.md`
- `markdown/implementation_plan.md`
- `markdown/implementation_plan_pt.md`
- `markdown/novo_plano_claude.md`
- `markdown/novo_plano_pro.md`
- `markdown/plano_antigravity.md`
- `markdown/plano_antigravity_claude.md`
- `markdown/plano_arquitetura_e_clean_code.md`
- `markdown/plano_arquitetura_e_clean_code_2.0.md`
- `markdown/plano_claude.md`
- `markdown/plano_designer.md`
- `markdown/task.md`
- `markdown/top5_ollama.md`
- `RESUMO_FASE1.md` (raiz)

São **22 arquivos Markdown** de planejamento/diagnóstico acumulados de sessões anteriores com diferentes agentes AI. Poluem o repositório, confundem git blame e ocupam espaço. Deveriam estar em um branch separado ou em uma pasta `docs/archive/` com `.gitignore`.

---

## 3. Wrong Responsibilities — Funções fazendo o que não deveriam

### 3.1 `parsers/nubank.py` — Parser que também extrai parcelas

**Arquivo:** `parsers/nubank.py` (linhas 63–75)

Um parser tem uma única responsabilidade: **ler um formato de arquivo e retornar dados estruturados**. O `parse_nubank()` vai além:

- Lê e decodifica o CSV ✅ (correto)
- Renomeia colunas ✅ (correto)
- Classifica tipo de transação (`gasto/estorno/ajuste`) — lógica de negócio ❌
- Filtra transações de pagamento de fatura (`mask_pagamento`) — lógica de negócio ❌
- Extrai e valida informações de parcelamento (`01/12`) — lógica de negócio ❌

As últimas três responsabilidades pertencem a `core/` ou a uma função de pipeline separada. Se um dia o Nubank mudar o formato de parcelas, será necessário modificar o parser, misturando preocupações.

### 3.2 `views/transactions.py` — View que persiste dados

**Arquivo:** `views/transactions.py` (linhas 36–46)

```python
if not df_display.equals(edited_df):
    cache = cache_repo.load()
    diff = edited_df[df_display['categoria'] != edited_df['categoria']]
    for _, row in diff.iterrows():
        norm_title = normalize(row['title'])
        if norm_title:
            cache[norm_title] = {"categoria": row['categoria'], "source": "user"}
    cache_repo.save(cache)
    ...
    load_all_data_func.clear()
    st.rerun()
```

A view: (1) detecta diff, (2) normaliza texto, (3) constrói entradas de cache, (4) salva no repositório, (5) limpa o cache do Streamlit, (6) força rerun. Isso é lógica de serviço completa dentro de uma view. A view deveria apenas chamar algo como `classification_service.save_manual_corrections(diff)`.

### 3.3 `views/installments.py` — View que calcula saldo devedor e cria gráfico Plotly inline

**Arquivo:** `views/installments.py` (linhas 26–43 e 60–86)

O loop nas linhas 29–43 calcula `total_remaining_debt` e monta `future_data` — isso é lógica de negócio pura que pertence a `core/installments.py`. A função `calculate_future_installments()` em `core/installments.py` retorna apenas a lista de parcelas, mas **toda a projeção mensal de impacto financeiro** é computada na view.

Além disso, a view contém definição completa de um gráfico Plotly (linhas 70–84) com cores hardcoded (`#EF4444`), sem usar `CATEGORY_COLORS` nem `get_plotly_layout` corretamente (usa `get_plotly_layout` mas ignora a cor da barra).

### 3.4 `components/budget.py` — Componente que é repositório + calculadora + formulário

**Arquivo:** `components/budget.py` (70 linhas completas)

- Linhas 8–14: lê do repositório (`budget_repo.load()`)
- Linhas 16–47: calcula percentuais e renderiza barras
- Linhas 49–69: contém formulário completo de edição com `st.number_input` e escreve no repositório (`budget_repo.save()`)

Um componente de apresentação (`render_budget`) nunca deveria conter lógica de persistência. O formulário de edição deveria ser uma view separada ou pelo menos uma função separada.

### 3.5 `components/header.py` — Gerencia estado global da aplicação

**Arquivo:** `components/header.py` (linhas 12–26)

O header inicializa e modifica `st.session_state.dark_mode`, que é um estado **global** da aplicação. Um componente de header não deveria ser responsável pela inicialização de estado global. Isso pertence ao entry point (`app.py`) ou a um módulo de gerenciamento de estado.

### 3.6 `classifier/engine.py` — Orquestrador que gerencia um singleton de cache mutable

**Arquivo:** `classifier/engine.py` (linhas 11–17)

O engine de classificação gerencia um cache em memória via variável global `_cache`. Este padrão singleton-em-módulo é frágil no Streamlit (ver seção 1.2.G) e mistura responsabilidade de classificação com gerenciamento de estado de sessão.

---

## 4. Code Smells — Classes Deus, Deep Nesting, Feature Envy

### 4.1 God Class: `config/theme.py`

**Arquivo:** `config/theme.py` (631 linhas)

`theme.py` é o maior arquivo do projeto e acumula responsabilidades:
- Função `apply_theme()` (linhas 5–9): aplica CSS via `st.markdown`
- Constante `CSS` (linhas 12–387): **375 linhas** de CSS inline como string Python — inclui reset, tipografia, glassmorphism, tabs, sidebar, inputs, sliders, checkboxes, file uploader, botões, tabela, responsividade
- Constante `CSS_DARK` (linhas 389–565): **176 linhas** de CSS para dark mode — duplica todas as variáveis CSS redefinindo o `:root`
- Constante `CATEGORY_COLORS` (linhas 568–586): mapa de cores por categoria — dado de domínio, não de tema
- Função `get_plotly_layout()` (linhas 588–631): retorna dict de layout Plotly para light/dark — lógica de configuração de gráficos

**Problema crítico:** `CATEGORY_COLORS` é importado por `app.py` (linha 18), `components/charts.py` (linha 4) e `components/sidebar.py` (indiretamente via `CATEGORY_COLORS.keys()`). Dado de domínio (categorias e cores) está acoplado ao módulo de tema visual.

### 4.2 Deep Nesting: `components/charts.py` — render_bar_history

**Arquivo:** `components/charts.py` (linhas 70–96)

```python
for month in monthly_pivot.index:           # nível 1
    month_values = monthly_pivot.loc[month]
    cat_order = month_values.sort_values(ascending=False).index
    for category in cat_order:              # nível 2
        val = month_values.get(category, 0)
        pct = 0
        if monthly_totals.loc[month] ...:   # nível 3
            pct = round(...)
        text_label = ...
        showlegend = category not in seen_legend
        if showlegend:                      # nível 3
            seen_legend.add(category)
        fig_bar.add_trace(go.Bar(...))      # nível 2 (continua)
```

O loop duplo (mês × categoria) com 3 níveis de nesting para construir os traces do gráfico é difícil de ler e testar. Cada `go.Bar` individual por mês/categoria resulta potencialmente em dezenas de traces para o Plotly renderizar — impacto de performance.

### 4.3 Deep Nesting: `views/installments.py` — render_installments

**Arquivo:** `views/installments.py` (linhas 29–43)

```python
for _, row in parceladas.iterrows():     # nível 1
    faltam = row['total_parcelas'] - row['parcela_atual']
    if faltam > 0:                       # nível 2
        for i in range(1, int(faltam) + 1):  # nível 3
            future_month_date = ...
            if future_month_date > last_data_date:  # nível 4
                total_remaining_debt += row['amount']
                future_data.append(...)
```

4 níveis de indentação dentro de uma view. Esta lógica deveria estar em `core/installments.py` como função pura testável.

### 4.4 Feature Envy: `views/transactions.py` inveja `classifier/engine.py`

**Arquivo:** `views/transactions.py` (linhas 37–43)

A view acessa `cache_repo`, chama `normalize()`, constrói entradas de cache com o formato exato `{"categoria": ..., "source": "user"}` — ela **conhece profundamente a estrutura interna do motor de classificação**. Isso é Feature Envy clássico: a view quer ser o classificador.

### 4.5 Feature Envy: `app.py` inveja `data/repository.py`

**Arquivo:** `app.py` (linhas 27–34)

```python
categories_path = settings.CATEGORIES_PATH
cache_path = settings.CACHE_PATH
if not cache_path.exists() or categories_path.stat().st_mtime > cache_path.stat().st_mtime:
    cache_path.parent.mkdir(exist_ok=True, parents=True)
    cache_path.write_text("{}", encoding="utf-8")
```

O entry point manipula diretamente paths de arquivos e usa `stat().st_mtime` para invalidar cache. Esse comportamento pertence ao `CacheRepository` em `data/repository.py` — um método `invalidate_if_stale(reference_path)` resolveria isso.

### 4.6 String HTML hardcoded em múltiplos componentes (Primitive Obsession)

**Arquivos:**
- `views/overview.py` (linhas 12–17, 56–65, 70–73)
- `components/budget.py` (linhas 22–29, 40–47)
- `components/metrics.py` (linhas 25–32)
- `components/sidebar.py` (linhas 7–12)

Todos usam `st.markdown(..., unsafe_allow_html=True)` com strings HTML longas e formatadas manualmente via f-strings. Não há consistência nos valores de `padding`, `margin`, `font-size` entre esses componentes — cada um usa valores arbitrários (ex: `padding: 16px 20px`, `padding:12px 16px`, `padding: 22px 26px`).

---

## 5. Wrong Design Patterns — Padrões mal aplicados ou ausentes

### 5.1 Ausente: Strategy Pattern para classificação

**Arquivo afetado:** `classifier/engine.py` (linhas 42–63)

O pipeline de classificação atual tem uma sequência `if/elif/continue` inline para: cache → local_rules → fallback. Se um dia for adicionado um step de AI, de fuzzy matching, ou de outra fonte, essa função cresce com mais condicionais. O padrão **Strategy** permitiria adicionar estratégias de classificação de forma plugável sem modificar o engine.

**Exemplo do problema:**
```python
# hoje:
if normalized in cache: ...continue
local_cat = classify_local(normalized)
if local_cat and local_cat != "Outros": ...continue
# fallback direto — não há como inserir um step intermediário sem modificar o for loop
```

### 5.2 Mal aplicado: Repository Pattern sem abstração de interface

**Arquivo afetado:** `data/repository.py` (completo)

`JSONRepository` e `CacheRepository` são boas ideias, mas são instanciadas diretamente como singletons globais no módulo (`cache_repo = CacheRepository(...)`, `budget_repo = JSONRepository(...)`). Esses singletons são importados diretamente por `views/transactions.py` e `components/budget.py`, criando acoplamento hard. Sem uma interface ou injeção de dependência, é impossível substituir por um SQLite ou outro backend sem modificar múltiplos arquivos.

### 5.3 Ausente: Service Layer

**Arquivos afetados:** `views/transactions.py`, `views/overview.py`, `components/budget.py`, `app.py`

Não existe uma camada de serviço (`services/`) entre as views e o repositório/core. Toda lógica de negócio fica distribuída entre views e componentes, tornando impossível reutilizar lógica sem importar componentes Streamlit.

### 5.4 Mal aplicado: Singleton com variável global de módulo

**Arquivo afetado:** `classifier/engine.py` (linhas 11–17)

O `_cache = None` / `get_cache()` implementa um Singleton via variável global de módulo. Em Python com Streamlit, módulos são recarregados entre reruns dependendo da configuração de worker. O Streamlit já oferece `st.session_state` e `st.cache_data` como mecanismos corretos de estado entre reruns — o singleton de módulo bypassa esses mecanismos.

### 5.5 Ausente: Command Pattern para edição de categorias

**Arquivo afetado:** `views/transactions.py` (linhas 36–46)

A ação de "salvar correção manual de categoria" é implementada inline na view. Não há registro de quem alterou, quando, qual era o valor anterior, nem a possibilidade de desfazer. Um **Command Pattern** (ou simples log de auditoria) tornaria isso rastreável.

### 5.6 Mal aplicado: CSS duplicado em vez de CSS Variables

**Arquivo afetado:** `config/theme.py` (linhas 12–387 e 389–565)

O CSS de dark mode (`CSS_DARK`) redefine completamente o bloco `:root {}` com novos valores. Isso causa **375 + 176 = 551 linhas de CSS** com valores duplicados. O padrão correto com CSS Custom Properties já está parcialmente implementado (`:root { --accent: #0866FF; }`) mas o dark mode os sobrescreve em vez de simplesmente trocar uma classe no `<body>`. O toggle deveria adicionar a classe `data-theme="dark"` ao `<html>` e o CSS deveria ser:

```css
[data-theme="dark"] { --accent: #58A6FF; ... }
```

Isso reduziria o CSS de 551 para ~300 linhas.

---

## 6. Visual Bugs in Streamlit Interface — Bugs visuais e inconsistências estéticas

### 6.1 Quebra de layout: `.glass-card` envolvendo `st.plotly_chart`

**Arquivo:** `views/overview.py` (linhas 63–65)

```python
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
render_donut(df_gastos)
st.markdown('</div>', unsafe_allow_html=True)
```

O Streamlit **não garante** que o HTML gerado por `st.plotly_chart` fique dentro do `<div class="glass-card">` aberto manualmente. O Streamlit injeta seus próprios wrappers `<div data-testid="stPlotlyChart">` que podem quebrar a hierarquia do DOM, fazendo o `backdrop-filter` e `border-radius` do glass-card não se aplicar visualmente ao contêiner do gráfico. **O gráfico pode aparecer fora da borda arredondada.**

### 6.2 dark_mode toggle não reaplicar o CSS corretamente no primeiro render

**Arquivo:** `config/theme.py` (linhas 5–9) e `components/header.py` (linhas 22–26)

```python
def apply_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    if st.session_state.get("dark_mode", False):
        st.markdown(CSS_DARK, unsafe_allow_html=True)
```

`apply_theme()` é chamado uma única vez em `app.py` (linha 22), antes de `render_header()` (linha 23). Mas o estado `dark_mode` é inicializado **dentro** de `render_header()`. Na primeira execução: `apply_theme()` roda com `dark_mode` ainda não definido no session_state, então `st.session_state.get("dark_mode", False)` retorna `False` — o CSS_DARK nunca é aplicado no primeiro render, mesmo se o usuário havia salvo o dark mode antes. O usuário vê o flash do modo claro antes do dark mode ser ativado após o primeiro rerun.

### 6.3 Inconsistência: métricas nativas vs métricas customizadas

**Arquivos:** `views/recurrences.py` (linha 15) e `views/overview.py` (via `components/metrics.py`)

`views/recurrences.py` usa `st.metric(...)` nativo do Streamlit:
```python
st.metric("Estimativa de Custo Fixo Mensal", f"R$ {total_fixed:,.2f}")
```

`views/overview.py` usa `metric_card(...)` de `components/metrics.py` que renderiza HTML customizado. As duas abordagens coexistem no mesmo app com estilos completamente diferentes — o `st.metric` nativo tem aparência padrão do Streamlit (que é estilizado via CSS em `theme.py`), enquanto o `metric_card` é um div HTML customizado. Visualmente inconsistente.

Mesmo problema em `views/installments.py` (linha 46):
```python
st.metric("Saldo Devedor Estimado (Futuro)", f"R$ {total_remaining_debt:,.2f}", ...)
```

### 6.4 Cor hardcoded no gráfico de parcelas

**Arquivo:** `views/installments.py` (linha 73)

```python
marker_color='#EF4444',
```

O gráfico de projeção de parcelas usa `#EF4444` (vermelho) hardcoded, sem consultar `CATEGORY_COLORS` nem respeitar o dark mode. Em dark mode, esta cor pode ter contraste insuficiente sobre o fundo escuro `#0B0F1A`.

### 6.5 Fonte inconsistente nos gráficos Plotly

**Arquivo:** `components/charts.py` (linhas 22 e 94)

O `render_donut` usa `textfont=dict(size=11, family='Inter')` e `render_bar_history` usa `textfont=dict(size=10, color='white', family='Inter')`. O design system do app usa **DM Sans** como `--font-body` e **Merriweather** como `--font-heading` (definidos em `config/theme.py` linhas 17–18), mas os gráficos Plotly usam **Inter** — uma terceira fonte que não é carregada pelo Google Fonts no CSS do app. Os textos dentro dos gráficos podem renderizar com fallback do sistema.

### 6.6 Toggle dark mode exibe emoji em vez de ícone SVG consistente

**Arquivo:** `components/header.py` (linhas 23–25)

```python
button_label = "🌙" if st.session_state.dark_mode else "☀️"
if st.button(button_label, ...):
```

O botão usa emojis Unicode (`🌙` / `☀️`) que renderizam diferente entre sistemas operacionais (macOS vs Windows vs Linux). Em alguns sistemas, o emoji do sol pode aparecer com fundo colorido ou ter tamanho inconsistente com o layout do header.

### 6.7 `.streamlit/config.toml` e `config/theme.py` definem valores conflitantes

**Arquivos:** `.streamlit/config.toml` (completo) e `config/theme.py` (linhas 16–41)

O `config.toml` define:
```toml
primaryColor = "#0866FF"
backgroundColor = "#F0F2F5"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#1C1E21"
font = "sans serif"
```

O `theme.py` redefine tudo isso via CSS injetado com `!important`. Isso cria uma camada de theming dupla: o Streamlit aplica o `config.toml` primeiro, depois o CSS sobrescreve. Se o Streamlit atualizar sua estrutura de HTML em versões futuras, o CSS pode parar de funcionar sem aviso, enquanto o `config.toml` continuaria aplicando seu tema parcialmente — resultando em aparência híbrida não intencional.

### 6.8 Responsividade: `[data-testid="stHorizontalBlock"]` no CSS dark mode ausente

**Arquivo:** `config/theme.py` (linhas 370–385)

O CSS light mode tem regras responsivas para mobile (`@media (max-width: 768px)`) incluindo:
```css
[data-testid="stHorizontalBlock"] { flex-direction: column !important; }
```

O CSS dark mode (`CSS_DARK`) **não reimplementa** essas media queries. Em dark mode no mobile, o layout de colunas não colapsa para coluna única.

---

## 7. UI/UX Improvements — Melhorias de usabilidade

### 7.1 Sem feedback durante o carregamento inicial (loading state)

**Arquivo afetado:** `app.py` (linhas 50–65)

Quando o app carrega pela primeira vez (ou após `st.cache_data.clear()`), a função `load_all_data()` processa todos os CSVs em sequência sem nenhum indicador visual de progresso. Para usuários com muitos CSVs ou transações, a tela fica em branco por vários segundos. Solução: usar `st.spinner("Carregando faturas...")` ou `st.progress()` durante o loading.

### 7.2 Filtros na sidebar não têm botão "Limpar Filtros"

**Arquivo afetado:** `components/sidebar.py` (completo)

O usuário pode aplicar múltiplos filtros (texto, categorias, valor, data, tipo, ocultar outros). Para voltar ao estado sem filtros, precisa manualmente resetar cada campo. Um único botão "Limpar Filtros" que chame `st.rerun()` após resetar os valores de session_state melhoraria drasticamente a usabilidade.

### 7.3 Tabela de transações não tem paginação

**Arquivo afetado:** `views/transactions.py` (linhas 21–34)

O `st.data_editor` exibe todas as transações sem paginação. Para faturas com 100+ transações (cenário real de uso mensal), a tabela fica muito longa, exigindo scroll extenso. O Streamlit 1.31+ suporta `height` no `data_editor` para limitar a altura com scroll interno.

### 7.4 Edição de categoria não mostra confirmação contextual

**Arquivo afetado:** `views/transactions.py` (linhas 36–46)

Após editar uma categoria, o app exibe `st.success("✅ Classificações manuais salvas com sucesso!")` mas imediatamente força `st.rerun()`, fazendo a mensagem desaparecer em menos de 1 segundo sem ser lida pelo usuário. O usuário não tem feedback visual de que a ação foi executada.

### 7.5 Seleção de arquivo CSV não tem contexto de data

**Arquivo afetado:** `app.py` (linha 69)

```python
selected_file = st.sidebar.selectbox("Selecione o arquivo CSV:", csv_files, format_func=lambda x: x.name)
```

O selectbox mostra apenas o nome do arquivo (ex: `nubank_2024_01.csv`). Não mostra o período de datas das transações, quantidade de transações, ou valor total — informações que ajudariam o usuário a escolher o arquivo correto sem precisar trocar e verificar.

### 7.6 Aba "Recorrências" não tem ação de exclusão

**Arquivo afetado:** `views/recurrences.py` (completo)

A tabela de recorrências é somente leitura (`st.dataframe`). Se o algoritmo detectar falsos positivos (ex: uma compra que aconteceu 3 meses seguidos por coincidência mas não é uma assinatura), o usuário não tem como removê-la da lista. Falta um botão "Ignorar este item" que adicione o título a uma lista de exclusão persistida.

### 7.7 Sem visão cross-arquivo (visão consolidada)

**Arquivo afetado:** `views/overview.py`, `app.py`

O dashboard sempre mostra dados de **um único arquivo CSV** por vez (o selecionado na sidebar). O gráfico de histórico mensal usa `df_consolidated` (todos os arquivos), mas as métricas (total gasto, ticket médio, top categoria) são sempre do arquivo selecionado. Não há uma view dedicada "Visão Anual" ou "Visão Consolidada" que mostre métricas agregadas de todos os arquivos carregados.

### 7.8 Acessibilidade: `metric_card` usa `title` HTML ao invés de `aria-label`

**Arquivo afetado:** `components/metrics.py` (linha 23)

```python
help_html = f' title="{help_text}"' if help_text else ""
```

O atributo HTML `title` para tooltip funciona apenas no hover com mouse — não é acessível via teclado nem leitores de tela. O padrão correto seria `aria-label` ou `aria-describedby`.

---

## 8. Existing Features Mapped — Mapeamento de todas as funcionalidades atuais

> Cada funcionalidade está mapeada ao arquivo que a implementa.

### 8.1 Upload e armazenamento de CSVs
- **Onde:** `app.py` (linhas 37–43)
- **Como funciona:** Sidebar com `st.file_uploader`. O arquivo é salvo diretamente em `DATA_DIR` via `write_bytes`. Após salvar, limpa o cache e reroda o app.
- **Limitação:** Apenas CSVs do Nubank. Sem validação do formato antes de salvar.

### 8.2 Parsing e normalização de CSVs
- **Onde:** `parsers/nubank.py`
- **Como funciona:** Lê com UTF-8, fallback para Latin-1. Renomeia colunas. Classifica tipo de transação. Filtra pagamentos de fatura. Extrai informações de parcelamento com guards matemáticos.

### 8.3 Invalidação automática de cache por mudança no categories.json
- **Onde:** `app.py` (linhas 27–34)
- **Como funciona:** Compara `st_mtime` do `categories.json` com `st_mtime` do arquivo de cache. Se o JSON for mais novo, reseta o cache para `{}`.

### 8.4 Classificação automática de transações
- **Onde:** `classifier/engine.py`, `classifier/local_rules.py`, `utils/normalize.py`
- **Como funciona (ordem estrita):**
  1. Normaliza o título (remove acentos, IDs, tokens curtos)
  2. Verifica no cache de classificações (`cache/categories_cache.json`)
  3. Aplica keyword matching (substring, case-insensitive) contra `categories.json`
  4. Aplica regex matching como fallback
  5. Se nada casa, classifica como "Outros"
  6. Salva resultado no cache para evitar reclassificação

### 8.5 Cache persistente de classificações
- **Onde:** `data/repository.py` (`CacheRepository`), `cache/categories_cache.json`
- **Como funciona:** JSON com chave = descrição normalizada, valor = `{"categoria": "...", "source": "local|ai|user"}`. Suporta migração de formato legado (string → dict).

### 8.6 Edição manual de categorias
- **Onde:** `views/transactions.py`
- **Como funciona:** `st.data_editor` com coluna `categoria` como `SelectboxColumn`. Ao editar, detecta diff, normaliza o título, e salva no cache com `source: "user"`.

### 8.7 Filtros de transações
- **Onde:** `components/sidebar.py`, `utils/filters.py`
- **Filtros disponíveis:**
  - Busca textual (título ou categoria)
  - Multiselect de categorias
  - Faixa de valor (slider)
  - Período de datas (date_input)
  - Tipo de transação (gasto/estorno/ajuste)
  - Toggle "Ocultar Outros" / "Só Outros"

### 8.8 Exportação de dados
- **Onde:** `utils/export.py`
- **Como funciona:** Botão de download que converte o DataFrame filtrado para CSV UTF-8 e oferece download via `st.download_button`.

### 8.9 Visão Geral (Aba 1)
- **Onde:** `views/overview.py`, `components/metrics.py`, `components/charts.py`, `components/budget.py`
- **Funcionalidades:**
  - Gráfico de donut: gastos por categoria (arquivo selecionado)
  - Métricas: total de transações, valor total, ticket médio, maior categoria, % não classificado
  - Delta automático comparando com o CSV anterior na lista
  - Acompanhamento de orçamento global e por categoria com barras de progresso
  - Histórico mensal com gráfico de barras empilhadas + média móvel de 3 meses (dados consolidados)

### 8.10 Tabela de Transações (Aba 2)
- **Onde:** `views/transactions.py`
- **Funcionalidades:** Filtro textual inline, tabela editável com dropdown de categoria

### 8.11 Recorrências (Aba 3)
- **Onde:** `views/recurrences.py`, `core/recurrences.py`
- **Como funciona:** Detecta transações que aparecem em 3+ meses distintos OU cuja categoria é "Assinaturas". Exibe tabela com: serviço, categoria, valor médio, meses ativos. Mostra estimativa de custo fixo mensal.

### 8.12 Parcelas Futuras (Aba 4)
- **Onde:** `views/installments.py`, `core/installments.py`
- **Como funciona:** Identifica compras parceladas (`total_parcelas > 1`), mantém apenas a entrada mais recente de cada série. Calcula parcelas ainda a vencer após a última data de transação. Exibe: saldo devedor estimado, barra de progresso por item, gráfico de impacto mensal futuro.

### 8.13 Dark Mode
- **Onde:** `components/header.py`, `config/theme.py`
- **Como funciona:** Toggle via botão emoji no header. Alterna `st.session_state.dark_mode`. O CSS dark é injetado condicionalmente em `apply_theme()`.

### 8.14 Acompanhamento de Orçamento
- **Onde:** `components/budget.py`
- **Como funciona:** Lê `config/budget.json`. Exibe barras de progresso HTML para orçamento global e por categoria. Formulário de edição inline com `st.expander`.

### 8.15 Suporte a múltiplos CSVs
- **Onde:** `app.py` (linhas 45–70)
- **Como funciona:** Carrega todos os `.csv` da `DATA_DIR`. Consolida em `df_consolidated`. Permite selecionar qual arquivo exibir no selectbox da sidebar.

---

## 9. Proposed New Features — Proposta de novas funcionalidades

### 9.1 Suporte a múltiplos bancos (além do Nubank)

**Justificativa:** O parser atual é 100% acoplado ao formato Nubank (`parsers/nubank.py`). O projeto pode crescer para suportar Itaú, Bradesco, XP, etc.  
**Impacto:** Permite uso por qualquer pessoa com cartão de crédito brasileiro, aumentando o escopo do projeto.  
**Arquivos que precisariam ser criados/modificados:**
- Criar `parsers/itau.py`, `parsers/bradesco.py` etc. com a mesma interface (`parse_X(filepath) -> DataFrame`)
- Modificar `app.py` para detectar o banco automaticamente (pelo cabeçalho do CSV) ou permitir seleção manual
- Criar `parsers/__init__.py` com factory: `get_parser(filepath) -> Callable`

### 9.2 Relatório mensal em PDF/HTML exportável

**Justificativa:** O usuário pode querer compartilhar ou arquivar um resumo do mês. Hoje só é possível exportar o CSV bruto.  
**Impacto:** Aumenta o valor do dashboard como ferramenta de controle financeiro pessoal.  
**Arquivos que precisariam ser criados/modificados:**
- Criar `utils/report.py` com geração de HTML via template (Jinja2) ou PDF via `reportlab`/`weasyprint`
- Adicionar `requirements.txt`: `jinja2` e/ou `weasyprint`
- Criar `views/report.py` com botão de geração e download
- Adicionar aba "Relatório" em `app.py`

### 9.3 Log de auditoria de classificações manuais

**Justificativa:** Quando o usuário edita uma categoria manualmente, não há registro de quando ou quais mudanças foram feitas. O cache apenas sobrescreve.  
**Impacto:** Rastreabilidade e possibilidade de desfazer correções.  
**Arquivos que precisariam ser criados/modificados:**
- Modificar `data/repository.py`: adicionar `AuditLogRepository` que salva em `cache/audit_log.json`
- Modificar `views/transactions.py` (ou criar `services/classification.py`): registrar cada edição com timestamp, título, categoria anterior, categoria nova, fonte
- Criar `views/audit.py` para exibir o log

### 9.4 Metas financeiras por categoria com projeção

**Justificativa:** O orçamento atual (`components/budget.py`) mostra apenas o consumo do mês atual. Não há projeção de "se continuar neste ritmo, vai ultrapassar o limite em X dias".  
**Impacto:** Intervenção preventiva antes de estourar o orçamento.  
**Arquivos que precisariam ser criados/modificados:**
- Modificar `core/` para adicionar `projections.py` com lógica de projeção linear baseada em dias decorridos do mês
- Modificar `components/budget.py` para exibir projeção
- Adicionar alerta visual (`st.warning`) quando a projeção ultrapassar 90% do orçamento

### 9.5 Detecção de gastos anômalos (alertas)

**Justificativa:** Se o usuário gasta R$50 por mês em Delivery e um mês específico gastou R$300, o app poderia destacar esse outlier automaticamente.  
**Impacto:** Aumenta o valor da análise automática sem precisar de AI.  
**Arquivos que precisariam ser criados/modificados:**
- Criar `core/anomalies.py` com detecção por desvio padrão (ex: valor > média + 2σ da categoria nos últimos N meses)
- Modificar `views/overview.py` para exibir alertas com `st.warning`

### 9.6 Comparação mês a mês detalhada

**Justificativa:** Hoje a comparação é apenas via delta numérico nas métricas (total, ticket médio). Não há drill-down de "o que mudou".  
**Impacto:** Insight imediato sobre padrões de consumo.  
**Arquivos que precisariam ser criados/modificados:**
- Criar `views/comparison.py` com tabela de categorias lado a lado (mês atual vs mês anterior)
- Modificar `app.py` para adicionar a aba
- Usar `df_consolidated` já disponível

### 9.7 Importação automática de CSVs de uma pasta monitorada

**Justificativa:** Atualmente o upload é manual via sidebar. Se o usuário baixar o CSV do Nubank para uma pasta específica, o app poderia detectar automaticamente.  
**Impacto:** Zero fricção no fluxo de atualização de dados.  
**Arquivos que precisariam ser criados/modificados:**
- Modificar `config/settings.py`: adicionar `WATCH_DIR` com path configurável via env
- Criar `utils/file_watcher.py` usando `watchdog` ou polling periódico

### 9.8 Suporte a múltiplas personas/perfis de usuário

**Justificativa:** Se o app for usado por casal ou família, cada pessoa poderia ter seu próprio conjunto de categorias e orçamentos.  
**Impacto:** Amplia o escopo sem virar SaaS.  
**Arquivos que precisariam ser criados/modificados:**
- Modificar `config/settings.py`: adicionar `PROFILE` lendo de env
- Segregar paths de cache, budget e categorias por perfil
- Adicionar seletor de perfil em `app.py`

---

## 10. Prioritized List — Lista de tarefas priorizada por impacto

> **Legenda:** 🔴 HIGH — bloqueia qualidade ou tem risco de bug real | 🟡 MEDIUM — melhoria significativa sem urgência | 🟢 LOW — refinamento ou feature nova

---

### 🔴 HIGH — Impacto imediato na corretude e manutenibilidade

| # | Tarefa | Arquivo(s) Afetado(s) | Esforço |
|---|--------|-----------------------|---------|
| H1 | **Corrigir a ordem de inicialização do dark_mode**: mover `st.session_state.dark_mode` init para antes de `apply_theme()` em `app.py`, e remover do `header.py` | `app.py` (adicionar init antes da linha 22), `components/header.py` (remover linhas 12–13) | 15 min |
| H2 | **Remover dependência morta `google-generativeai`** do `requirements.txt` e o atributo `GEMINI_API_KEY` de `settings.py` | `requirements.txt` (linha 5), `config/settings.py` (linha 16) | 5 min |
| H3 | **Mover invalidação de cache para `CacheRepository`**: criar método `invalidate_if_stale(reference_path)` e remover lógica inline do `app.py` | `data/repository.py`, `app.py` (linhas 27–34) | 30 min |
| H4 | **Corrigir o import tardio dentro de `load_all_data`**: mover `from utils.logger import get_logger` para o topo de `app.py` | `app.py` (linha 58 → mover para o bloco de imports) | 5 min |
| H5 | **Eliminar a leitura repetida de `categories.json` em `classify_local`**: carregar o dict uma vez em `classify_batch` e passar como parâmetro | `classifier/engine.py`, `classifier/local_rules.py` (linhas 10–13 e 27) | 20 min |
| H6 | **Corrigir a categoria `"Outros"` no `categories.json`**: remover o regex `.*` que nunca é atingido e é enganoso | `categories.json` (linhas 221–226) | 5 min |
| H7 | **Adicionar `st.set_page_icon` e melhorar `page_title`**: o `st.set_page_config` em `app.py` usa apenas `page_title="Finanças"` sem ícone — browser tab fica sem identidade visual | `app.py` (linha 21) | 5 min |

---

### 🟡 MEDIUM — Qualidade de código e manutenibilidade

| # | Tarefa | Arquivo(s) Afetado(s) | Esforço |
|---|--------|-----------------------|---------|
| M1 | **Extrair lógica de cálculo de métricas de `views/overview.py`** para uma função em `core/` ou `services/` | `views/overview.py` (linhas 29–44), criar `core/metrics.py` | 1h |
| M2 | **Criar `services/classification.py`** para encapsular a lógica de salvar correções manuais, retirando de `views/transactions.py` | `views/transactions.py` (linhas 36–46), criar `services/classification.py` | 45 min |
| M3 | **Mover projeção de parcelas futuras de `views/installments.py` para `core/installments.py`** | `views/installments.py` (linhas 26–43), `core/installments.py` | 45 min |
| M4 | **Separar `components/budget.py` em dois**: `render_budget_display()` e `render_budget_editor()` (ou mover editor para `views/`) | `components/budget.py` (separar linhas 5–47 das linhas 49–69) | 30 min |
| M5 | **Eliminar o diretório `components/ui/`** que contém dead code não utilizado | `components/ui/__init__.py`, `components/ui/components.py` | 5 min |
| M6 | **Substituir `_cache` global em `classifier/engine.py`** por `st.session_state` ou `st.cache_data` para alinhar com o modelo de estado do Streamlit | `classifier/engine.py` (linhas 11–17) | 30 min |
| M7 | **Unificar uso de métricas**: substituir `st.metric()` nativo em `views/recurrences.py` e `views/installments.py` por `metric_card()` para consistência visual | `views/recurrences.py` (linha 15), `views/installments.py` (linha 46) | 20 min |
| M8 | **Adicionar `st.spinner` durante `load_all_data`** para dar feedback de carregamento | `app.py` (bloco de chamada da linha 62) | 10 min |
| M9 | **Adicionar botão "Limpar Filtros" na sidebar** | `components/sidebar.py` | 15 min |
| M10 | **Corrigir `metric_card` para usar `aria-label` em vez de `title`** para acessibilidade | `components/metrics.py` (linha 23) | 10 min |
| M11 | **Consolidar `CATEGORY_COLORS` para fora de `theme.py`**: mover para `config/categories.py` ou `categories.json` | `config/theme.py` (linhas 568–586), `components/charts.py` (linha 4), `app.py` (linha 18) | 30 min |
| M12 | **Mover os arquivos `.md` de planejamento para `docs/archive/`** e adicionar ao `.gitignore` | 22 arquivos em `markdown/` e raiz (listados na seção 2.6) | 10 min |
| M13 | **Adicionar `height` ao `st.data_editor`** na tabela de transações para limitar altura sem scroll de página | `views/transactions.py` (linha 21–34) | 5 min |
| M14 | **Adicionar `@st.cache_data` em `load_categories()`** em `local_rules.py` para evitar leitura de disco por transação | `classifier/local_rules.py` (linhas 10–13) | 5 min |
| M15 | **Corrigir font family nos gráficos Plotly**: trocar `'Inter'` por `'DM Sans'** para consistência com o design system | `components/charts.py` (linhas 22, 94) | 5 min |

---

### 🟢 LOW — Features novas e refinamentos

| # | Tarefa | Arquivo(s) Afetado(s) | Esforço |
|---|--------|-----------------------|---------|
| L1 | **Adicionar suporte a Itaú CSV**: criar `parsers/itau.py` e factory em `parsers/__init__.py` | Criar `parsers/itau.py`, modificar `app.py` | 2h |
| L2 | **Implementar log de auditoria de edições manuais** | `data/repository.py`, criar `services/classification.py`, criar `views/audit.py` | 3h |
| L3 | **Adicionar projeção de orçamento**: "se continuar assim, ultrapassa em X dias" | Criar `core/projections.py`, modificar `components/budget.py` | 2h |
| L4 | **Adicionar detecção de gastos anômalos** por desvio padrão histórico | Criar `core/anomalies.py`, modificar `views/overview.py` | 3h |
| L5 | **Adicionar aba "Comparação Mensal"** com tabela side-by-side por categoria | Criar `views/comparison.py`, modificar `app.py` | 2h |
| L6 | **Implementar o toggle de dark mode via classe CSS** em vez de CSS duplicado, reduzindo `theme.py` de 631 para ~350 linhas | `config/theme.py` (refatorar CSS_DARK), `components/header.py` | 2h |
| L7 | **Adicionar ação "Ignorar falso positivo" na aba de Recorrências** | `views/recurrences.py`, criar `data/ignored_recurrences.json`, `data/repository.py` | 1h 30min |
| L8 | **Contextualizar o selectbox de arquivo com dados de período e total** | `app.py` (linha 69): melhorar `format_func` para exibir período e qtd de transações | 30 min |
| L9 | **Adicionar `DEFAULT_DARK_MODE` como env var** (`DARK_MODE=true`) | `config/settings.py` (linha 14) | 5 min |
| L10 | **Expandir cobertura de testes**: atualmente apenas 2 testes em `tests/test_ui.py`. Adicionar testes para `normalize()`, `classify_local()`, `parse_nubank()`, `detect_recurrences()`, `calculate_future_installments()` | `tests/` — criar `test_normalize.py`, `test_classifier.py`, `test_parser.py`, `test_core.py` | 4h |

---

## Resumo Executivo

O `app_faturas` é um projeto **bem estruturado para seu escopo de MVP pessoal**, com separação lógica razoável de módulos e um sistema de classificação inteligente (cache → keywords → regex). Os maiores riscos no estado atual são:

1. **Bug real imediato (H1):** O dark mode não funciona corretamente no primeiro render devido à ordem de inicialização.  
2. **Inchaço desnecessário (H2 + H5):** Dependência de 50MB (`google-generativeai`) que nunca é usada e leitura repetida de arquivo em loop.  
3. **Acoplamento que vai crescer (M1 + M2 + M4):** Views e componentes com lógica de negócio e persistência vão dificultar qualquer evolução futura.  
4. **Dead code confuso (seção 2):** `components/ui/`, regex `.*` em categories.json, e 22 arquivos Markdown de planejamento poluem o repositório.

O caminho mais seguro é executar todos os itens **HIGH em uma única sessão** (estimativa: 1h30min total), depois atacar os MEDIUM incrementalmente.
