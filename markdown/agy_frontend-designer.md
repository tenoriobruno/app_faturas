Analise a UI e o código deste dashboard de Finanças Pessoais executando a aplicação localmente. Varra os arquivos do projeto para avaliar a implementação, a alternância entre os temas Light e Dark, e proponha melhorias de UX/UI e refatoração estrutural com foco nas seguintes abas e componentes mapeados:

1. Elementos Globais e Sidebar (Persistentes):
   - Sidebar de Filtros: Avalie o alinhamento da área de drag-and-drop de arquivos CSV, o contraste interno dos inputs e a usabilidade dos sliders de faixa de valor (especialmente o comportamento da linha azul e inputs de texto no tema Dark).
   - Menu Superior de Navegação: Verifique o alinhamento das abas de navegação e o posicionamento do botão/ícone de alternância de tema (Sol/Lua).

2. Visão Geral (Métricas e Distribuição):
   - Gráfico de Rosca (Donut Chart): Analise o contraste das fatias coloridas sobre o fundo branco e o fundo cinza-escuro. Avalie a legibilidade do texto e a disposição da legenda multicolunas ao lado do gráfico.
   - Cards Laterais de Resumo: Verifique o espaçamento interno (padding), a hierarquia tipográfica dos valores principais e a legibilidade dos micro-dados de comparação percentual ou nominal (ex: os valores em verde ou vermelho abaixo do total).

3. Acompanhamento de Orçamento e Histórico:
   - Barras de Progresso de Categoria: Avalie o layout e o contraste das barras de progresso horizontais (Global, Delivery, Supermercado, etc.). Verifique a legibilidade dos textos de teto de gastos empilhados e o componente de dropdown 'Editar Orçamento'.
   - Gráfico de Histórico Mensal (Barras Empilhadas): Verifique o contraste das micro-fatias nas barras mensais, a legibilidade do eixo Y (valores em R$) e a área da legenda inferior com múltiplos itens.

4. Visões de Dados e Tabelas (Transações, Recorrências e Parcelas Futuras):
   - Visualização de Dados Brutos (Tabelas): Analise o layout das tabelas na aba Transações e Recorrências. Avalie o contraste das linhas alternadas (zebra striping), o padding das células, o alinhamento dos cabeçalhos e a legibilidade das datas e valores monetários.
   - Dívidas Ativas e Faturas Futuras: Avalie o componente de progresso das parcelas (ex: "Airbnb - 2/6 pagas") e garanta que as barras horizontais mantêm a consistência visual do restante do app.

5. Engenharia de Código e Execução Autônoma:
   - Verifique se a folha de estilos ou o gerenciamento de estados (ex: variáveis CSS ou propriedades do framework de UI) para os temas Light/Dark está centralizado e escalável.
   - Identifique redundâncias de código ou lógica duplicada na renderização das tabelas e gráficos.
   - Gere artifacts visuais (screenshots) das principais abas para validação. Liste as propostas de melhoria de UX/UI e, caso identifique correções seguras de alinhamento, espaçamento ou cores de fontes, aplique as modificações diretamente nos arquivos de front-end.