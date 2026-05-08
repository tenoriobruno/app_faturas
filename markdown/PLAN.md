# PLAN.md — MVP Finanças Pessoais

## 1. Responsabilidade de cada arquivo

### `app.py`
Streamlit entry point. Imports e orquestra todos os módulos.
- Renderiza sidebar com filtros (mês, categoria)
- Chama `parsers/nubank.py` no upload
- Chama `classifier/engine.py` para classificar
- Chama `utils/storage.py` para persistir e carregar
- Renderiza cards de resumo, gráficos Plotly, tabela editável
- Aplica `assets/styles.css` via `st.markdown`

### `parsers/nubank.py`
Input: arquivo CSV do Nubank (bytes).  
Output: `pd.DataFrame` com colunas `[date, description, amount, category]`.
- Detecta encoding (tenta UTF-8, fallback latin-1)
- Lê CSV com pandas
- Renomeia colunas para padrão interno (`Data` → `date`, `Descrição` → `description`, `Valor` → `amount`)
- Deduplica por `(date, description, amount)`
- Sinaliza estornos (amount > 0) com `category = "ESTORNO"`

### `classifier/engine.py`
Input: `pd.DataFrame`.  
Output: mesmo DataFrame com coluna `category` preenchida.
- Para cada linha sem categoria:
  1. Chama `normalize.normalize(description)`
  2. Consulta `storage.get_cache(normalized)`
  3. Chama `local_rules.classify(normalized)`
  4. Chama `ai_classifier.classify(normalized)` se local falhar
  5. Chama `storage.set_cache(normalized, category)`
- Retorna DataFrame completo

### `classifier/local_rules.py`
Input: string normalizada.  
Output: categoria string ou `None`.
- Carrega `categories.json` uma vez (module-level singleton)
- Tenta keyword match (substring)
- Tenta regex match
- Tenta fuzzy token match (token overlap ratio ≥ 0.8)
- Retorna primeira categoria que bate, ou `None`

### `classifier/ai_classifier.py`
Input: string normalizada.  
Output: categoria string.
- Instancia cliente Anthropic (API key via `.env`)
- Prompt contém lista de categorias válidas + instrução de retornar apenas o nome da categoria
- Modelo: `claude-haiku-3-5-20251001`
- Max tokens: 20 (resposta é só o nome da categoria)
- Fallback categoria: `"Outros"` se resposta inválida

### `utils/normalize.py`
Input: string raw da descrição.  
Output: string limpa.
- Lowercase
- Remove `XX/YY` (parcelas)
- Remove tokens puramente numéricos ou alfanuméricos com 6+ chars
- Remove `*` e chars especiais
- Remove tokens < 2 chars
- Strip e collapse whitespace

### `utils/storage.py`
Dois tipos de persistência:
1. **Cache** (`cache/categories_cache.json`): dict `{normalized_description: category}`. Carrega em memória no startup, salva após cada nova entrada.
2. **Dados** (`data/transacoes_YYYY-MM.json`): lista de dicts por mês. Salva DataFrame completo após classificação.

### `categories.json`
Estrutura:
```json
{
  "Alimentação": {
    "keywords": ["ifood", "restaurante", "lanche", "pizza", "burger"],
    "regex": ["ifood.*pedido", "uber.*eat"]
  },
  "Transporte": {
    "keywords": ["uber", "99", "cabify", "onibus", "metro"],
    "regex": ["uber.*trip", "99.*taxi"]
  },
  ...
}
```

### `assets/styles.css`
CSS injetado via `st.markdown("<style>...</style>")`.
- Oculta header, footer, menu hamburguer do Streamlit
- Define paleta dark (fundo `#0f1117`, cards `#1e2130`)
- Font: Inter ou system-ui
- Cards com `border-radius: 12px`, `box-shadow`

---

## 2. Fluxo completo passo a passo

```
1. Usuário faz upload do CSV no Streamlit
        ↓
2. parsers/nubank.py
   - Detecta encoding
   - Parse pandas
   - Renomeia colunas
   - Deduplica
   - Sinaliza estornos
        ↓
3. classifier/engine.py — para cada transação:
   a. normalize.normalize(description)
   b. storage.get_cache(normalized)  → se hit: usa categoria, pula para próxima
   c. local_rules.classify(normalized)  → se match: salva cache, próxima
   d. ai_classifier.classify(normalized)  → salva cache, próxima
        ↓
4. utils/storage.py
   - Salva DataFrame em data/transacoes_YYYY-MM.json
   - Persiste cache atualizado em cache/categories_cache.json
        ↓
5. app.py renderiza:
   - Cards: total gasto, maior categoria, nº transações, % classificado local
   - Gráfico pizza: gasto por categoria (Plotly)
   - Gráfico barras: gasto por dia (Plotly)
   - Tabela editável: st.data_editor com coluna categoria como selectbox
        ↓
6. Usuário edita categoria na tabela
   - app.py detecta mudança via st.session_state
   - Atualiza DataFrame
   - Chama storage.set_cache(normalized, nova_categoria) — aprende
   - Re-renderiza gráficos
        ↓
7. Usuário clica "Exportar CSV"
   - app.py gera CSV via DataFrame.to_csv()
   - st.download_button entrega arquivo
```

---

## 3. Estratégia de economia de tokens

Ordem obrigatória no `engine.py` antes de qualquer chamada IA:

| Passo | Economia esperada |
|-------|-------------------|
| 1. Normalização | Remove ruído, aumenta cache hit rate |
| 2. Cache lookup | ~60% das transações (recorrentes) |
| 3. Keywords | ~25% do restante |
| 4. Regex | ~8% do restante |
| 5. Fuzzy match | ~4% do restante |
| 6. IA (Haiku) | ≤ 3% das transações totais |

Meta: IA chamada em menos de 15% das transações. Estimativa real: ~3-5%.

Cache persiste entre sessões → primeira importação paga custo maior, subsequentes quase zero.

---

## 4. Estratégia de normalização

```python
# utils/normalize.py

import re

def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\b\d{1,2}/\d{1,2}\b', '', text)      # parcelas: 01/12
    text = re.sub(r'[*]', ' ', text)                       # asterisco separador
    text = re.sub(r'[^a-z0-9 ]', '', text)                # chars especiais
    tokens = text.split()
    tokens = [t for t in tokens if len(t) >= 2]            # remove tokens < 2 chars
    tokens = [t for t in tokens if not re.match(r'^[a-z0-9]{6,}$', t) or t.isalpha()]  # remove IDs
    return ' '.join(tokens).strip()
```

Exemplos validados:
```
"UBER TRIP 123ABC"       → "uber trip"
"IFOOD *PEDIDO"          → "ifood pedido"
"MERCPAGO*LOJA123"       → "mercpago"
"COMPRA PARCELADA 01/12" → "compra parcelada"
"AMAZON.COM.BR 9F3X2"   → "amazon com br"
```

---

## 5. Casos extremos a tratar

| Caso | Onde tratar | Como |
|------|-------------|------|
| CSV vazio | `parsers/nubank.py` | Checar `len(df) == 0`, retornar erro legível |
| CSV corrompido | `parsers/nubank.py` | Try/except no `pd.read_csv`, mensagem clara |
| Encoding inesperado | `parsers/nubank.py` | `try utf-8 except UnicodeDecodeError: latin-1` |
| Upload duplicado | `parsers/nubank.py` | `drop_duplicates(subset=['date','description','amount'])` |
| Estorno (amount > 0) | `parsers/nubank.py` | `category = "ESTORNO"`, skip classificação |
| Parcelamento | `utils/normalize.py` | Regex `\d{1,2}/\d{1,2}` remove antes de processar |
| Compra internacional | `classifier/local_rules.py` | Keyword "dolar", "usd", "compra internacional" → categoria "Internacional" |
| API key ausente | `classifier/ai_classifier.py` | `os.getenv("ANTHROPIC_API_KEY")` — se None, logar warning, retornar "Outros" |
| Haiku resposta inválida | `classifier/ai_classifier.py` | Checar se resposta está em lista de categorias válidas, fallback "Outros" |

---

## 6. Estratégia visual Streamlit

### Ocultar chrome padrão
```css
/* assets/styles.css */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {padding-top: 1rem;}
```

### Layout
```
Sidebar          | Main content
─────────────────┼───────────────────────────────
Filtro: mês      | [Card total] [Card categ] [Card nº]
Filtro: categ    | ─────────────────────────────────
Upload CSV       | [Pizza: gasto/categ] [Barras: gasto/dia]
                 | ─────────────────────────────────
                 | [Tabela editável: data|desc|valor|categ]
                 | [Botão: Exportar CSV]
```

### Paleta dark
```css
:root {
  --bg: #0f1117;
  --card: #1e2130;
  --accent: #00d4aa;  /* verde fintech */
  --text: #e0e0e0;
  --muted: #8892a4;
}
```

### Cards (via `st.columns` + `st.markdown`)
```html
<div class="metric-card">
  <div class="metric-label">Total Gasto</div>
  <div class="metric-value">R$ 3.240,50</div>
</div>
```

---

## 7. Plano incremental de execução

### Passo 1 — Scaffold
**Implementar**: criar todos os arquivos com stubs (funções vazias, imports).  
**Testar**: `python -c "import app"` sem erros de import.  
**Critério**: todos os módulos importáveis.

### Passo 2 — Parser Nubank
**Implementar**: `parsers/nubank.py` completo com encoding detection e dedup.  
**Testar**: `python -c "from parsers.nubank import parse; df = parse('sample.csv'); print(df.head())"` com CSV real do Nubank.  
**Critério**: DataFrame com colunas corretas, sem duplicatas, estornos sinalizados.

### Passo 3 — Normalização
**Implementar**: `utils/normalize.py` completo.  
**Testar**: script inline com os 10 exemplos reais do Nubank.  
**Critério**: todos os exemplos produzem saída esperada.

### Passo 4 — categories.json + local_rules
**Implementar**: `categories.json` com 10+ categorias e 50+ keywords. `classifier/local_rules.py` com keyword + regex + fuzzy.  
**Testar**: script classifica lista de 20 descrições normalizadas conhecidas.  
**Critério**: ≥ 80% corretas sem IA.

### Passo 5 — Storage + Cache
**Implementar**: `utils/storage.py` com load/save cache e dados.  
**Testar**: salva dict, relê, confirma persistência. Salva DataFrame, relê.  
**Critério**: round-trip sem perda de dados.

### Passo 6 — Engine de classificação
**Implementar**: `classifier/engine.py` orquestrando passos 1-5 (sem IA ainda).  
**Testar**: classifica DataFrame real, verifica % classificado localmente.  
**Critério**: ≥ 85% classificado localmente.

### Passo 7 — AI fallback
**Implementar**: `classifier/ai_classifier.py` com prompt enxuto.  
**Testar**: classifica 5 descrições que local_rules falhou. Verificar custo no Anthropic console.  
**Critério**: resposta válida (categoria na lista), custo < $0.01 para 5 chamadas.

### Passo 8 — UI básica funcional
**Implementar**: `app.py` com upload → parse → classify → tabela simples.  
**Testar**: `streamlit run app.py`, upload CSV real, ver tabela classificada.  
**Critério**: fluxo completo funciona end-to-end.

### Passo 9 — Dashboard visual
**Implementar**: cards de métricas, gráficos Plotly, CSS dark theme.  
**Testar**: visual no browser, checar responsividade sidebar.  
**Critério**: parece fintech, não Streamlit padrão.

### Passo 10 — Edição manual + export
**Implementar**: `st.data_editor` com selectbox de categoria, botão export, aprendizado de edições no cache.  
**Testar**: editar categoria → re-exportar → reimportar mesmo CSV → categoria já correta.  
**Critério**: edição persiste via cache no próximo upload.

---

## 8. Estimativa de custo

### Distribuição esperada de classificação
| Método | % transações |
|--------|-------------|
| Cache hit (2ª importação+) | 60% |
| Keywords | 20% |
| Regex | 8% |
| Fuzzy | 7% |
| IA (Haiku) | **5%** |

### Custo IA por 100 transações
- 5 chamadas IA por 100 transações
- Prompt ~200 tokens (lista categorias + instrução) + ~10 tokens input + ~5 tokens output = ~215 tokens/chamada
- Haiku pricing: $0.80/M input tokens, $4.00/M output tokens
- Input: 5 × 210 tokens = 1050 tokens = $0.00084
- Output: 5 × 5 tokens = 25 tokens = $0.0001
- **Total: ~$0.001 por 100 transações** (meta < $0.05 ✓, margem 50x)

### Custo total desenvolvimento
- Sessão de planejamento: ~$0.01
- Sessão de execução (estimada): ~$0.10–0.20
- Testes com dados reais: ~$0.05
- **Total estimado: ~$0.20–0.30** (meta < $1 ✓)
