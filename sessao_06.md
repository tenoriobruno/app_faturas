# Objective
Implementar uma nova aba de Comparação Mês a Mês e adicionar suporte para ignorar recorrências (falsos positivos) de forma persistente.

# Affected files
- `app.py`
- `views/comparison.py` (novo arquivo)
- `views/recurrences.py`
- `core/recurrences.py`
- `data/repository.py`

# What NOT to touch
- O parser de faturas do Nubank.
- O cálculo de parcelas e o motor de classificação original.

# Step by step instructions
1. Crie o arquivo `views/comparison.py`. Desenvolva uma view que monte uma tabela dinâmica ou pivot table dos gastos categorizados por mês, comparando o mês selecionado com os meses anteriores (usando `df_consolidated`). Exiba variações em reais (R$) e percentuais (%).
2. Modifique `app.py` para incluir a aba "Comparação Mês a Mês" e renderizar a view criada.
3. No arquivo `data/repository.py`, crie uma classe ou método no repositório para gerenciar uma lista persistente de assinaturas/recorrências a serem ignoradas (ex: salvando um arquivo JSON `cache/ignored_recurrences.json`).
4. Em `core/recurrences.py`, integre a verificação de itens ignorados para filtrar a lista gerada de assinaturas antes de retornar os resultados.
5. Em `views/recurrences.py`, altere a exibição de recorrências para permitir ao usuário selecionar e clicar em um botão de ação "Ignorar esta assinatura". Ao clicar, grave a assinatura na lista de ignorados e recarregue a view.

# Success criteria
- A nova aba "Comparação Mês a Mês" exibe a evolução dos gastos categorizados de forma clara e legível.
- Ao clicar em "Ignorar" em uma recorrência na aba "Recorrências", ela é removida da listagem e salva no arquivo local de ignorados, não reaparecendo em execuções futuras.

# Complexity
Medium
