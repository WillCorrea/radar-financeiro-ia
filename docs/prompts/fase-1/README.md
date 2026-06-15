# Prompts — Fase 1: MVP 1

Prompts derivados do backlog [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md).

## Ordem de execução

| Ordem | Prompt | Estórias | Depende de |
|---|---|---|---|
| **01** | [01-coletar-variacoes.md](01-coletar-variacoes.md) | MVP1-01 | — |
| **02** | [02-destaques-preco.md](02-destaques-preco.md) | MVP1-02, MVP1-03 | 01 |
| **03** | [03-scheduler.md](03-scheduler.md) | MVP1-04 | 02 |
| **04** | [04-api-endpoints.md](04-api-endpoints.md) | MVP1-05 | 02 |
| **05** | [05-testes.md](05-testes.md) | MVP1-06 | 01, 02 |
| **06** | [06-operacao-local-wsl.md](06-operacao-local-wsl.md) | MVP1-07 | 04 |
| **07** | [07-brapi-um-ativo-por-requisicao.md](07-brapi-um-ativo-por-requisicao.md) | MVP1-08 | 01 |

> **03** e **04** podem ser feitos em paralelo após o **02**. O **05** deve vir antes do **06**. O **07** é pós-MVP operacional — corrige coleta multi-ativo no plano BRAPI gratuito.

## Como invocar

> Implemente a estória MVP1-01 conforme `docs/prompts/fase-1/01-coletar-variacoes.md`
