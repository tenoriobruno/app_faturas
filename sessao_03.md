# Objective
Desacoplar a lógica de cache e configurações globais de visualizações e views, melhorando a modularização e o desempenho de classificação.

# Affected files
- `data/repository.py`
- `app.py`
- `classifier/engine.py`
- `classifier/local_rules.py`
- `config/theme.py`
- `components/charts.py`
- `components/sidebar.py`
- `config/categories.py` (novo arquivo)

# What NOT to touch
- O fluxo de normalização de strings antes da classificação.
- O formato de gravação do cache em `cache/categories_cache.json`.

# Step by step instructions
1. Em `data/repository.py`, na classe `CacheRepository`, implemente o método `invalidate_if_stale(reference_path)` contendo a lógica de verificação de `st_mtime` que estava em `app.py` (linhas 27-34).
2. Em `app.py`, substitua o bloco inline de invalidação de cache pela chamada do método `cache_repo.invalidate_if_stale(settings.CATEGORIES_PATH)`.
3. Em `classifier/engine.py`, remova o singleton mutable global `_cache = None` e o método `get_cache()`. Alinhe o carregamento do cache utilizando as ferramentas do Streamlit (`st.cache_data` / `st.session_state`) ou instancie o repositório diretamente.
4. Em `classifier/local_rules.py`, decore `load_categories()` com `@st.cache_data` para evitar leituras de disco repetidas no mesmo rerun.
5. Em `classifier/local_rules.py` e `classifier/engine.py`, otimize `classify_batch()` para ler o arquivo `categories.json` apenas uma vez no início do lote e passar o dicionário carregado como parâmetro para `classify_local()`, em vez de reler o arquivo em cada transação individual.
6. Crie o arquivo `config/categories.py` e mova a constante `CATEGORY_COLORS` para ele, retirando-a de `config/theme.py`.
7. Atualize as referências e imports de `CATEGORY_COLORS` nos arquivos `app.py`, `components/charts.py` e `components/sidebar.py`.

# Success criteria
- O cache é limpo automaticamente quando o arquivo `categories.json` é modificado.
- A classificação de lotes de transações não realiza leituras redundantes de disco.
- As cores das categorias continuam sendo aplicadas corretamente nos gráficos e na barra lateral.

# Complexity
Medium
