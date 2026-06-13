# Entrevista — Plano de Redesign Visual

> Resultado da entrevista de brainstorming sobre próximos passos do dashboard.
> Data: 2026-06-08

## Contexto

O dashboard já é funcional e maduro: 4 abas (Visão Geral, Transações, Recorrências, Parcelas Futuras), orçamento, detecção de anomalias, projeção de gastos, recorrências. A entrevista buscava descobrir a próxima prioridade.

## Achado central da entrevista

A dor real **não** é falta de features nem de insight analítico. É **visual**: o frontend está feio. Gatilho concreto apontado pelo usuário — as cores dos gráficos (donut e histórico) não harmonizam. Investigação mostrou que ambos os gráficos já usam a mesma `CATEGORY_COLORS`, então o problema não é divergência entre gráficos, e sim a **paleta em si**: 17 cores de saturação alta e matizes sem relação (laranja `#FF7F50`, vermelho `#FA383E`, azul Facebook `#0866FF`, pastéis aleatórios) que brigam entre si e destoam da vibe editorial do app.

**Decisão:** o próximo passo é um **redesign visual completo**, não features novas. Features de insight/diagnóstico ficam para depois (ver "Fora de escopo").

## Decisões travadas (validadas com mockups)

1. **Profundidade do redesign:** completo — tipografia, espaçamento, cards, header, cores. Não só os gráficos.
2. **Norte estético:** iOS (grid limpo, cards arredondados, profundidade suave, muito respiro, glanceável) + coesão tipo Instagram/Facebook.
3. **Tipografia:** trocar Merriweather serif → **sans pura** (estilo SF / DM Sans bold), em todo o app. iOS não usa serifa.
4. **Paleta de gráficos:** trocar para a **paleta sóbria dessaturada** (terrosa). Cores-base validadas:
   - slate `#3D5A80`, terracota `#E07A5F`, sage `#81B29A`, vermelho-tijolo `#C44E52`, lavanda `#9D8DF1`, teal suave `#6FB3B8`, mostarda `#E0B452`, cinza `#A0A4A8`. Estender para as 17 categorias mantendo a mesma saturação/luminosidade.
5. **Accent do app:** trocar azul Facebook `#0866FF` → **slate sóbrio `#3D5A80`** (alinhado à paleta), para o chrome não brigar com os gráficos calmos.
6. **Modos:** manter **light + dark**.
7. **Layout da Visão Geral (ordem validada):**
   - Header: mês grande (sans bold) + subtítulo cinza
   - Grid de 4 metric cards: total, ticket médio, transações, maior categoria — delta com cor semântica (vermelho subiu / verde caiu)
   - **Donut "Por categoria"** em largura total (donut + legenda lateral) — vem primeiro, detalha o mês que os metric cards resumem
   - **Histórico mensal** em largura total embaixo (barras empilhadas + média móvel) — fecha como tendência/aprofundamento
   - Demais seções (orçamento, anomalias, projeção) seguem o mesmo padrão de card
   - Racional da ordem (donut→histórico): fluxo resumo → detalhe do mês → tendência. Os dois gráficos ficam empilhados em largura total (não lado a lado) para que o histórico de 12 meses não fique espremido contra o donut.

## Escopo de arquivos

Centro da mudança:
- `config/theme.py` — CSS, tipografia (remover serif), variáveis de accent (slate), `get_plotly_layout`
- `config/categories.py` — substituir `CATEGORY_COLORS` pela paleta sóbria (17 entradas)
- `components/charts.py` — donut e barras consomem a nova paleta; ajustes de estilo (linhas, fontes, legendas)
- `views/overview.py` — reordenar painéis (donut full-width antes do histórico full-width)
- Ajuste fino em `components/` e `views/` para o padrão de card iOS

**Sem mexer** em lógica de dados, parsers, classificação, cache ou regras de negócio. Redesign é puramente de apresentação.

## Fora de escopo (deste plano)

Reconhecido como desejável no futuro, mas **não** entra agora:
- Diagnóstico narrativo / resumo em texto no topo ("esse mês foi caro por causa de X")
- Novos bancos / contas / receita / investimento
- Pergunta em linguagem natural
- Metas/objetivos de poupança

## Critérios de sucesso

- Donut e histórico visualmente harmônicos (mesma família de paleta), sem clash.
- App inteiro com aparência iOS coesa: sans, cards arredondados, respiro, accent slate.
- Light e dark mode ambos consistentes.
- Visão Geral na ordem validada (metric cards → donut full-width → histórico full-width).
- Nenhuma regressão de comportamento/dados.

## Próximo passo

Transformar este plano em plano de implementação detalhado (skill `writing-plans`).
