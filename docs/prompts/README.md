# Prompts — Radar Financeiro IA

Prompts de implementação derivados do backlog. Organizados por fase, numerados por ordem de execução.

## Estrutura

```
docs/prompts/
├── README.md
├── fase-0/
│   ├── README.md
│   └── 01-alembic-setup.md
└── fase-1/
    ├── README.md
    ├── 01-coletar-variacoes.md
    ├── 02-destaques-preco.md
    ├── 03-scheduler.md
    ├── 04-api-endpoints.md
    └── 05-testes.md
```

## Relação backlog → prompt

| Backlog | Prompts |
|---|---|
| [`backlog/fase-0/`](../backlog/fase-0/fase-0-fundacao.md) | [`fase-0/`](fase-0/README.md) |
| [`backlog/fase-1/`](../backlog/fase-1/fase-1-mvp1.md) | [`fase-1/`](fase-1/README.md) |

## Como usar

1. Consulte o backlog da fase para ver estórias e ordem
2. Execute os prompts na ordem numérica
3. Invoque no chat:

> Implemente a estória MVP1-01 conforme `docs/prompts/fase-1/01-coletar-variacoes.md`

4. Ao concluir, marque a estória como concluída no backlog
