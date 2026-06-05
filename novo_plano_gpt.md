# Resumo Executivo

Este documento apresenta um plano de evolução incremental para o sistema **app_faturas**, preservando a estabilidade da aplicação em produção. Cada fase foi pensada para gerar valor imediato, ser implementada e validada de forma independente e minimizar riscos operacionais.

# Diagnóstico Atual

## Arquitetura & Estrutura de Diretórios  
- **Frontend** em Streamlit (Python) com componentes customizados
- **Backend** integrado ao próprio app.py
- Arquitetura monolítica mas com separação lógica de módulos
- Estrutura de pastas bem definida mas sem um design system centralizado
- Uso de módulos Python para diferentes responsabilidades (parsers, classifier, core, views, components)

## Frontend & UX/UI  
- Layout responsivo básico
- Falta de _design system_ unificado → inconsistências de cores, tipografia e espaçamentos
- Acessibilidade parcial: ausência de atributos `aria-` críticos

## Responsividade & Performance  
- Componentes críticos sem otimização
- Alguns componentes com renderizaões redundantes

## Qualidade de Código & Débito Técnico  
- Alguns componentes com código duplicado
- Funções espalhadas sem módulo compartilhado
- Tipagem dinâmica do Python permite uso extensivo de tipos genéricos

## Integrações & Testes  
- Integrações com serviços de faturamento via arquivos CSV
- Testes unitários cobrem parte do código

# Principais Problemas Encontrados

| Problema | Evidência (arquivo) | Impacto |
|----------|---------------------|----------|
| Inconsistência visual (paletas diferentes) | `components/` | Experiência do usuário confusa |
| Falta de componentização | `components/` | Código redundante e risco de divergência de comportamento |
| Ausência de atributos de acessibilidade | `components/` | Dificuldade de uso por pessoas com deficiência |
| Cobertura de testes limitada | `tests/` | Risco de regressões não detectadas |

# Oportunidades de Melhoria

1. **Introduzir Design System** (tokens de cores, tipografia, componentes base) – centraliza UI, reduz duplicação.  
2. **Componentizar UI** – criar componentes reutilizáveis.  
3. **Aprimorar acessibilidade** – adicionar atributos ARIA.  
4. **Aumentar cobertura de testes** – adicionar testes unitários para componentes críticos.  

# Roadmap Evolutivo

## Fase 1 – Melhorias de Baixo Risco (Entrega Imediata)

| Item | Objetivo | Benefício ao usuário | Impacto no negócio | Complexidade | Risco | Dependências |
|------|----------|----------------------|--------------------|--------------|-------|--------------|
| 1.1 Consolidar componentes | Unificar componentes em `components/` | UI consistente | Redução de dívida técnica | Baixa | Baixo | Nenhuma |
| 1.2 Acessibilidade básica | Adicionar `aria-` attributes | Navegação mais fluida | Conformidade com WCAG AA | Baixa | Baixo | Nenhuma |
| 1.3 Lint & CI lint fix | Garantir que o linter passe | Código limpo | Qualidade de código | Baixa | Baixo | Nenhuma |

### Plano Detalhado de Implementação da Fase 1

| Tarefa | Arquivos Impactados | Ordem de Execução | Estratégia de Implementação | Riscos | Validações Necessárias | Testes Manuais Recomendados |
|--------|----------------------|-------------------|----------------------------|--------|------------------------|-----------------------------|
| 1.1 Componentes | `components/` | 1️⃣ Identificar componentes duplicados. 2️⃣ Criar componentes reutilizáveis. 3️⃣ Atualizar imports. | Refatoração incremental | Quebra de importação | - Build bem-sucedido. - Verificar visualmente | Navegar nas páginas principais |
| 1.2 Acessibilidade | `components/` | 1️⃣ Inserir atributos `aria-`. 2️⃣ Gerenciar foco | Usuários com deficiência | Possível regressão | - Testar com teclado | Abrir cada componente, navegar com Tab |
| 1.3 Lint | Configuração `.streamlit/` | 1️⃓ Rodar linter. 2️⃣ Revisar avisos | Código padronizado | Pouco risco | - Build bem-sucedido. | Revisar visualmente | Revisar diff de lint |

### Checklist de Segurança para a Fase 1

- [ ] Build funcionando
- [ ] Lint sem erros
- [ ] Testes existentes passando
- [ ] Dashboard carregando normalmente
- [ ] Navegação funcionando
- [ ] Nenhuma regressão visual crítica
- [ ] Nenhuma regressão funcional crítica
- [ ] Rollback possível

## Fase 2 – Otimizações de Performance & Estado

| Item | Objetivo | Benefício | Complexidade | Risco |
|------|----------|-----------|--------------|-------|
| 2.1 Memorização de componentes | `st.cache` | Mais rapidez | Baixa | Baixo |

## Fase 3 – Design System & Component Library

| Item | Objetivo | Benefício | Complexidade | Risco |
|------|----------|-----------|--------------|-------|
| 3.1 Criar design tokens | Centralizar estilos | Consistência visual | Média | Baixo |
| 3.2 Refatorar componentes | Usar tokens | Reduzir duplicação | Média | Médio |

## Fase 4 – Testes de Integração & E2E

| Item | Objetivo | Benefício | Complexidade | Risco |
|------|----------|-----------|--------------|-------|
| 4.1 Cobertura de testes unitários > 80% | `components/*` | Detecta regressões | Média | Baixo |
| 4.2 Testes E2E | Fluxos críticos | Segurança | Média | Médio |

# Critérios para Aprovação da Fase 1

* build funcionando
* lint sem erros
* testes existentes passando
* dashboard carregando normalmente
* navegação funcionando
* nenhuma regressão visual crítica
* nenhuma regressão funcional crítica
* rollback possível