Refatore o gráfico de rosca (donut chart) de Gastos por Categoria no arquivo correspondente do dashboard para corrigir a ordenação e a paleta de cores, seguindo estas diretrizes:

1. Ordenação Horária (Maior para Menor):
   - Altere a lógica do gráfico para que as fatias sejam exibidas estritamente do maior valor para o menor valor.
   - Configure o início do gráfico no topo (12 horas / 90° de direção) e faça com que a ordenação decrescente siga estritamente no sentido horário.

2. Nova Paleta de Cores (Sem repetições):
   - Atualmente, existem tons de cinza repetidos para diferentes categorias. Substitua a paleta atual por uma sequência de cores expandida, harmônica e com alto contraste, adequada para temas Light e Dark.
   - Utilize uma paleta nativa estendida do Plotly (como `px.colors.qualitative.Prism`, `Safe` ou `Bold`) ou defina um mapeamento discreto de cores explícito para garantir que nenhuma categoria repita a mesma cor.

3. Legenda e Validação:
   - Garanta que a legenda ao lado do gráfico atualize a ordem dos itens para refletir exatamente a nova disposição (do maior para o menor).
   - Execute o dashboard localmente para validar as alterações, gere um artifact visual (screenshot) do novo gráfico e aplique o código definitivo assim que o layout estiver corrigido.