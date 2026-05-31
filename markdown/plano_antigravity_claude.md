# Plano Antigravity Resumido

Rodar `plano_resumido.md` no Antigravity gastando mínimo de tokens gratuitos.

## 1. Modelos (barato→caro)

`GPT-OSS 120B < Gemini 3 Flash < Gemini 3.1 Pro low < Sonnet 4.6 thinking < Gemini 3.1 Pro high ≈ Opus 4.6 thinking`

| Modelo | Usar para | Evitar |
|--------|-----------|--------|
| Flash | UI boilerplate, CSS, patches linha-exata | Lógica cruzada |
| GPT-OSS 120B | Testes, fixtures, repetitivo | Código arquitetural |
| Gemini Pro low | Impl guiada, algoritmo simples | Decisão arquitetural |
| Sonnet thinking | API nova, regex edge cases | Edit trivial |
| Gemini Pro high | Refactor multi-arquivo | Tarefa mecânica |
| Opus thinking | **Emergência** (2 fallbacks falharam) | Primeira tentativa |

## 2. Alocação

| Seção | Primário | Fallback | Motivo |
|-------|----------|----------|--------|
| S1 Fix bugs | **Flash** | Sonnet | 6 patches descritos linha-a-linha |
| S2 AI classifier | **Sonnet thinking** | Gemini Pro high | Prompt + migração cache |
| S3 Sidebar+filtros | **Flash** | Sonnet | UI + 1 função pura |
| S4 Recorrências | **Gemini Pro low** | Sonnet | Groupby + critérios |
| S5 Orçamento | **Flash** | GPT-OSS | I/O JSON + UI |
| S6 KPIs delta | **Gemini Pro low** | Sonnet | Regex filename + Period |
| S7 Parcelas | **Sonnet thinking** | Gemini Pro high | Regex data vs parcela |
| S8 Refactor | **Gemini Pro high** | Opus | Toca tudo, risco cruzado |

Opus só emergência.

## 3. Setup

1. Workspace Antigravity → `/home/sagemaker-user/workspace/app_faturas`.
2. `git checkout -b antigravity-exec`.
3. Anexar `plano_resumido.md` em cada chat.
4. `PROGRESSO.md` com checklist S1-S8.

## 4. Loop por seção

1. Modelo da tabela 2.
2. **Chat NOVO** (contexto residual=vaza tokens).
3. Colar template §5 preenchido com N.
4. Anexar só arquivos da seção + `plano_resumido.md`.
5. Validar (comandos em `plano_resumido.md`).
6. `git commit -m "secao N: <titulo>"`.
7. Marcar em `PROGRESSO.md`.
8. **Fechar chat.**

## 5. Templates

### 5.1. Base
```
Implemente EXATAMENTE Seção {N} de plano_resumido.md.
REGRAS: leia primeiro; siga literal; não altere fora do escopo; ambíguo→pare e pergunte; não refatore fora do especificado; validar + reportar ao final.
Report: Seção {N} | Arquivos | Validação (passou/falhou+critério) | Dúvidas.
```

### 5.2. Mecânico (Flash/GPT-OSS)
```
Tarefa mecânica. Aplique diffs da Seção {N} de plano_resumido.md.
NÃO: feature extra, refactor, rename fora escopo, comentário.
SIM: bullets como edits isolados, preservar indent/imports.
```

### 5.3. Raciocínio (Sonnet/Gemini Pro low thinking)
```
Siga Seção {N} de plano_resumido.md.
Antes de codar:
1. Resuma em 3 bullets.
2. Liste arquivos tocados.
3. Liste riscos (edge cases, efeitos cruzados).
Depois implemente. Validar. Reportar.
```

### 5.4. Emergência (Opus/Gemini Pro high)
```
Duas tentativas falharam na Seção {N}.
Erros: <colar mensagens + diffs>
Tarefas: 1) causa raiz; 2) correção mínima; 3) aplicar; 4) validar.
Se ambiguidade do plano, propor update e parar antes de aplicar.
```

## 6. Economia de tokens

- **Nunca** anexar repo inteiro. Só arquivos da seção.
- **Nunca** reusar chat entre seções.
- **Sempre** chat novo por seção.
- **Máx 2 tentativas** por modelo antes de escalar.
- Dúvidas: acumular em `PROGRESSO.md`, perguntar em 1 sessão Opus/Gemini high, não 3x em modelos médios.

## 7. Execução seção-a-seção

**S1 Flash** — Anexar `plano_resumido.md`, `classifier/engine.py`, `parsers/nubank.py`, `app.py`, `categories.json`. Template 5.2. Validar: app sem exceção. Commit.

**S2 Sonnet thinking** — Anexar `plano_resumido.md`, `classifier/engine.py`, `utils/storage.py`, `utils/normalize.py`, `.env`. Template 5.3. Antes de codar, pedir confirmação da migração de cache. Validar: delete cache, rodar, ratio<15%, `source` presente. Commit.

**S3 Flash** — Anexar `plano_resumido.md`, `app.py`, `config/theme.py`; criar `utils/filters.py`. Template 5.2. Validar: 6 filtros reagem. Commit.

**S4 Gemini Pro low** — Anexar `plano_resumido.md`, `utils/normalize.py`, `app.py`; criar `analysis/recurrences.py`. Template 5.3. Testar `detect_recurrences` em script rápido antes da UI. Validar: Netflix "ativa". Commit.

**S5 Flash** — Anexar `plano_resumido.md`, `utils/storage.py`, `app.py`; criar `components/budget.py` + `budget.json`. Template 5.2. Validar: edição persiste. Commit.

**S6 Gemini Pro low** — Anexar `plano_resumido.md`, `app.py`, `components/charts.py`; criar `analysis/metrics.py`. Template 5.3. Confirmar regex `(\d{4})-(\d{2})-\d{2}` no filename. Validar: março/26 delta, abril/25 não. Commit.

**S7 Sonnet thinking** — Anexar `plano_resumido.md`, `utils/normalize.py`, `parsers/nubank.py`, `app.py`; criar `analysis/installments.py`. Template 5.3. **Risco:** regex pega datas. Confirmar guards (`total<=1`, `cur>total`, `total>24`). Validar: amostrar contra dados reais. Commit.

**S8 dividir em 4 sub-chats:**
- **S8a Flash** — `config/settings.py` + `utils/logger.py` (template 5.2).
- **S8b GPT-OSS 120B** — `tests/*` (template 5.2).
- **S8c Gemini Pro high** — `utils/loader.py` + `views/{overview,transactions,recurrences,installments}.py` (template 5.3).
- **S8d Gemini Pro high** — reescrita `app.py` <50 linhas (template 5.3).

Entre cada sub-chat: `pytest tests/ -v` + `streamlit run app.py`. Commit atômico. Fallback 8c/8d: Opus thinking.

## 8. Modo emergência (pool esgotou)

| Faltou | Substituir |
|--------|------------|
| Flash | GPT-OSS 120B |
| Sonnet | Gemini Pro low |
| Gemini Pro low | Sonnet |
| Gemini Pro high | Opus thinking |
| Opus | Gemini Pro high |
| Tudo | **Pausar. Esperar reset.** |

Nunca cair para tier inferior ao previsto — reset é mais barato que desfazer código ruim.

## 9. Checklist pré-seção

- [ ] Branch `antigravity-exec` limpo.
- [ ] `PROGRESSO.md` com anteriores marcadas.
- [ ] Modelo da tabela 2 selecionado.
- [ ] Chat novo.
- [ ] Só arquivos da seção + `plano_resumido.md` anexados.

## 10. Checklist pós-seção

- [ ] Validação passou.
- [ ] `streamlit run app.py` sem erro.
- [ ] Commit `secao N: <titulo>`.
- [ ] `PROGRESSO.md` atualizado.
- [ ] Chat fechado.

## 11. Regras duras

1. **Nunca** Flash/GPT-OSS na S8c/S8d.
2. **Nunca** reusar chat entre seções.
3. **Nunca** pular validação.
4. **Sempre** commit atômico por seção.
5. **Sempre** re-anexar `plano_resumido.md` em chat novo.

## 12. Ordem final

```
S1  Flash              S5  Flash
S2  Sonnet thinking    S6  Gemini Pro low
S3  Flash              S7  Sonnet thinking
S4  Gemini Pro low     S8a Flash
                       S8b GPT-OSS 120B
                       S8c Gemini Pro high
                       S8d Gemini Pro high
```

Opus 4.6 só emergência.
