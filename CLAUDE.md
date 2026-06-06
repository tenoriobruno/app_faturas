# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## Project Overview

Personal finance MVP inspired by Guiabolso. Not SaaS — personal use only, no scalability requirements. Processes Nubank CSV exports and categorizes transactions using local rules with AI fallback.

**Budget constraint**: < $1 total development cost, < $0.05 per 100 classified transactions. AI must be called for fewer than 15% of transactions.

## Stack

- Python 3.9+, Streamlit, Pandas, Plotly, python-dotenv
- Pytest for tests
- No linting/formatter configured (match existing style)

## Commands

```bash
# Create venv (Python 3.9+ required)
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Run tests (from project root)
python -m pytest tests/ -v

# Run single test file
python -m pytest tests/test_ui.py -v
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATA_PATH` | `.` | Directory where Nubank CSVs are stored |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Architecture

Data flow: `Upload CSV → Parse → Normalize → Classify → Cache/Save → Display/Edit → Export`

```
app.py                        # Streamlit entry, wires all modules
config/
  settings.py                 # Centralized settings + env loader (Settings class)
  theme.py                    # Custom CSS, dark/light mode, category colors
  categories.py               # CATEGORY_COLORS dict (17 categories, hex palette)
parsers/nubank.py             # CSV parsing, encoding detection, dedup, installments
classifier/
  engine.py                   # Orchestrates classification pipeline (classify_batch)
  local_rules.py              # Keyword + regex matching against categories.json
core/
  metrics.py                  # Overview metrics (total, avg, deltas vs prev month)
  installments.py             # Groups installment purchases, keeps most recent entry
  recurrences.py              # Detects subscriptions (3+ months or "Assinaturas" cat)
services/
  classification.py           # save_manual_corrections — persists user reclassifications to cache
data/
  repository.py               # JSONRepository (generic) + CacheRepository (with migration + staleness)
                              # cache_repo + budget_repo singletons
views/
  overview.py                 # Visão Geral tab — charts, metrics, budget
  transactions.py             # Transações tab — editable table + filters
  recurrences.py              # Recorrências tab — detected subscriptions
  installments.py             # Parcelas Futuras tab — pending installments
components/
  sidebar.py                  # Filter sidebar (search, categories, value range, date range)
  charts.py                   # Plotly charts (donut, bar)
  metrics.py                  # Metric cards (total, avg, top category)
  header.py                   # App header with dark mode toggle
  budget.py                   # Budget tracking + editor (global + per-category)
utils/
  normalize.py                # Text normalization for classification matching
  filters.py                  # apply_filters — DataFrame filtering pipeline
  export.py                   # CSV export button
  logger.py                   # get_logger — configured StreamHandler
cache/categories_cache.json   # Persistent cache keyed by normalized description
categories.json               # Keyword/regex patterns per category
config/budget.json            # Saved budget limits (global + per-category dicts)
```

## Key Files

### `config/settings.py`

Singleton `Settings` class loaded from `.env`. Key paths: `DATA_PATH`, `CACHE_PATH`, `BUDGET_PATH`, `CATEGORIES_PATH`. Exposes `get_category_names()`.

### `data/repository.py`

Two repositories:
- **JSONRepository** — generic JSON read/write with error handling
- **CacheRepository** — extends JSONRepository with migration from old string format to `{categoria, source}` dict format. Has `invalidate_if_stale(reference_path)` — clears cache if `categories.json` is newer than cache

Singletons: `cache_repo` (CacheRepository) and `budget_repo` (JSONRepository).

### `classifier/engine.py` — Classification Pipeline (strict order)

Never skip steps — each step saves API cost:

1. **Normalize** — strip trailing IDs, numbers, special chars (`"UBER TRIP 123ABC"` → `"uber trip"`)
2. **Cache lookup** — if normalized description already classified, return immediately
3. **Keyword match** — search `categories.json` in JSON order (substring match)
4. **Regex match** — patterns like `UBER*`, `IFOOD*PEDIDO`, `99*`
5. **Fallback** — `"Outros"` (LLM/API fallback is commented out/deactivated)

Preserves pre-existing categories from CSV. Saves new cache entries in bulk at end.

### `classifier/local_rules.py`

- `load_categories()` — cached with `@st.cache_data`, reads `categories.json`
- `classify_local(description, categories)` — iterates ALL keywords first, then ALL regex. First match wins per pass. Returns `None` if no match.

### `parsers/nubank.py`

- Handles UTF-8/Latin-1 encoding detection
- Renames columns to `date`, `title`, `amount`, `categoria`
- Derives `tipo_transacao`: `gasto` (positive), `estorno` (negative), `ajuste` (zero)
- Filters out `saldo`/`pagamento` transactions and `ajuste` type
- Dedup by `(date, title, amount)`
- Extracts installment info: `parcela_atual`/`total_parcelas` from trailing `DD/DD` pattern
- Guards against false positives (clothing sizes, street numbers): validates `total > 1`, `total <= 24`, `atual <= total`

### `services/classification.py`

Saves manual reclassifications from the transaction table back to the cache. `save_manual_corrections(diff)` — iterates changed rows, normalizes title, stores `{categoria, source: "user"}` in cache.

## Configuration Files

### `categories.json`

```json
{
  "CategoryName": {
    "keywords": ["keyword1", "keyword2"],
    "regex": ["pattern1", "pattern2"]
  }
}
```

Keywords checked first (substring match, JSON order matters). Regex fallback. 17 categories defined.

### `config/budget.json`

```json
{
  "global": 2000.0,
  "categories": {
    "Transporte": 300.0
  }
}
```

### `config/categories.py`

Color palette dict `CATEGORY_COLORS` — 17 entries, hex values. Used by charts and UI.

## Cache Format

`cache/categories_cache.json` stores normalized → category mappings:

```json
{
  "uber trip": {
    "categoria": "Transporte",
    "source": "local"
  }
}
```

`source` can be `"local"` or `"user"` (from manual reclassification). Cache auto-invalidates when `categories.json` is modified.

## DataFrame Schema

Parsed DataFrames have columns:
- `date` — transaction date
- `title` — transaction description
- `amount` — value (positive = expense, negative = income/refund)
- `tipo_transacao` — `"gasto"` | `"estorno"` | `"ajuste"`
- `categoria` — classified category (nullable)
- `parcela_atual` — current installment number (default 1)
- `total_parcelas` — total installments (default 1)

## Core Business Logic

### Installments (`core/installments.py`)

Groups by `(title, amount, total_parcelas)` and keeps the most recent entry for each installment series.

### Recurrences (`core/recurrences.py`)

Detects subscriptions/recurring transactions:
- Appears in 3+ distinct months, OR
- Category is `"Assinaturas"`
Returns aggregated stats: months_count, avg_amount, last_date.

### Metrics (`core/metrics.py`)

`calculate_overview_metrics(df_current, df_previous)` — counts, totals, avg ticket, top category, "Outros" percentage, plus deltas against previous month.

### Filters (`utils/filters.py`)

`apply_filters(df, search_text, selected_cats, val_range, date_range, tipos, hide_outros, only_outros)` — chains filter conditions via boolean masks.

### Budget (`components/budget.py`)

Global + per-category spending tracking with progress bars. Editor in expandable section. Persists to `budget.json`.

## Key Edge Cases

- **Encoding**: try UTF-8 first, fallback to latin-1
- **Deduplication**: by `(date, title, amount)`
- **Refunds**: positive amounts → `tipo_transacao = "estorno"`, included but flagged
- **Installments**: strip `"02/05"` suffix from title before normalizing. Guard against false positives: `total_parcelas` must be 2-24, `parcela_atual` ≤ `total_parcelas`
- **International purchases**: not explicitly flagged yet
- **Cache migration**: old string-format entries auto-converted to `{categoria, source}` dict on load
- **Category preservation**: if CSV already has category values, classifier skips those rows
- **Payment/filter rows**: filters out rows containing `"saldo"` or `"pagamento"`
- **Column variance**: parser handles both `"title"` and `"description"` column names downstream
- **Empty cache creation**: repository creates parent directories on first save

## Normalization Examples (Nubank real cases)

```
"UBER TRIP 123ABC"       → "uber trip"
"IFOOD *PEDIDO"          → "ifood"
"MERCPAGO*LOJA123"       → "mercpago"
"COMPRA PARCELADA 01/12" → "compra parcelada"
```

## Dark Mode

Toggled via header button, stored in `st.session_state.dark_mode`. Default: `False` (light mode). Controlled by `settings.DEFAULT_DARK_MODE`. CSS variables in `theme.py` switch between light/dark palettes.

## UI Structure

4 tabs: Visão Geral, Transações, Recorrências, Parcelas Futuras. Sidebar has file selection + filters + export button. Header has title + dark mode toggle. Custom CSS hides Streamlit chrome, adds glassmorphism cards, fintech-modern appearance. Facebook-inspired color palette.