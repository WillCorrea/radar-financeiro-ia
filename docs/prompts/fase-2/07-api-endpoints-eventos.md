# 07 — Endpoints API de eventos

**Estória:** MVP2-09
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md#mvp2-09--endpoints-api-de-eventos)

> **Como invocar:** "Implemente a estória MVP2-09 conforme `docs/prompts/fase-2/07-api-endpoints-eventos.md`"

## Contexto

MVP 1 entregou `POST /radar/run` e `GET /alerts`. Estender para eventos.

Leia: `app/api/routes/radar.py`, `app/api/routes/alerts.py`, `app/main.py`

## Escopo

1. **`app/api/routes/events.py`**
   - `POST /events/run` → dispara `EventsJob`, retorna mensagem ou `{ "message": null, "events": 0 }`
2. Confirmar que `GET /alerts?alert_type=dividend` (e `jcp`, `corporate_event`) funciona — ajustar se necessário
3. Registrar router em `app/main.py`
4. Usar `get_db()` e tipagem Py 3.8 (`Dict`, `Optional`)

## Fora de escopo

- Autenticação / multi-tenant
- WebSocket

## Critérios de aceite

- [ ] `POST /events/run` retorna 200
- [ ] Filtro por `alert_type` documentado no docstring ou README
- [ ] App sobe sem erro (`uvicorn app.main:app`)

## Notas para o implementador

- Marcar MVP2-09 concluída no backlog
