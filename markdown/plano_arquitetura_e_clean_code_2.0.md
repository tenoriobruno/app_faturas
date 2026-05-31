# Plano de Arquitetura e Clean Code 2.0

> Auditoria completa do projeto `app_faturas` — **16/05/2026**

---

## 1. Mapa de Arquitetura Atual

```
app.py ──► parsers/nubank.py
       ──► classifier/engine.py ──► local_rules.py ──► categories.json
       │                        ──► llm_fallback.py ──► categories.json
       │                        ──► utils/normalize.py
       │                        ──► data/repository.py ──► config/settings.py
       ──► config/theme.py
       ──► components/sidebar.py ──► utils/filters.py
       ──► utils/export.py
       ──► views/overview.py ──► components/charts.py ──► config/theme.py
       │                    ──► components/budget.py ──► data/repository.py
       ──► views/transactions.py ──► data/repository.py
       │                        ──► utils/normalize.py
       ──► views/recurrences.py ──► core/recurrences.py
       ──► views/installments.py ──► core/installments.py
                                ──► config/theme.py
```

### Inventário de Arquivos (20 arquivos Python + 4 config)

| Camada | Módulo | Linhas | Responsabilidade |
|--------|--------|--------|------------------|
| **Entry** | `app.py` | 89 | Orquestração, upload, cache, roteamento |
| **Parser** | `parsers/nubank.py` | 82 | Leitura CSV, dedup, extração de parcelas |
| **Classifier** | `classifier/engine.py` | 75 | Pipeline de classificação com cache |
| | `classifier/local_rules.py` | 44 | Keywords + regex contra `categories.json` |
| | `classifier/llm_fallback.py` | 49 | Fallback via Gemini (não Haiku) |
| **Core** | `core/recurrences.py` | 28 | Detecção de despesas fixas |
| | `core/installments.py` | 20 | Cálculo de parcelas futuras |
| **Data** | `data/repository.py` | 41 | Persistência JSON genérica |
| **Views** | `views/overview.py` | 56 | Aba Visão Geral |
| | `views/transactions.py` | 39 | Aba Transações (data_editor) |
| | `views/recurrences.py` | 29 | Aba Recorrências |
| | `views/installments.py` | 59 | Aba Parcelas Futuras |
| **Components** | `components/charts.py` | 131 | Donut + Barras empilhadas |
| | `components/budget.py` | 64 | Orçamento com progress bars |
| | `components/sidebar.py` | 49 | Filtros da sidebar |
| **Utils** | `utils/filters.py` | 36 | Lógica pura de filtragem |
| | `utils/normalize.py` | 42 | Normalização de texto |
| | `utils/export.py` | 17 | Botão de download CSV |
| | `utils/logger.py` | 13 | Factory de logger |
| **Config** | `config/settings.py` | 17 | Caminhos centralizados |
| | `config/theme.py` | 138 | CSS + cores + layout Plotly |

---

## 2. Problemas Identificados

### 🔴 Críticos

#### P1 — CSS duplicado e não utilizado
- `config/theme.py` contém **104 linhas de CSS inline** (variável `CSS`).
- `assets/styles.css` contém **42 linhas de CSS** com regras diferentes (select boxes).
- O `assets/styles.css` **nunca é carregado** — não há nenhum `st.markdown` ou `open()` que o consuma.
- **Resultado:** CSS morto no repositório; duas fontes de verdade para estilos.

#### P2 — Lista de categorias hardcoded em 3 lugares
- `categories.json` → fonte de verdade (16 categorias).
- `config/theme.py` → `CATEGORY_COLORS` dict (16 chaves).
- `views/transactions.py` → lista literal hardcoded no `SelectboxColumn` (16 strings).
- **Resultado:** Ao adicionar uma nova categoria, é preciso editar 3 arquivos manualmente.

#### P3 — `CLAUDE.md` desatualizado (documentação mente)
- Referencia `utils/storage.py` → **deletado**.
- Referencia `classifier/ai_classifier.py` → **não existe** (é `llm_fallback.py`).
- Diz que usa `anthropic` SDK / `claude-haiku` → o código usa **`google.generativeai` / Gemini**.
- Descreve "fuzzy token match" como step 5 → **não existe** no código.
- A seção "Architecture" não menciona `views/`, `core/`, `data/`, `components/`.
- **Resultado:** Qualquer agente AI ou dev que ler o CLAUDE.md vai tomar decisões erradas.

#### P4 — `__init__.py` faltando em `core/`, `data/`, `views/`
- Esses 3 packages não têm `__init__.py`.
- Funciona por acaso porque o Streamlit adiciona o diretório raiz ao `sys.path`, mas quebraria em qualquer outro contexto (testes, scripts CLI, import por ferramentas de análise estática).

### 🟡 Moderados

#### P5 — `config/settings.py` existe mas é parcialmente ignorado
- `app.py` faz seu próprio `load_dotenv()` + `Path(os.getenv("DATA_PATH"))` na linha 20-21, **ignorando** `settings.DATA_PATH`.
- `local_rules.py` constrói o path do `categories.json` manualmente (`Path(__file__).parent.parent / "categories.json"`) em vez de usar `settings.CATEGORIES_PATH`.
- `llm_fallback.py` lê `os.getenv("GEMINI_API_KEY")` diretamente, ignorando `settings.GEMINI_API_KEY`.
- **Resultado:** O `Settings` centralizado é uma ilusão — metade do código o ignora.

#### P6 — `load_dotenv()` chamado 2 vezes
- `config/settings.py` linha 5: `load_dotenv()`.
- `app.py` linha 20: `load_dotenv()`.
- Não é destrutivo, mas demonstra falta de ponto único de inicialização.

#### P7 — Cache em memória com global mutável (`engine.py`)
- `_cache` é um `dict` global mutável, carregado via `get_cache()`.
- `classify_batch()` muta esse dict in-place e depois salva.
- Não é thread-safe e o estado sobrevive entre reruns do Streamlit de forma imprevisível.
- A função `get_cache()` é exportada e usada em `views/transactions.py` implicitamente (via `cache_repo.load()` diretamente).

#### P8 — `requirements.txt` com dependência fantasma
- Lista `anthropic==0.21.0` — mas o código **não importa** a lib `anthropic` em nenhum lugar.
- Usa `google.generativeai` que **não está listada** no requirements.
- **Resultado:** `pip install -r requirements.txt` instala lib inútil e não instala a necessária.

### 🟢 Menores

#### P9 — Pasta `images/` com screenshots órfãos
- 4 arquivos (269KB + 339KB + 30KB + 57KB) que não são referenciados por nenhum código.
- Provavelmente screenshots de desenvolvimento. Poluem o repositório.

#### P10 — `components/__init__.py` tem conteúdo vazio mas ocupa espaço (2 bytes)
- Inconsistência: `classifier/__init__.py`, `parsers/__init__.py`, `utils/__init__.py` também existem (vazios). São necessários, mas `core/`, `data/`, `views/` não os têm.

#### P11 — `utils/filters.py` importa `streamlit` mas não o usa
- Linha 2: `import streamlit as st` — nunca referenciado no corpo da função.

#### P12 — `Estorno` como categoria com keyword no `categories.json`
- O parser já identifica estornos pelo valor negativo (`tipo_transacao = 'estorno'`).
- Ter "Estorno" como categoria no JSON é redundante e pode gerar conflito (uma transação seria classificada como "Estorno" pela keyword E como `tipo_transacao='estorno'` pelo parser).

---

## 3. Tarefas de Refatoração

### Tarefa 1 — Single Source of Truth para Categorias
**Impacto: Alto | Esforço: Baixo**

- [ ] Criar função `get_category_names()` em `config/settings.py` que lê `categories.json` e retorna a lista de nomes.
- [ ] `config/theme.py` → `CATEGORY_COLORS` deve validar que suas chaves correspondem ao JSON (ou ser gerado a partir dele).
- [ ] `views/transactions.py` → substituir lista hardcoded por `list(CATEGORY_COLORS.keys())` (já importado em outros módulos).
- [ ] `local_rules.py` → usar `settings.CATEGORIES_PATH` em vez de path manual.
- [ ] `llm_fallback.py` → usar `settings.CATEGORIES_PATH` em vez de path manual.

### Tarefa 2 — Consolidar CSS e remover código morto
**Impacto: Médio | Esforço: Baixo**

- [ ] Mover o conteúdo de `assets/styles.css` para dentro de `config/theme.py` (fundir os dois CSS).
- [ ] **OU** extrair o CSS de `config/theme.py` para `assets/styles.css` e carregá-lo via `open()` no `app.py`.
- [ ] Deletar o arquivo que sobrar (eliminar duplicidade).
- [ ] Decisão recomendada: manter tudo em `config/theme.py` (inline) pois o projeto é Streamlit e não tem build step para assets.

### Tarefa 3 — Centralizar inicialização via `settings`
**Impacto: Alto | Esforço: Baixo**

- [ ] `app.py` → remover `load_dotenv()` e `Path(os.getenv(...))`. Usar `from config.settings import settings` → `settings.DATA_PATH`.
- [ ] `llm_fallback.py` → usar `settings.GEMINI_API_KEY` em vez de `os.getenv()`.
- [ ] `local_rules.py` → usar `settings.CATEGORIES_PATH`.
- [ ] Garantir que `config/settings.py` é o **único** lugar que chama `load_dotenv()`.

### Tarefa 4 — Atualizar `CLAUDE.md` e `requirements.txt`
**Impacto: Alto | Esforço: Baixo**

- [ ] Reescrever seção "Architecture" do `CLAUDE.md` refletindo a árvore real (`views/`, `core/`, `data/`, `components/`).
- [ ] Corrigir referências: `storage.py` → `data/repository.py`, `ai_classifier.py` → `llm_fallback.py`.
- [ ] Corrigir stack: `anthropic` → `google-generativeai`.
- [ ] Remover step "fuzzy token match" do pipeline.
- [ ] `requirements.txt`: remover `anthropic`, adicionar `google-generativeai`.

### Tarefa 5 — Adicionar `__init__.py` faltantes e limpar imports
**Impacto: Médio | Esforço: Mínimo**

- [ ] Criar `core/__init__.py`, `data/__init__.py`, `views/__init__.py` (vazios).
- [ ] `utils/filters.py` → remover `import streamlit as st` (não usado).
- [ ] `views/transactions.py` → mover imports de `data.repository` e `utils.normalize` para o topo do arquivo.

### Tarefa 6 — Limpar repositório de arquivos órfãos
**Impacto: Baixo | Esforço: Mínimo**

- [ ] Avaliar se `images/` tem valor documental. Se não, deletar a pasta.
- [ ] Adicionar `images/` ao `.gitignore` se decidir manter localmente.
- [ ] Avaliar se os 13 arquivos `.md` em `markdown/` podem ser consolidados (muitos são versões anteriores do mesmo plano).

---

## 4. Estrutura-Alvo Pós-Refatoração

```
app_faturas/
├── .env                          # DATA_PATH, GEMINI_API_KEY
├── .gitignore
├── .streamlit/config.toml
├── CLAUDE.md                     # ✅ Atualizado
├── README.md
├── requirements.txt              # ✅ Corrigido
├── categories.json
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # ✅ Single load_dotenv(), paths centralizados
│   ├── theme.py                  # ✅ CSS consolidado + cores + layout
│   └── budget.json
│
├── parsers/
│   ├── __init__.py
│   └── nubank.py
│
├── classifier/
│   ├── __init__.py
│   ├── engine.py
│   ├── local_rules.py            # ✅ Usa settings.CATEGORIES_PATH
│   └── llm_fallback.py           # ✅ Usa settings.GEMINI_API_KEY
│
├── core/
│   ├── __init__.py               # ✅ Novo
│   ├── recurrences.py
│   └── installments.py
│
├── data/
│   ├── __init__.py               # ✅ Novo
│   └── repository.py
│
├── views/
│   ├── __init__.py               # ✅ Novo
│   ├── overview.py
│   ├── transactions.py           # ✅ Sem lista hardcoded
│   ├── recurrences.py
│   └── installments.py
│
├── components/
│   ├── __init__.py
│   ├── charts.py
│   ├── budget.py
│   └── sidebar.py
│
├── utils/
│   ├── __init__.py
│   ├── filters.py                # ✅ Sem import st desnecessário
│   ├── normalize.py
│   ├── export.py
│   └── logger.py
│
├── cache/
│   └── categories_cache.json
│
└── markdown/                     # Documentação histórica
    └── *.md
```

> **Nota:** `assets/styles.css` removido (CSS consolidado em `config/theme.py`).

---

## 5. Critérios de Validação

| Tarefa | Validação |
|--------|-----------|
| T1 | `grep -r "Delivery.*Alimentação.*Transporte" views/` retorna 0 resultados |
| T2 | `ls assets/styles.css` retorna "not found" |
| T3 | `grep -r "load_dotenv" .` retorna apenas `config/settings.py` |
| T4 | `grep "anthropic" requirements.txt` retorna 0; `grep "storage.py" CLAUDE.md` retorna 0 |
| T5 | `find . -name "__init__.py" -not -path "./.git/*" | wc -l` retorna **8** |
| T6 | `ls images/` retorna "not found" ou pasta listada no `.gitignore` |

---

## 6. Ordem de Execução Recomendada

```
T5 (init.py) → T3 (settings) → T1 (categorias) → T2 (CSS) → T4 (docs) → T6 (limpeza)
```

T5 primeiro porque é pré-requisito de qualidade. T3 antes de T1 porque T1 depende de `settings.CATEGORIES_PATH` estar em uso.
