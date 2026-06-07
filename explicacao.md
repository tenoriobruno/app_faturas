# Propostas de Melhoria de Interface — Explicação para o Usuário

Este documento explica, em linguagem simples, cada melhoria proposta para o dashboard de faturas: o que muda na prática e por que isso ajuda no uso do dia a dia.

---

## 1. Cards de resumo no topo da página

**O que muda:** Ao abrir o app, antes mesmo de clicar em qualquer aba, você já veria cards com o essencial: quanto gastou no total no período, como esse valor se compara ao mês anterior, e se há algum alerta de anomalia importante.

**Por que ajuda:** Hoje é preciso entrar na aba "Visão Geral" para ter essa noção. Com o resumo logo na entrada, você sabe "como está o mês" em um olhar, sem cliques.

---

## 2. Período/fatura selecionado sempre visível

**O que muda:** Um indicador fixo no topo mostraria sempre qual mês ou fatura você está vendo no momento.

**Por que ajuda:** Ao navegar entre abas (Visão Geral, Transações, Recorrências...), é fácil perder de vista qual período está sendo analisado. Esse indicador elimina a dúvida "espera, isso é a fatura de qual mês mesmo?".

---

## 3. Alertas de anomalias como banner colapsável

**O que muda:** Em vez de uma lista de avisos ocupando espaço fixo na tela, os alertas de gasto fora do padrão apareceriam como uma faixa no topo que você pode abrir ou fechar — mostrando "tudo certo" quando não há nada de anormal, ou "atenção: X categorias fora do padrão" quando há.

**Por que ajuda:** Você vê rapidamente se precisa se preocupar ou não, sem precisar ler avisos longos toda vez que abre o app — mas pode expandir para detalhes quando quiser.

---

## 4. Cards de métrica clicáveis

**O que muda:** Cards como "Maior Categoria" passariam a funcionar como atalho: ao clicar, a aba de Transações já abriria filtrada por aquela categoria.

**Por que ajuda:** Hoje, se você quer investigar "por que gastei tanto em Transporte", precisa ir manualmente até a aba Transações e configurar o filtro. Com o clique direto, a investigação começa em um passo.

---

## 5. Histórico mensal mais visível

**O que muda:** O gráfico de histórico de gastos por mês, que hoje fica no final da página de Visão Geral (depois de rolar bastante), subiria para perto do topo ou ganharia uma aba própria de "Tendências".

**Por que ajuda:** Esse gráfico mostra a evolução dos seus gastos ao longo do tempo — informação valiosa que hoje passa despercebida por estar "escondida" no fim da página.

---

## 6. Unificação dos filtros de busca

**O que muda:** Atualmente existem dois lugares para filtrar transações — a busca dentro da aba Transações e os filtros da barra lateral (sidebar). A proposta é ter um único ponto de busca/filtro, evitando duplicidade.

**Por que ajuda:** Menos confusão sobre "qual campo eu uso pra filtrar isso?" — você aprende um único fluxo e usa em qualquer lugar.

---

## 7. Contador de transações na tabela

**O que muda:** A tabela de transações passaria a mostrar quantos itens estão sendo exibidos no momento (ex.: "Mostrando 45 de 230 transações").

**Por que ajuda:** Em faturas grandes, fica difícil saber se você está vendo tudo ou apenas uma fatia filtrada. Esse contador dá noção exata do que está na tela.

---

## 8. Indicação visual de classificação manual vs. automática

**O que muda:** Cada transação categorizada mostraria um pequeno ícone ou selo indicando se a categoria foi definida automaticamente pelo sistema (🤖) ou corrigida manualmente por você (✍️).

**Por que ajuda:** Você consegue identificar rapidamente quais classificações já revisou e confirmou, e quais ainda são "palpites" do sistema que talvez mereçam uma conferida.

---

## 9. Filtros agrupados na barra lateral

**O que muda:** Os 7 controles de filtro hoje empilhados na lateral (busca, categorias, valor, data, tipo, 2 caixas de seleção) seriam organizados em grupos que se expandem — por exemplo "Filtros básicos" e "Avançado" — e mostrariam quantos filtros estão ativos no momento, com um botão para limpar tudo de uma vez.

**Por que ajuda:** Reduz a sensação de "tela cheia de opções". Quem só quer trocar o mês não precisa enxergar todos os filtros avançados; quem precisa deles os encontra organizados.

---

## 10. Tratamento de telas vazias / sem dados

**O que muda:** Se você subir um arquivo no formato errado, ou a pasta de dados estiver vazia, o app mostraria uma mensagem clara explicando o que aconteceu e o que fazer — em vez de uma tela confusa ou em branco.

**Por que ajuda:** Evita a sensação de "quebrou e não sei por quê" — você recebe uma orientação direta de como resolver.

---

## 11. Botão de exportação mais visível

**O que muda:** O botão para exportar os dados em CSV, que hoje pode estar "escondido" em algum canto da interface, subiria para um lugar de destaque na aba Transações.

**Por que ajuda:** Exportar dados é uma ação comum (para planilhas, backups, etc.) — ela deve ser fácil de encontrar, não exigir procura.

---

## 12. Revisão da paleta de cores e modo escuro

**O que muda:** Verificação se as cores atuais (inspiradas no Facebook) e o modo escuro estão com bom contraste e destaque visual em todos os estados — ao passar o mouse, ao focar em um campo, etc.

**Por que ajuda:** Garante que a interface continue agradável e fácil de usar tanto no modo claro quanto no escuro, sem elementos "sumindo" ou difíceis de enxergar.

---

## Próximos passos

Estas são propostas para discussão — nenhuma foi implementada ainda. A ideia é você escolher quais fazem mais sentido para o seu uso do dia a dia, e a partir disso criamos um plano detalhado de implementação para cada uma.
