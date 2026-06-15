# Backlog — Radar Financeiro IA

Estórias e tarefas organizadas por fase. Cada fase tem seu próprio diretório.

## Estrutura

```
docs/backlog/
├── README.md                 # Este arquivo
├── fase-0/
│   └── fase-0-fundacao.md
├── fase-1/
│   └── fase-1-mvp1.md
├── fase-2/                   # Criar quando iniciar MVP 2
├── fase-3/
├── fase-4/
└── fase-5/
```

## Fluxo

```mermaid
flowchart LR
    A[Estória no backlog] --> B[Prompt em docs/prompts/fase-x/]
    B --> C[Implementação]
    C --> D[Atualizar status da estória]
```

1. **Estória** define *o quê* e *por quê* (critérios de aceite)
2. **Prompt** define *como* implementar (arquivos, passos técnicos)
3. **1 prompt** cobre **1 a 3 estórias** relacionadas

## Template de estória

```markdown
### MVP1-XX — Título

**Como** [persona]
**Quero** [ação]
**Para** [benefício]

**Critérios de aceite:**
- [ ] ...

**Prompt:** `docs/prompts/fase-1/nome-do-prompt.md`
**Status:** pendente | em progresso | concluído
```

## Índice por fase

| Fase | Arquivo | MVP | Status |
|---|---|---|---|
| 0 | [fase-0/fase-0-fundacao.md](fase-0/fase-0-fundacao.md) | Fundação | Quase concluída (F0-06 pendente) |
| 1 | [fase-1/fase-1-mvp1.md](fase-1/fase-1-mvp1.md) | Radar Diário | Pendente |
| 2 | — | Eventos Relevantes | Não iniciado |
| 3 | — | Inteligência Financeira | Não iniciado |
| 4 | — | Personalização | Não iniciado |
| 5 | — | Assistente Conversacional | Não iniciado |

## Como invocar no chat

> Implemente a estória MVP1-01 conforme `docs/prompts/fase-1/01-coletar-variacoes.md`

Ou consulte o backlog da fase para ver a ordem recomendada.
