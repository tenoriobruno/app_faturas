# Objective
Separar responsabilidades nas camadas de visualização (views/components), extraindo lógicas de negócio e persistência para arquivos do core ou de serviços.

# Affected files
- `views/overview.py`
- `views/transactions.py`
- `views/installments.py`
- `components/budget.py`
- `core/metrics.py` (novo arquivo)
- `services/classification.py` (novo arquivo)
- `core/installments.py`

# What NOT to touch
- O estilo CSS ou estrutura HTML dos cards e barras de progresso do budget.
- O formato do JSON de cache ou de orçamento.

# Step by step instructions
1. Crie o arquivo `core/metrics.py` e extraia a lógica de cálculo de métricas da view `views/overview.py` (linhas 29-44) para funções puras e testáveis (ex: `calculate_overview_metrics(df_current, df_previous)`).
2. Atualize `views/overview.py` para chamar o novo módulo do core e obter os valores calculados antes de renderizar os cartões.
3. Crie o arquivo `services/classification.py` e encapsule a lógica de persistência de correções manuais de categoria (linhas 36-46 de `views/transactions.py`), incluindo a normalização de texto e gravação no repositório.
4. Modifique `views/transactions.py` para invocar o novo serviço de classificação em vez de realizar a escrita e normalização de forma direta.
5. No arquivo `core/installments.py`, adicione a lógica de projeção de saldo devedor mensal futuro que estava implementada inline na view `views/installments.py` (linhas 29-43).
6. Atualize a view `views/installments.py` para consumir apenas o resultado processado pelo core e renderizar o gráfico.
7. Em `components/budget.py`, separe a lógica de renderização (`render_budget`) da lógica de edição/atualização do orçamento (linhas 49-69), criando uma função dedicada ou movendo o formulário de edição para fora do componente visual principal.

# Success criteria
- Todas as views ficam livres de lógica de persistência direta no disco.
- O cálculo de métricas, deltas e projeção de parcelas gera resultados idênticos aos anteriores.
- A edição manual de categorias continua funcionando e atualizando o cache.

# Complexity
Medium
