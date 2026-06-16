# 06 — Testes do fluxo de eventos

**Estória:** MVP2-08
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md#mvp2-08--testes-do-fluxo-de-eventos)

> **Como invocar:** "Implemente a estória MVP2-08 conforme `docs/prompts/fase-2/06-testes-eventos.md`"

## Contexto

MVP 1 estabeleceu padrão de testes com mock httpx. Repetir para eventos.

Leia: `tests/test_stocks_collector.py`, `tests/test_daily_radar_job.py`, `tests/test_price_analyzer.py`

## Escopo

| Arquivo | Cobertura |
|---|---|
| `tests/test_dividends_collector.py` | Parse brapi, 1 req/ticker, falha parcial |
| `tests/test_events_collector.py` | Parse CVM, lookback, falha parcial |
| `tests/test_event_analyzer.py` | Dedup, lookback, formatação |
| `tests/test_events_job.py` | Fluxo com mocks; sem Telegram se vazio; dedup na 2ª execução |

## Fora de escopo

- Testes de integração real com BRAPI/CVM
- Testes E2E Telegram

## Critérios de aceite

- [x] `pytest` passa sem erros
- [x] Dedup testado (segunda execução não duplica alerta)
- [x] Mock de `TelegramSender.send_message` verifica conteúdo quando há eventos

## Notas para o implementador

- Usar `pytest` + `unittest.mock`
- Marcar MVP2-08 concluída no backlog
