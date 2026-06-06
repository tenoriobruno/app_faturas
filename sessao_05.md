# Objective
Melhorar a usabilidade, acessibilidade e o feedback visual da interface do usuário do Streamlit.

# Affected files
- `views/recurrences.py`
- `views/installments.py`
- `app.py`
- `components/sidebar.py`
- `components/metrics.py`
- `views/transactions.py`
- `config/settings.py`

# What NOT to touch
- O fluxo de processamento de dados subjacente.
- A paleta de cores principal definida no tema.

# Step by step instructions
1. Em `views/recurrences.py` e `views/installments.py`, substitua o uso do componente `st.metric()` nativo pela função `metric_card()` para padronizar os blocos de métricas.
2. Em `app.py`, envolva o carregamento inicial de dados em um bloco `with st.spinner("Carregando faturas..."):`.
3. Em `components/sidebar.py`, adicione um botão "Limpar Filtros" que redefina todos os inputs da barra lateral para seus estados padrão no `st.session_state` e execute um `st.rerun()`.
4. Em `components/metrics.py` (linha 23), substitua o atributo `title` do HTML por `aria-label` para aumentar a acessibilidade da tooltip.
5. Em `views/transactions.py` (linha 21), defina um limite de altura (`height`) para o `st.data_editor` para adicionar rolagem vertical interna à tabela de transações.
6. Em `app.py` (linha 69), ajuste a função `format_func` do selectbox de arquivos para mostrar informações contextuais (por exemplo, o período de datas e o total de transações) em vez de apenas o nome do arquivo bruto.
7. Em `config/settings.py` (linha 14), altere `DEFAULT_DARK_MODE` para carregar a partir de variável de ambiente (ex: `os.getenv("DEFAULT_DARK_MODE", "False").lower() == "true"`).

# Success criteria
- O visual do painel é uniforme, sem mistura de `st.metric` padrão e customizado.
- Há feedback de loading ao carregar ou trocar arquivos.
- A tabela de transações não estica a página do navegador infinitamente.
- O botão de limpar filtros limpa todos os inputs na sidebar com sucesso.

# Complexity
Low
