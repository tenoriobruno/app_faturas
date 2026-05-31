# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## Project Overview

Personal finance MVP inspired by Guiabolso. Not SaaS — personal use only, no scalability requirements. Processes Nubank CSV exports and categorizes transactions using local rules with AI fallback.

**Budget constraint**: < $1 total development cost, < $0.05 per 100 classified transactions. AI must be called for fewer than 15% of transactions.

## Stack

- Python 3.11+, Streamlit, Pandas, Plotly, python-dotenv

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATA_PATH` | `.` | Directory where Nubank CSVs are stored |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Architecture

Data flow: `Upload CSV → Parse → Normalize → Classify → Cache/Save → Display/Edit → Export`

```
app.py                   # Streamlit entry point, wires all modules
config/
  settings.py            # Centralized settings and env loader
  theme.py               # Custom CSS to hide Streamlit defaults, layout, colors
parsers/nubank.py        # CSV parsing, encoding detection (utf-8/latin-1), dedup
classifier/
  engine.py              # Orchestrates classification pipeline
  local_rules.py         # Keywords + regex matching against categories.json
core/                    # Business logic (recurrences, installments)
data/
  repository.py          # Persistence: JSON caching and budget
views/                   # Streamlit tabs
components/              # Reusable UI components (charts, sidebar, budget)
utils/
  normalize.py           # Text normalization to reduce noise before classification
  export.py              # CSV export functionality
cache/categories_cache.json  # Persistent cache keyed by normalized description
categories.json          # Keyword/regex patterns per category
```

## Configuration Files

### `categories.json`

Defines classification rules per category:

```json
{
  "CategoryName": {
    "keywords": ["keyword1", "keyword2"],
    "regex": ["pattern1", "pattern2"]
  }
}
```

Keywords are checked first (substring match, order of JSON matters). Regex is fallback.

### `.streamlit/config.toml`

Theme configuration with Facebook-inspired colors. Located at `.streamlit/config.toml`.

## Classification Pipeline (strict order)

Never skip steps — each step saves API cost:

1. **Normalize** — strip trailing IDs, numbers, special chars (`"UBER TRIP 123ABC"` → `"uber trip"`)
2. **Cache lookup** — if normalized description already classified, return immediately
3. **Keyword match** — search `categories.json` in JSON order
4. **Regex match** — patterns like `UBER*`, `IFOOD*PEDIDO`, `99*`

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

`source` can be `"local"` or `"ai"`.

## DataFrame Schema

Parsed DataFrames have columns:
- `date` — transaction date
- `title` — transaction description
- `amount` — value (negative = income/refund, positive = expense)
- `tipo_transacao` — `"gasto"` | `"estorno"` | `"ajuste"`
- `categoria` — classified category (nullable)
- `parcela_atual` — current installment number (default 1)
- `total_parcelas` — total installments (default 1)

## Core Business Logic

### Installments (`core/installments.py`)

Identifies installment purchases from consolidated data. Groups by `(title, amount, total_parcelas)` and keeps the most recent entry for each installment series.

### Recurrences (`core/recurrences.py`)

Detects subscriptions/recurring transactions:
- Appears in 3+ distinct months, OR
- Category is `"Assinaturas"`

Returns aggregated stats: months_count, avg_amount, last_date.

## Key Edge Cases

- **Encoding**: try UTF-8 first, fallback to latin-1
- **Deduplication**: by `date + description + amount`
- **Refunds**: positive amounts — `tipo_transacao = "estorno"`, included but flagged
- **Installments**: strip `"01/12"` suffix from title before normalizing, guard against false positives (size numbers, street numbers)
- **International purchases**: not explicitly flagged yet

## Normalization Examples (Nubank real cases)

```
"UBER TRIP 123ABC"       → "uber trip"
"IFOOD *PEDIDO"          → "ifood"
"MERCPAGO*LOJA123"       → "mercpago"
"COMPRA PARCELADA 01/12" → "compra parcelada"
```

## UI

Custom CSS hides the default Streamlit chrome. Target layout: sidebar + card grid + Plotly charts + editable transaction table. Goal is a fintech-modern appearance, not a standard Streamlit app.

Colors defined in `config/theme.py` — Facebook-inspired palette.