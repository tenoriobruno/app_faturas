# Proposta de Melhoria — Feature de Orçamento

## Diagnóstico: por que está "solta"

A feature de orçamento hoje vive no **fim da aba Visão Geral** (`views/overview.py:92`),
depois do histórico mensal e das anomalias. Consequências:

1. **Sem destaque próprio.** Quem abre o app não vê o orçamento — precisa rolar até o
   final. Não existe aba, badge no header nem resumo na sidebar.
2. **Desconectada do resto.** Anomalias (`core/anomalies.py`) e orçamento são dois
   sistemas de alerta paralelos que não conversam. Um diz "gastou fora do padrão", o
   outro "estourou o limite" — mas nunca juntos.
3. **Projeção frágil.** `calculate_linear_projection` usa `datetime.now()`
   (`core/projections.py:13`) contra o mês do arquivo selecionado. Se o usuário abre um
   CSV de um **mês passado**, a projeção divide o gasto fechado por `progress` < 1 e
   infla números sem sentido (ex.: mês fechado projeta 200% do orçamento).
4. **Sem ação acionável.** Mostra "gastou R$ X de R$ Y", mas não responde a pergunta que
   importa: **"quanto posso gastar por dia até o fim do mês sem estourar?"**
5. **Lógica de limiar duplicada.** As cores/thresholds (0.8, 0.9, 1.0) estão hardcoded e
   repetidas em `budget.py` e `projections.py`. Mudar a regra exige editar dois arquivos.
6. **Sem memória.** Não há histórico de aderência ao orçamento ("cumpri o limite em
   abril?"). Cada mês começa do zero, sem aprendizado.

---

## Proposta

### A. Tornar o orçamento visível (baixo esforço, alto impacto)

- **Resumo na sidebar**: uma linha compacta "Orçamento: R$ 3.2k / R$ 5k (64%)" com a
  barra de progresso global, sempre visível independente da aba.
- **Badge no header**: ícone 🎯 que fica amarelo/vermelho quando projeção ≥ 90% /
  estourou. Sinal de status sem precisar abrir nada.

### B. "Quanto posso gastar por dia" (o número que falta)

No card global, adicionar a métrica mais útil de controle:

```
Disponível: R$ 1.800 restantes
Ritmo seguro: R$ 138/dia pelos próximos 13 dias
```

Cálculo: `(global_budget - total_spent) / dias_restantes`. Se negativo → "Orçamento
estourado, R$ X acima".

### C. Corrigir a projeção para mês não-corrente

`projections.py` deve detectar o mês do `df` (via `df['date'].max()`):

- Mês **corrente** → projeção linear como hoje.
- Mês **passado/fechado** → sem projeção, mostrar resultado **real** ("Fechou em 92% do
  orçamento ✅" ou "Estourou em 14% ❌").

Isso também habilita a seção D.

### D. Unificar anomalias + orçamento

Em vez de dois blocos de alerta separados, um único painel **"Saúde do Mês"**:

- Categorias que **estouraram o limite** (do orçamento).
- Categorias **fora do padrão histórico** (das anomalias).
- Marcar quando as duas coisas batem na mesma categoria (alerta forte).

### E. Histórico de aderência (memória)

Pequeno gráfico/lista: "% do orçamento global usado nos últimos N meses". Usa
`df_consolidated` que já existe. Responde "estou melhorando ou piorando?".

### F. Centralizar limiares

Mover os thresholds (`WARN=0.8`, `PROJECTION_WARN=0.9`, `OVER=1.0`) e as cores
correspondentes para `config/settings.py` (ou `config/categories.py`). Elimina a
duplicação entre `budget.py` e `projections.py`.

---

## Priorização sugerida

| # | Item | Esforço | Impacto | Ordem |
|---|------|---------|---------|-------|
| C | Corrigir projeção mês fechado | Baixo | Alto (corrige bug) | **1º** |
| B | Ritmo seguro / disponível por dia | Baixo | Alto | **2º** |
| A | Resumo sidebar + badge header | Médio | Alto (visibilidade) | **3º** |
| F | Centralizar limiares | Baixo | Médio (manutenção) | 4º |
| D | Unificar anomalias + orçamento | Médio | Médio | 5º |
| E | Histórico de aderência | Médio | Médio | 6º |

**Quick win recomendado:** C + B + F juntos — resolvem o bug da projeção, entregam o
número acionável que falta e limpam a duplicação, tudo em arquivos que já existem
(`projections.py`, `budget.py`, `settings.py`), sem nova aba nem nova dependência.

---

## Fora de escopo (consciente)

- Rollover de saldo entre meses (sobra de um mês vira margem do outro) — complexidade
  alta, valor incerto para uso pessoal.
- Orçamento por método de pagamento ou por banco.
- Metas/objetivos de poupança (outra feature, não orçamento de gasto).
