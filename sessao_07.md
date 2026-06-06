# Objective
Implementar projeções de gastos em relação ao orçamento definido e adicionar um detector de anomalias (outliers) no histórico financeiro.

# Affected files
- `components/budget.py`
- `views/overview.py`
- `core/projections.py` (novo arquivo)
- `core/anomalies.py` (novo arquivo)

# What NOT to touch
- O fluxo de carregamento e consolidação de múltiplos CSVs.
- O formato de categorias de gastos.

# Step by step instructions
1. Crie o arquivo `core/projections.py` com funções para calcular a projeção linear de despesas com base no progresso temporal do mês atual (razão entre dia atual e quantidade total de dias no mês).
2. Modifique `components/budget.py` (ou o local onde as barras de progresso do orçamento são renderizadas) para exibir um indicador da projeção de fim de mês e adicionar alertas visuais de aviso se a projeção linear ultrapassar 90% do teto.
3. Crie o arquivo `core/anomalies.py` contendo uma lógica estatística básica (usando desvio padrão, ex: $gasto > média + 2\sigma$) para identificar categorias ou despesas atipicamente elevadas com base em `df_consolidated`.
4. Em `views/overview.py`, execute a verificação de anomalias para as transações do mês e renderize alertas visuais amigáveis (ex: `st.warning("⚠️ O gasto com Delivery este mês está 45% acima da média histórica")`).

# Success criteria
- O dashboard exibe projeções numéricas realistas do teto orçamentário.
- Alertas dinâmicos de anomalias aparecem apenas quando há picos estatísticos válidos nos dados.

# Complexity
Medium
