# 04 — Endpoints de radar e histórico

**Estória:** MVP1-05
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md#mvp1-05--endpoints-de-radar-e-histórico)

> **Como invocar:** "Implemente a estória MVP1-05 conforme `docs/prompts/fase-1/04-api-endpoints.md`"

## Contexto

A API tem apenas `/health`. Precisamos de endpoints para disparar o radar e consultar histórico.

Leia: `app/main.py`, `database/models.py`, `database/connection.py`

## Escopo

**Novos arquivos em** `app/api/routes/`:

| Endpoint | Método | Descrição |
|---|---|---|
| `/radar/run` | POST | Dispara `DailyRadarJob` manualmente |
| `/alerts` | GET | Lista alertas (`limit`, `alert_type` opcionais) |
| `/messages` | GET | Lista mensagens enviadas (`limit` opcional) |

1. Usar `get_db()` como dependency
2. Respostas em JSON com campos essenciais (id, tipo, conteúdo, data)
3. Registrar routers em `app/main.py`

## Fora de escopo

- Autenticação (MVP 4)
- Paginação avançada
- Frontend

## Critérios de aceite

- [ ] `POST /radar/run` retorna mensagem gerada ou confirmação
- [ ] `GET /alerts?limit=10` retorna lista de alertas
- [ ] `GET /messages?limit=10` retorna mensagens enviadas
- [ ] Endpoints funcionam com `uvicorn app.main:app --reload`
