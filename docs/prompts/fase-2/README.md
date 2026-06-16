# Prompts — Fase 2: MVP 2 (Eventos Relevantes)

Prompts derivados do backlog [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md).

## Ordem de execução

| Ordem | Prompt | Estórias | Depende de |
|---|---|---|---|
| **01** | [01-coletar-dividendos-jcp.md](01-coletar-dividendos-jcp.md) | MVP2-01 | MVP1-08 (BRAPI 1 ativo/req) |
| **02** | [02-coletar-fatos-relevantes.md](02-coletar-fatos-relevantes.md) | MVP2-02 | 01 |
| **03** | [03-event-analyzer-e-alertas.md](03-event-analyzer-e-alertas.md) | MVP2-03, MVP2-04 | 01, F0-06 (Alembic) |
| **04** | [04-events-job-e-telegram.md](04-events-job-e-telegram.md) | MVP2-05, MVP2-06 | 03 |
| **05** | [05-operacao-eventos.md](05-operacao-eventos.md) | MVP2-07 | 04 |
| **06** | [06-testes-eventos.md](06-testes-eventos.md) | MVP2-08 | 01, 03, 04 |
| **07** | [07-api-endpoints-eventos.md](07-api-endpoints-eventos.md) | MVP2-09 | 04 |

> **02** pode ser entregue em versão mínima sem bloquear **03–06**. **06** deve vir antes de considerar a fase fechada. **07** é opcional para MVP operacional via cron.

## Como invocar

> Implemente a estória MVP2-01 conforme `docs/prompts/fase-2/01-coletar-dividendos-jcp.md`
