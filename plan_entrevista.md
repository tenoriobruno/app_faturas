# Redesign Visual iOS — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesenhar a aparência do dashboard para uma estética iOS limpa (sans pura, cards arredondados, accent slate sóbrio) e trocar a paleta de gráficos por uma paleta dessaturada harmônica, sem alterar lógica de dados.

**Architecture:** Mudança puramente de apresentação. Centro em `config/theme.py` (CSS, tipografia, accent), `config/categories.py` (paleta), `components/charts.py` (estilo dos gráficos), `views/overview.py` (reordenação dos painéis). Nenhuma alteração em parsers, classificação, cache ou regras de negócio.

**Tech Stack:** Python 3.9+, Streamlit, Plotly, Pandas, Pytest.

**Contexto crítico descoberto na análise:**
- `categories.json` define **16 categorias**: Delivery, Restaurante, Transporte, Supermercado, Saúde, Assinaturas, Serviço, Compras, Moradia, Lazer, Educação, Viagem, Feira, **Carro**, Estorno, Outros.
- O `CATEGORY_COLORS` atual está **dessincronizado**: tem `Alimentação` e `Gasolina` (que NÃO existem no JSON) e falta `Carro`. A Task 1 corrige isso.
- A Visão Geral hoje usa `st.columns([0.6, 0.4])` com donut ao lado dos metric cards. O redesign reordena para: metric cards em grid no topo → donut em largura total → histórico em largura total.

**Decisões de design travadas (validadas via mockup):**
- Tipografia: sans pura (DM Sans), remover serif Merriweather.
- Accent: slate `#3D5A80` (light) no lugar do azul Facebook `#0866FF`.
- Paleta de gráficos: dessaturada terrosa (definida na Task 1).
- Ordem Visão Geral: metric cards → donut full-width → histórico full-width.
- Manter light + dark mode.

**Como verificar visualmente (usado em várias tasks):**
```bash
streamlit run app.py
```
Abrir no browser, subir um CSV de exemplo, conferir a aba Visão Geral em light e dark mode (toggle no header ☀️/🌙).

---

## Task 1: Nova paleta de cores sincronizada com as categorias reais

**Files:**
- Modify: `config/categories.py` (substituir todo o dict `CATEGORY_COLORS`)
- Test: `tests/test_theme_palette.py` (criar)

- [ ] **Step 1: Escrever o teste que falha**

Criar `tests/test_theme_palette.py`:

```python
import re
from config.categories import CATEGORY_COLORS
from config.settings import settings


def test_every_category_has_color():
    """Toda categoria definida em categories.json deve ter cor no palette."""
    names = settings.get_category_names()
    missing = [n for n in names if n not in CATEGORY_COLORS]
    assert missing == [], f"Categorias sem cor no palette: {missing}"


def test_all_colors_are_valid_hex():
    for cat, color in CATEGORY_COLORS.items():
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", color), f"Cor inválida em {cat}: {color}"
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

Run: `python -m pytest tests/test_theme_palette.py -v`
Expected: `test_every_category_has_color` FALHA — `Carro` está em `categories.json` mas não em `CATEGORY_COLORS`.

- [ ] **Step 3: Substituir o palette**

Substituir TODO o conteúdo de `config/categories.py` por:

```python
CATEGORY_COLORS = {
    # Paleta dessaturada terrosa — saturação/luminosidade uniformes para harmonia.
    # Chaves alinhadas com as 16 categorias de categories.json.
    'Moradia': '#3D5A80',       # slate blue (âncora — maior categoria típica)
    'Restaurante': '#E07A5F',   # terracota
    'Delivery': '#C44E52',      # tijolo
    'Supermercado': '#81B29A',  # sage
    'Transporte': '#6FB3B8',    # teal suave
    'Saúde': '#9D8DF1',         # lavanda
    'Assinaturas': '#7B8FC7',   # índigo suave
    'Serviço': '#8E9AAF',       # azul-cinza
    'Compras': '#D8A657',       # ocre
    'Lazer': '#B07AA1',         # malva
    'Educação': '#6A8CA4',      # azul-poeira
    'Viagem': '#E0B452',        # ouro
    'Feira': '#A3B565',         # oliva
    'Carro': '#7D6E83',         # ameixa acinzentada
    'Estorno': '#A8C686',       # verde suave (positivo)
    'Outros': '#B0B3B8',        # cinza neutro
    # Aliases legados — categorias antigas que ainda podem aparecer em cache/CSV.
    'Alimentação': '#E07A5F',
    'Gasolina': '#7D6E83',
}
```

- [ ] **Step 4: Rodar o teste e confirmar que passa**

Run: `python -m pytest tests/test_theme_palette.py -v`
Expected: PASS (ambos os testes).

- [ ] **Step 5: Commit**

```bash
git add config/categories.py tests/test_theme_palette.py
git commit -m "feat: paleta de gráficos dessaturada sincronizada com categorias"
```

---

## Task 2: Tipografia — remover serif, sans pura

**Files:**
- Modify: `config/theme.py` (bloco `CSS`, seção `:root` e import de fontes)

- [ ] **Step 1: Trocar o import de fontes**

Em `config/theme.py`, a linha de `@import` (atualmente importa DM Sans + Merriweather). Substituir por (só DM Sans, com todos os pesos):

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');
```

- [ ] **Step 2: Trocar a variável de fonte de heading**

Em `:root` do bloco `CSS`, trocar:

```css
    --font-heading: 'Merriweather', Georgia, serif;
```

por:

```css
    --font-heading: 'DM Sans', system-ui, -apple-system, sans-serif;
```

- [ ] **Step 3: Ajustar os pesos dos headings (iOS = sans bold)**

Na seção `/* ===================== TYPOGRAPHY ===================== */`, substituir o bloco:

```css
h1, h2, h3 {
    font-family: var(--font-heading) !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em;
    color: var(--text-primary) !important;
}
h1 {
    font-size: 2rem !important;
    font-weight: 300 !important;
    letter-spacing: -0.02em;
}
h2 { font-size: 1.35rem !important; }
h3 { font-size: 1.1rem !important; }
```

por:

```css
h1, h2, h3 {
    font-family: var(--font-heading) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
    color: var(--text-primary) !important;
}
h1 {
    font-size: 2rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.03em;
}
h2 { font-size: 1.35rem !important; font-weight: 600 !important; }
h3 { font-size: 1.1rem !important; font-weight: 600 !important; }
```

- [ ] **Step 4: Verificar visualmente**

Run: `streamlit run app.py` — conferir que os títulos (h1 "Finanças Pessoais", headers das seções) aparecem em sans bold, sem serifa. Conferir em light e dark.

- [ ] **Step 5: Commit**

```bash
git add config/theme.py
git commit -m "feat: tipografia sans pura, remove serif Merriweather"
```

---

## Task 3: Accent slate no lugar do azul Facebook (light + dark)

**Files:**
- Modify: `config/theme.py` (variáveis de accent em `:root` do `CSS` e do `CSS_DARK`)

- [ ] **Step 1: Trocar accent no tema light**

Em `:root` do bloco `CSS`, substituir o grupo de variáveis de accent e gradientes de fundo. Trocar:

```css
    --bg-page: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(8,102,255,0.06), transparent),
               radial-gradient(ellipse 50% 40% at 80% 100%, rgba(8,102,255,0.04), transparent),
               #F0F2F5;
```

por (fundo cinza-claro Apple, gradiente slate sutil):

```css
    --bg-page: radial-gradient(ellipse 80% 50% at 50% -20%, rgba(61,90,128,0.05), transparent),
               radial-gradient(ellipse 50% 40% at 80% 100%, rgba(61,90,128,0.03), transparent),
               #F2F2F7;
```

E trocar:

```css
    --border-card-accent: rgba(8, 102, 255, 0.15);
    --accent: #0866FF;
    --accent-soft: rgba(8, 102, 255, 0.08);
    --accent-glow: rgba(8, 102, 255, 0.15);
```

por:

```css
    --border-card-accent: rgba(61, 90, 128, 0.18);
    --accent: #3D5A80;
    --accent-soft: rgba(61, 90, 128, 0.08);
    --accent-glow: rgba(61, 90, 128, 0.15);
```

- [ ] **Step 2: Trocar accent no tema dark**

Em `:root` do bloco `CSS_DARK`, trocar:

```css
    --bg-page: radial-gradient(ellipse 90% 55% at 50% -10%, rgba(8,102,255,0.08), transparent),
               radial-gradient(ellipse 60% 40% at 80% 90%, rgba(88,166,255,0.04), transparent),
               #0B0F1A;
```

por:

```css
    --bg-page: radial-gradient(ellipse 90% 55% at 50% -10%, rgba(123,156,196,0.08), transparent),
               radial-gradient(ellipse 60% 40% at 80% 90%, rgba(123,156,196,0.04), transparent),
               #0B0F1A;
```

E trocar:

```css
    --border-card-accent: rgba(88, 166, 255, 0.2);
    --accent: #58A6FF;
    --accent-soft: rgba(88, 166, 255, 0.1);
    --accent-glow: rgba(88, 166, 255, 0.18);
```

por (slate mais claro para contraste no escuro):

```css
    --border-card-accent: rgba(123, 156, 196, 0.22);
    --accent: #7B9CC4;
    --accent-soft: rgba(123, 156, 196, 0.1);
    --accent-glow: rgba(123, 156, 196, 0.18);
```

- [ ] **Step 3: Verificar visualmente**

Run: `streamlit run app.py` — conferir que tabs ativas, bordas de hover, foco de inputs, barra lateral dos metric cards e barras de progresso usam o slate (não mais azul Facebook). Conferir light e dark.

- [ ] **Step 4: Commit**

```bash
git add config/theme.py
git commit -m "feat: accent slate sóbrio substitui azul Facebook"
```

---

## Task 4: Estilo dos gráficos coerente com o tema

**Files:**
- Modify: `components/charts.py` (fallback de cor do donut)
- Modify: `config/theme.py` (função `get_plotly_layout` — apenas se necessário; ver step)

- [ ] **Step 1: Trocar fallback do donut por cinza neutro**

Em `components/charts.py`, dentro de `render_donut`, substituir:

```python
    import plotly.express as px
    # fallback colors from Plotly qualitative palette
    fallback_palette = px.colors.qualitative.Plotly
    pie_colors = [CATEGORY_COLORS.get(cat, fallback_palette[i % len(fallback_palette)]) for i, cat in enumerate(category_spend.index)]
```

por (categoria sem cor cai em cinza neutro — evita cor berrante fora da paleta):

```python
    pie_colors = [CATEGORY_COLORS.get(cat, '#B0B3B8') for cat in category_spend.index]
```

- [ ] **Step 2: Confirmar que a média móvel do histórico continua legível**

Em `render_bar_history`, a linha de média móvel usa `'#FAFAFA' if is_dark else '#1A1D23'` e o fallback de barra usa `'#94A3B8'`. Esses tons neutros continuam OK com a nova paleta — **não alterar**. Apenas confirmar lendo o código que nenhum hex azul-Facebook (`#0866FF`/`#58A6FF`) está hardcoded em `charts.py`. Se encontrar algum, trocar por `var`-equivalente neutro `#8E9AAF`.

- [ ] **Step 3: Verificar visualmente**

Run: `streamlit run app.py` — conferir donut e histórico: cores da nova paleta, mesma cor por categoria nos dois gráficos, sem clash. Conferir light e dark.

- [ ] **Step 4: Commit**

```bash
git add components/charts.py
git commit -m "feat: gráficos usam fallback neutro e paleta sóbria"
```

---

## Task 5: Reordenar a Visão Geral (metric cards → donut → histórico)

**Files:**
- Modify: `views/overview.py` (função `render_overview`, linhas ~11-67)

- [ ] **Step 1: Substituir o corpo de `render_overview`**

Em `views/overview.py`, substituir todo o bloco da função `render_overview` (da assinatura até a chamada de `render_budget`, ou seja, as linhas que hoje vão de `def render_overview(...)` até `render_budget(df, df_consolidated)`) por:

```python
def render_overview(df: pd.DataFrame, df_consolidated: pd.DataFrame, csv_files: list, selected_file, all_data: dict):
    # --- métricas do período ---
    prev_df = None
    try:
        idx = csv_files.index(selected_file)
        if idx + 1 < len(csv_files):
            prev_file = csv_files[idx + 1]
            prev_df = all_data[prev_file.name]
    except ValueError:
        pass

    from core.metrics import calculate_overview_metrics
    metrics = calculate_overview_metrics(df, prev_df)

    # --- linha de metric cards em grid (topo) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Valor Total", f"R$ {metrics['valor_total']:,.2f}",
                    delta=f"R$ {metrics['delta_valor']:+,.2f}" if metrics['delta_valor'] is not None else None,
                    delta_color="inverse")
    with c2:
        metric_card("Ticket Médio", f"R$ {metrics['ticket_medio']:,.2f}",
                    delta=f"R$ {metrics['delta_ticket']:+,.2f}" if metrics['delta_ticket'] is not None else None,
                    delta_color="inverse")
    with c3:
        metric_card("Transações (Gastos)", f"{metrics['total_tx']}",
                    delta=f"{metrics['delta_tx']:+d}" if metrics['delta_tx'] is not None else None,
                    delta_color="normal")
    with c4:
        metric_card("Maior Categoria", metrics['top_cat'])

    # linha auxiliar: % não-classificado + atalho de filtro da maior categoria
    aux_l, aux_r = st.columns([0.6, 0.4])
    with aux_l:
        st.caption(f"% Não-classificado: {metrics['outros_pct']:.1f}%")
    with aux_r:
        if metrics['top_cat'] != "N/A":
            if st.button(f"🔍 Ver transações de {metrics['top_cat']}", key="quick_filter_top_cat"):
                st.session_state['quick_filter_category'] = metrics['top_cat']
                st.toast("Filtro aplicado! Abra a aba 'Transações' para ver os resultados.", icon="🔍")
                st.rerun()

    st.divider()

    # --- donut em largura total (detalhe do mês) ---
    df_gastos = df[df['tipo_transacao'] == 'gasto']
    st.markdown(
        '<div style="font-weight:700;font-size:1.05rem;margin-bottom:12px;">💸 Gastos por Categoria</div>',
        unsafe_allow_html=True,
    )
    render_donut(df_gastos)

    st.divider()

    # --- histórico em largura total (tendência) ---
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="font-weight:700;font-size:1.05rem;margin-bottom:16px;">📈 Histórico Mensal de Gastos</div>', unsafe_allow_html=True)
    render_bar_history(df_consolidated)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    _render_month_health(df, df_consolidated)

    render_budget(df, df_consolidated)
```

A função `_render_month_health` abaixo permanece **inalterada**.

- [ ] **Step 2: Confirmar imports**

Conferir que o topo de `views/overview.py` mantém os imports já existentes (`render_donut`, `render_bar_history`, `metric_card`, etc.). Nenhum import novo é necessário; nenhum ficou órfão.

- [ ] **Step 3: Verificar visualmente**

Run: `streamlit run app.py` — na aba Visão Geral, conferir a nova ordem de cima para baixo: 4 metric cards lado a lado → linha auxiliar (% não-classificado + botão) → donut em largura total → histórico em largura total → Saúde do Mês → orçamento. O donut agora ocupa a largura inteira (não está mais espremido ao lado das métricas). Conferir que o histórico de vários meses respira. Conferir light e dark.

- [ ] **Step 4: Rodar a suíte de testes (sem regressão)**

Run: `python -m pytest tests/ -v`
Expected: PASS (incluindo `tests/test_ui.py` se existir).

- [ ] **Step 5: Commit**

```bash
git add views/overview.py
git commit -m "feat: reordena Visao Geral para cards, donut full-width, historico full-width"
```

---

## Task 6: Donut em largura total — ajustar layout do gráfico

**Files:**
- Modify: `components/charts.py` (função `render_donut`, `update_layout`)

**Contexto:** Com o donut agora em largura total (Task 5), a legenda vertical à direita com `r=120` de margem fica desproporcional num container largo. Centralizar melhor.

- [ ] **Step 1: Ajustar margem e legenda do donut**

Em `render_donut`, substituir o bloco `fig_pie.update_layout(...)`:

```python
    fig_pie.update_layout(
        **plot_layout,
        margin=dict(t=16, b=16, l=16, r=120),
        height=400,
        showlegend=True,
        legend=dict(
            orientation='v',
            x=1.02,
            y=0.5,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=11, color='#8B949E' if is_dark else '#64748B')
        )
    )
```

por:

```python
    fig_pie.update_layout(
        **plot_layout,
        margin=dict(t=16, b=40, l=16, r=16),
        height=420,
        showlegend=True,
        legend=dict(
            orientation='h',
            x=0.5,
            xanchor='center',
            y=-0.08,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=11, color='#8B949E' if is_dark else '#64748B')
        )
    )
```

- [ ] **Step 2: Verificar visualmente**

Run: `streamlit run app.py` — o donut deve ficar centralizado no container largo, com a legenda horizontal embaixo. Conferir light e dark.

- [ ] **Step 3: Commit**

```bash
git add components/charts.py
git commit -m "feat: donut centralizado com legenda horizontal para largura total"
```

---

## Task 7: Verificação final integrada

**Files:** nenhum (verificação).

- [ ] **Step 1: Suíte completa**

Run: `python -m pytest tests/ -v`
Expected: tudo PASS.

- [ ] **Step 2: Checklist visual light mode**

Run: `streamlit run app.py`, subir CSV de exemplo, light mode. Conferir:
  - Títulos em sans bold (sem serifa)
  - Accent slate em tabs/hover/foco/barra dos cards
  - Visão Geral na ordem nova (cards → donut full-width → histórico full-width)
  - Donut e histórico com a mesma paleta sóbria por categoria, sem clash
  - Fundo cinza-claro Apple `#F2F2F7`

- [ ] **Step 3: Checklist visual dark mode**

Toggle 🌙 no header. Repetir o checklist do Step 2 no dark — accent slate claro `#7B9CC4`, contraste OK, gráficos legíveis.

- [ ] **Step 4: Conferir as outras abas**

Navegar em Transações, Recorrências, Parcelas Futuras — confirmar que herdaram o tema novo (sans, accent slate, cards) sem quebra de layout.

- [ ] **Step 5: Commit final (se houver ajuste pendente)**

```bash
git add -A
git commit -m "chore: verificacao final do redesign visual iOS"
```

---

## Notas de escopo

**Fora deste plano** (features futuras, não implementar): diagnóstico narrativo em texto, novos bancos/contas/receita, pergunta em linguagem natural, metas de poupança.

**Critério de sucesso geral:** app com aparência iOS coesa (sans, cards arredondados, respiro, accent slate), gráficos harmônicos sem clash, light+dark consistentes, Visão Geral na ordem validada, zero regressão de dados/comportamento.
