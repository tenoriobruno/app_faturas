# Objective
Corrigir os bugs de inicialização do Streamlit, ordem de carregamento de tema (dark mode), importações tardias e inconsistências visuais em gráficos e CSS.

# Affected files
- `app.py`
- `components/header.py`
- `views/overview.py`
- `views/installments.py`
- `components/charts.py`
- `config/theme.py`

# What NOT to touch
- Lógica de cálculo de parcelas futuras em `core/installments.py`.
- Algoritmo de normalização e classificação de transações.
- Estrutura de dados básica dos DataFrames de faturas.

# Step by step instructions
1. Em `app.py`, verifique e inicialize `st.session_state.dark_mode` (usando o valor padrão definido em `config/settings.py`) antes de chamar `apply_theme()` na linha 22.
2. Em `components/header.py` (linhas 12-13), remova a lógica de inicialização de `st.session_state.dark_mode`.
3. Em `app.py` (linha 58), mova o import `from utils.logger import get_logger` de dentro da função `load_all_data` para a seção de imports globais no topo do arquivo.
4. Em `app.py` (linha 21), adicione o parâmetro `page_icon="💰"` à função `st.set_page_config` e ajuste o título para "App Faturas".
5. Em `views/overview.py` (linhas 63-65), remova os wraps manuais de `st.markdown('<div class="glass-card">', ...)` ao redor do gráfico de Plotly para evitar quebras de layout DOM.
6. Em `views/installments.py` (linha 73), altere o valor hardcoded `marker_color='#EF4444'` no gráfico de parcelas para usar a cor de destaque do tema ou uma cor com melhor contraste no dark mode.
7. Em `components/charts.py` (linhas 22 e 94), altere a propriedade `family='Inter'` das fontes dos gráficos para `family='DM Sans'` (ou remova para herdar a fonte do navegador).
8. Em `config/theme.py`, certifique-se de que a regra responsiva `@media (max-width: 768px) { [data-testid="stHorizontalBlock"] { flex-direction: column !important; } }` esteja presente também no CSS dark mode (`CSS_DARK`).

# Success criteria
- O dark mode funciona no carregamento inicial da página sem flash visual de light mode.
- O favicon e título da aba do navegador aparecem configurados corretamente.
- Nenhuma mensagem de erro de carregamento ou cache é mostrada devido a imports tardios.
- Os gráficos usam a tipografia correta e o gráfico de parcelas possui contraste adequado.
- As colunas colapsam em mobile sob o dark mode.

# Complexity
Low
