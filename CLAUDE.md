# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal finance MVP inspired by Guiabolso. Not SaaS — personal use only, no scalability requirements. Processes Nubank CSV exports and categorizes transactions using local rules with AI fallback.

**Budget constraint**: < $1 total development cost, < $0.05 per 100 classified transactions. AI must be called for fewer than 15% of transactions.

## Stack

- Python 3.11+, Streamlit, Pandas, Plotly, python-dotenv
- Anthropic SDK — model `claude-haiku-3-5-20251001` as AI fallback only

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Architecture

Data flow: `Upload CSV → Parse → Normalize → Classify → Cache/Save → Display/Edit → Export`

```
app.py                   # Streamlit entry point, wires all modules
parsers/nubank.py        # CSV parsing, encoding detection (utf-8/latin-1), dedup
classifier/
  engine.py              # Orchestrates classification pipeline
  local_rules.py         # Keywords + regex + fuzzy matching against categories.json
  ai_classifier.py       # Claude Haiku fallback, called only if local fails
utils/
  normalize.py           # Text normalization to reduce noise before classification
  storage.py             # Persistence: data/ and cache/
cache/categories_cache.json  # Persistent cache keyed by normalized description
categories.json          # Keyword/regex patterns per category
assets/styles.css        # Custom CSS to hide Streamlit defaults, fintech-like UI
```

## Classification Pipeline (strict order)

Never skip steps — each step saves API cost:

1. **Normalize** — strip trailing IDs, numbers, special chars (`"UBER TRIP 123ABC"` → `"uber trip"`)
2. **Cache lookup** — if normalized description already classified, return immediately
3. **Keyword match** — search `categories.json`
4. **Regex match** — patterns like `UBER*`, `IFOOD*PEDIDO`, `99*`
5. **Fuzzy token match** — simple token similarity
6. **AI (Haiku)** — only if all above fail

## Key Edge Cases

- **Encoding**: try UTF-8 first, fallback to latin-1
- **Deduplication**: by `date + description + amount`
- **Refunds**: positive amounts — exclude or flag, never classify normally
- **Installments**: strip `"01/12"` suffix before normalizing
- **International purchases**: flag separately

## Normalization Examples (Nubank real cases)

```
"UBER TRIP 123ABC"       → "uber trip"
"IFOOD *PEDIDO"          → "ifood"
"MERCPAGO*LOJA123"       → "mercpago"
"COMPRA PARCELADA 01/12" → "compra parcelada"
```

## UI

Custom CSS hides the default Streamlit chrome. Target layout: sidebar + card grid + Plotly charts + editable transaction table. Goal is a fintech-modern appearance, not a standard Streamlit app.
