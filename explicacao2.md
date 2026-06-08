# Propostas de Melhoria — Rodada 2

Esta é a segunda rodada de propostas de interface e uso, depois de implementadas as 12 melhorias do `explicacao.md`. O foco aqui são as abas e telas que ainda não foram revisadas — **Recorrências**, **Parcelas Futuras**, **Comparação Mês a Mês** e **Orçamento** — além de deixar a experiência mais consistente entre todas as partes do app.

Como antes: cada item explica **o que muda** na prática e **por que ajuda** no dia a dia. Nada aqui foi implementado ainda — é material para você escolher.

---

## 1. Recorrências com visual de cartões (e não tabela "crua")

**O que muda:** Hoje, a lista de assinaturas e despesas fixas aparece como linhas de texto simples, sem moldura nem destaque — destoa do resto do app, que usa cartões com sombra e cantos arredondados. A proposta é apresentar cada assinatura num cartão padronizado, igual ao usado na Visão Geral.

**Por que ajuda:** Visual consistente em todas as telas dá sensação de app acabado e facilita a leitura — cada assinatura vira um "bloco" claro, em vez de uma linha perdida no meio de outras.

---

## 2. Confirmação ao ignorar uma recorrência

**O que muda:** Hoje, o botão "Ignorar" remove uma assinatura da lista imediatamente, com um clique só, sem perguntar nada. A proposta é pedir uma confirmação rápida ("Tem certeza?") antes de remover — ou oferecer um "desfazer" logo após.

**Por que ajuda:** Evita remover algo por engano. Como essa ação fica salva (a assinatura some das próximas vezes que você abrir o app), um clique acidental hoje é difícil de perceber e desfazer.

---

## 3. Aviso de reajuste em assinaturas

**O que muda:** Para cada assinatura recorrente, mostrar se o valor subiu em relação aos meses anteriores — por exemplo, "↑ 8% desde o mês passado".

**Por que ajuda:** Serviços como streaming e apps sobem de preço silenciosamente. Um indicador de aumento te avisa de reajustes que passariam despercebidos, ajudando a decidir se vale manter a assinatura.

---

## 4. Parcelas futuras ordenadas por peso

**O que muda:** Na aba de Parcelas Futuras, a lista de compras parceladas hoje aparece sem uma ordem clara. A proposta é ordená-la da maior para a menor dívida restante (o que ainda falta pagar).

**Por que ajuda:** Você vê primeiro o que mais pesa nas próximas faturas, facilitando priorizar pagamentos ou decidir onde cortar.

---

## 5. Comparação entre meses à sua escolha

**O que muda:** Hoje, a aba "Comparação Mês a Mês" compara sempre os dois meses mais recentes, de forma fixa. A proposta é deixar você escolher quais dois meses comparar (por exemplo, este mês contra o mesmo mês do ano passado).

**Por que ajuda:** Comparações sazonais ficam possíveis — gastos de dezembro vs. dezembro, ou férias vs. férias — em vez de só "mês passado vs. retrasado".

---

## 6. Cores da tabela de comparação adaptadas ao modo escuro

**O que muda:** A tabela de variações (quanto cada categoria subiu ou caiu) usa cores fixas de verde e vermelho que foram pensadas para fundo claro. No modo escuro, elas podem ficar difíceis de ler. A proposta é usar tons que se ajustam ao tema ativo.

**Por que ajuda:** Garante que os números de "subiu" (vermelho) e "caiu" (verde) continuem legíveis no modo escuro, sem cores "lavadas" ou de baixo contraste.

---

## 7. Editor de orçamento mais organizado

**O que muda:** Ao editar os limites de orçamento por categoria, hoje aparecem todos os campos de uma vez, empilhados — pode chegar a quase 20 campos numa lista longa. A proposta é separar as categorias já configuradas das ainda sem limite, e/ou permitir filtrar.

**Por que ajuda:** Você acha rápido a categoria que quer ajustar, sem rolar uma lista comprida toda vez — especialmente quando só quer mexer em uma ou duas.

---

## 8. Contador e exportação também nas outras abas

**O que muda:** O contador de itens ("X registros") e o botão de exportar CSV — que agora existem na aba Transações — não estão em Recorrências nem Parcelas Futuras. A proposta é levar esse mesmo padrão para essas abas.

**Por que ajuda:** Consistência: você aprende o padrão num lugar e o encontra em todos. Além disso, poder exportar a lista de assinaturas ou de parcelas é útil para planejamento fora do app.

---

## 9. Estado de "carregando" ao processar faturas

**O que muda:** Ao abrir o app ou subir um arquivo novo, o processamento das faturas (leitura, categorização) acontece sem um indicador visível de progresso. A proposta é mostrar um "carregando..." enquanto isso roda.

**Por que ajuda:** Com muitas faturas, há uma espera. Um indicador deixa claro que o app está trabalhando — e não travado — evitando a sensação de que algo deu errado.

---

## Próximos passos

Como na primeira rodada, são propostas para discussão. Escolha as que fazem sentido para o seu uso e implementamos uma a uma, com verificação a cada passo.
