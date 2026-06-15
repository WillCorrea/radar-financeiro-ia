# Fase 0 — Fundação

**Objetivo:** base documentada e convenções definidas antes de evoluir os MVPs.

**Referência:** [`docs/plano-implementacao.md`](../../plano-implementacao.md#fase-0--fundação)

---

## Resumo

| ID | Estória | Status |
|---|---|---|
| F0-01 | Documentar visão e roadmap | concluído |
| F0-02 | Documentar arquitetura do pipeline | concluído |
| F0-03 | Criar rules do Cursor | concluído |
| F0-04 | Estruturar backlog por fases | concluído |
| F0-05 | Adicionar `__init__.py` nos pacotes | concluído |
| F0-06 | Configurar Alembic para migrations | pendente |

---

## F0-01 — Documentar visão e roadmap

**Como** mantenedor do projeto
**Quero** ter a visão do produto e o roadmap documentados
**Para** alinhar decisões técnicas com o objetivo do negócio

**Critérios de aceite:**
- [x] `docs/product/visao-geral.md` criado
- [x] `docs/product/roadmap.md` criado com MVPs 1–5

**Prompt:** —
**Status:** concluído

---

## F0-02 — Documentar arquitetura do pipeline

**Como** desenvolvedor
**Quero** entender a arquitetura em camadas do sistema
**Para** saber onde implementar cada tipo de funcionalidade

**Critérios de aceite:**
- [x] `docs/architecture/pipeline.md` criado
- [x] Responsabilidades de cada camada definidas

**Prompt:** —
**Status:** concluído

---

## F0-03 — Criar rules do Cursor

**Como** desenvolvedor usando IA
**Quero** convenções persistentes no agente
**Para** garantir tom neutro e respeito à arquitetura

**Critérios de aceite:**
- [x] `.cursor/rules/financial-disclaimer.mdc` criado
- [x] `.cursor/rules/architecture-pipeline.mdc` criado

**Prompt:** —
**Status:** concluído

---

## F0-04 — Estruturar backlog por fases

**Como** mantenedor do projeto
**Quero** estórias segregadas por fase em diretórios próprios
**Para** organizar o trabalho e derivar prompts focados

**Critérios de aceite:**
- [x] `docs/backlog/fase-x/` com um arquivo por fase
- [x] Estórias da Fase 1 detalhadas com critérios de aceite
- [x] Prompts da Fase 1 quebrados por grupo de estórias

**Prompt:** —
**Status:** concluído

---

## F0-05 — Adicionar `__init__.py` nos pacotes

**Como** desenvolvedor
**Quero** pacotes Python com imports estáveis
**Para** evitar problemas de importação entre módulos

**Critérios de aceite:**
- [x] `__init__.py` em `app/`, `app/api/`, `app/api/routes/`, `collectors/`, `analyzers/`, `agents/`, `notifications/`, `jobs/`, `database/`
- [x] Imports existentes continuam funcionando

**Prompt:** —
**Status:** concluído

---

## F0-06 — Configurar Alembic para migrations

**Como** desenvolvedor
**Quero** versionar mudanças no schema do banco
**Para** evoluir o modelo de dados com segurança

**Critérios de aceite:**
- [ ] Alembic configurado e integrado com `database/models.py`
- [ ] Primeira migration gerada a partir dos models atuais
- [ ] Instruções de uso no README ou docs

**Prompt:** [`docs/prompts/fase-0/01-alembic-setup.md`](../../prompts/fase-0/01-alembic-setup.md)
**Status:** pendente
