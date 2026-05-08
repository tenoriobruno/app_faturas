# 🔍 Diagnóstico de Design — Finanças Pessoais

> Análise realizada em 02/05/2026 com base no dashboard rodando localmente via Streamlit.

---

## 1. PROBLEMAS VISUAIS

### 🔴 O gráfico de pizza é dominado por "Outros" (50.9%)

Metade da pizza é cinza. Isso mata a utilidade do gráfico inteiro — o propósito de um pie chart é mostrar composição de gastos, mas quando metade é "não sei", o gráfico comunica **"a classificação não está funcionando"** em vez de informação financeira útil. As fatias menores (Restaurante, Saúde, Feira, Gasolina) ficam comprimidas ao ponto de serem ilegíveis, com labels se sobrepondo.

### 🔴 Delivery e Outros têm a mesma cor cinza na legenda

No `CATEGORY_COLORS` do `app.py` (linhas 206-223), "Outros" usa `#94A3B8` (cinza) mas "Delivery" **não tem cor definida** no mapa — cai no fallback `#94A3B8` (o mesmo cinza). No gráfico de barras, a legenda mostra dois retângulos cinza idênticos lado a lado para categorias completamente diferentes. Isso não é um detalhe estético — é um bug visual que impede a leitura do gráfico.

### 🟡 O gráfico de barras empilhadas está visualmente confuso

Cada barra tem 7-9 categorias empilhadas com porcentagens dentro. Os textos `12%`, `13%`, `15%` ficam apertados nas fatias menores. A quantidade de informação por barra é excessiva — o olho não sabe para onde ir. O gráfico quer mostrar tendência temporal E composição ao mesmo tempo, e não faz nenhum dos dois bem.

### 🟡 Os cards de métricas não têm hierarquia visual

Os 4 cards (Transações, Valor Total, Ticket Médio, Maior Categoria) são visualmente idênticos: mesma cor, mesmo tamanho, mesmo peso. O "Valor Total: R$ 4.028,05" deveria ser o dado mais proeminente da página, mas compete igualmente com "Transações: 127" que é informação secundária.

### 🟡 Background gradiente azul claro compete com os cards brancos

O contraste entre background (`#D6E4F7`) e cards (`#FFFFFF`) é baixo. Os cards não "saltam" — parecem flutuar num mar de lavanda sem ancoragem visual. A sombra `0 4px 24px rgba(0,0,0,0.07)` é sutil demais para compensar.

### 🟠 A mensagem de sucesso verde é ruído visual

O banner "✅ Arquivo carregado: Nubank_2025-12-28.csv" ocupa largura total e é mostrado permanentemente. Após o primeiro segundo, essa informação é irrelevante. Ela empurra os gráficos para baixo e adiciona peso visual sem valor.

---

## 2. PROBLEMAS DE USABILIDADE

### 🔴 A hierarquia de dados está invertida

O primeiro elemento que o usuário vê é o **gráfico de barras histórico consolidado** (dados de todos os CSVs). Só depois ele encontra o **seletor de CSV**, e então os dados do arquivo individual. Problema: o usuário abre o dashboard querendo ver **"quanto gastei esse mês?"**, e a primeira coisa que encontra é um gráfico de 12 meses que exige interpretação. A resposta simples (R$ 4.028,05) está escondida em um card no rodapé da página.

### 🔴 O seletor de CSV está perdido no meio da página

O dropdown "SELECIONE O ARQUIVO CSV" aparece entre o gráfico de barras e o pie chart — no meio do conteúdo, sem destaque visual. Não parece um controle; parece mais um campo de formulário abandonado. O label "SELECIONE O ARQUIVO CSV" em uppercase cinza é fácil de ignorar. Esse controle deveria estar no topo ou numa sidebar — é uma ação primária de navegação, não conteúdo.

### 🟡 A tabela de dados está escondida em expander

A tabela "📋 Ver Dados" está colapsada por padrão num `st.expander`. Para um engenheiro de dados, os dados brutos são frequentemente o conteúdo mais importante. Esconder atrás de um clique é uma decisão que prioriza "limpeza visual" sobre usabilidade real.

### 🟡 "Maior Categoria: Outros" é informação que desmotiva

O card mostra "Maior Categoria: Outros" — literalmente comunicando ao usuário que o sistema **falhou** em classificar a maioria das transações. Esse dado deveria ou excluir "Outros" do cálculo, ou não existir enquanto a taxa de classificação for < 80%.

### 🟠 Não há contexto temporal nos cards

"Valor Total: R$ 4.028,05" — de que período? O card não diz. O usuário precisa olhar o seletor de CSV e inferir pela data do nome do arquivo. Sem rótulo temporal, o número perde significado.

### 🟠 Processamento duplicado no código

O `app.py` processa e classifica todos os CSVs no loop consolidado (linhas 190-198), e depois **processa o mesmo arquivo novamente** no bloco individual (linhas 330-333). Isso não é visível ao usuário, mas causa lentidão desnecessária — cada CSV é parseado e classificado duas vezes.

---

## 3. HIERARQUIA DE INFORMAÇÃO

### O que o olho vê primeiro (ordem atual):

1. Título "💰 Finanças Pessoais"
2. Gráfico de barras empilhadas (domina a tela)
3. Legenda de categorias
4. Seletor de CSV
5. Banner verde de sucesso
6. Pie chart + cards de resumo (abaixo da dobra)

### O que o olho DEVERIA ver primeiro:

1. **Quanto gastei este mês** → R$ 4.028,05 (grande, central, acima da dobra)
2. **Onde gastei mais** → Breakdown por categoria (pie chart ou barras horizontais)
3. **Tendência** → Estou gastando mais ou menos que o mês passado?
4. **Detalhes** → Tabela de transações + gráfico temporal

> **IMPORTANTE:** A informação mais valiosa (valor total + composição do mês selecionado) está **abaixo da dobra**. O usuário precisa rolar para encontrar o que deveria ser a primeira coisa que ele vê. O gráfico consolidado de 12 meses, embora útil, é informação de contexto — deveria vir depois, não antes.

---

## 4. QUICK FIXES (3 sugestões)

### Quick Fix 1: Inverter a ordem — Cards e Pie ACIMA, Barras ABAIXO

**Problema:** A informação primária (resumo do mês) está abaixo da dobra enquanto o gráfico histórico (informação secundária) domina o topo.

**Correção:** No `app.py`, mover a seção de cards + pie chart para cima do gráfico de barras consolidado. Reorganizar:

1. Seletor de CSV (com label melhor)
2. Cards de resumo em linha horizontal
3. Pie chart donut (não pizza sólida)
4. Gráfico de barras históricas (embaixo)
5. Tabela

```diff
 st.markdown(css, unsafe_allow_html=True)
 st.title("💰 Finanças Pessoais")

+# === FILE SELECTOR (primeiro) ===
+# === CARDS + PIE (segundo) ===
+# === BAR CHART (terceiro) ===
-# === BAR CHART (primeiro — ERRADO) ===
-# === FILE SELECTOR (no meio — ERRADO) ===
-# === CARDS + PIE (último — ERRADO) ===
```

**Impacto:** O usuário abre o dashboard e imediatamente vê "R$ 4.028,05 este mês", sem rolar. A pergunta principal é respondida em < 1 segundo.

---

### Quick Fix 2: Adicionar cor para Delivery e corrigir "Outros" na pizza

**Problema:** Delivery e Outros compartilham o mesmo cinza. "Outros" com 50.9% domina a pizza inutilmente.

**Correção em 2 partes:**

**Parte A** — Adicionar cor para Delivery no `CATEGORY_COLORS`:

```diff
 CATEGORY_COLORS = {
+    'Delivery': '#1E293B',
     'Alimentação': '#8A05BE',
     ...
 }
```

**Parte B** — Converter pie chart em donut e mostrar o valor total no centro:

```python
hole=0.45  # ao invés de hole=0.0
```

**Impacto:** Cada categoria é visualmente distinta. O donut com total no centro dá um duplo-propósito ao gráfico (composição + total). O cinza de "Outros" fica menos dominante visualmente quando é um anel fino em vez de uma fatia enorme.

---

### Quick Fix 3: Remover o banner de sucesso e adicionar período ao título da seção

**Problema:** "✅ Arquivo carregado: Nubank_2025-12-28.csv" é ruído permanente. Os cards não dizem de que período são.

**Correção:**

```diff
-    st.success(f"✅ Arquivo carregado: {selected_file.name}")
-    st.write(f"Total de transações: **{len(df)}**")
+    # Extrair período do nome do arquivo ou dos dados
+    min_date = df['date'].min()
+    max_date = df['date'].max()
+    st.caption(f"📅 {min_date} a {max_date} · {len(df)} transações · {selected_file.name}")
```

**Impacto:** Libera ~80px de espaço vertical. O contexto temporal fica visível ao lado das métricas. O usuário sabe exatamente de que período está olhando.

---

## Resumo de Prioridades

| # | Quick Fix | Esforço | Impacto |
|---|-----------|---------|---------|
| 1 | Inverter layout: cards+pie no topo, barras embaixo | ~5 min | O total do mês aparece sem scroll |
| 2 | Adicionar cor para Delivery + converter pie em donut | ~2 min | Gráficos ficam legíveis |
| 3 | Trocar banner de sucesso por caption com datas | ~3 min | Remove ruído, adiciona contexto temporal |

> **Recomendação:** Executar nesta ordem. Os dois primeiros são mudanças de 5 minutos cada com impacto imediato na experiência.
