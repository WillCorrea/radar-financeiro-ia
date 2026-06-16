# 01 — Coletar dividendos e JCP

**Estória:** MVP2-01
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md#mvp2-01--coletar-dividendos-e-jcp)

> **Como invocar:** "Implemente a estória MVP2-01 conforme `docs/prompts/fase-2/01-coletar-dividendos-jcp.md`"

## Contexto

O MVP 1 cobre preço; o MVP 2 começa por **proventos em dinheiro**. A brapi.dev expõe `dividendsData.cashDividends` via `GET /api/quote/{ticker}?dividends=true`.

Leia: `collectors/stocks_collector.py` (padrão BRAPI 1 ativo/req), `app/config.py`, [documentação brapi — dividendos](https://brapi.dev/docs/acoes.mdx)

## Escopo

**Arquivo principal:** `collectors/dividends_collector.py`

1. Criar dataclass `DividendEvent` (ou módulo `collectors/types.py` se preferir):
   - `ticker`, `event_type` (`dividend` | `jcp`), `amount_per_share`, `ex_date`, `payment_date`, `label` (texto brapi)
2. `DividendsCollector.fetch_events(tickers: list[str]) -> list[DividendEvent]`
3. **1 ticker por requisição** + `apply_brapi_request_delay()` (reutilizar de `stocks_collector`)
4. Params: `dividends=true`, sem `range`/`interval` desnecessários
5. Mapear campos brapi (`rate`, `type`, `lastDatePrior`, `paymentDate`, etc.) — validar nomes reais na resposta
6. Falha parcial por ticker; 401 continua propagando erro de token
7. FIIs: tentar mesmo endpoint; se dados indisponíveis, retornar lista vazia para aquele ticker (documentar no código)

## Fora de escopo

- `EventAnalyzer`, job, Telegram
- Fatos relevantes (prompt 02)
- Persistência no banco

## Critérios de aceite

- [x] `fetch_events(["PETR4"])` retorna eventos parseados quando a API responder
- [x] Requisições individuais por ticker (mock em teste)
- [x] Tipos DIVIDENDO e JCP distinguidos
- [x] `pytest` para o collector (mock httpx)

## Referência API

```
GET https://brapi.dev/api/quote/PETR4?dividends=true
Authorization: Bearer {BRAPI_TOKEN}
```

Resposta esperada (simplificado):

```json
{
  "results": [{
    "symbol": "PETR4",
    "dividendsData": {
      "cashDividends": [
        {
          "type": "DIVIDENDO",
          "rate": 1.25,
          "lastDatePrior": "2026-08-15",
          "paymentDate": "2026-08-30"
        }
      ]
    }
  }]
}
```

## Notas para o implementador

- Respeitar `.cursor/rules/architecture-pipeline.mdc` — collector só coleta, não formata alerta
- Tom neutro; sem recomendar compra/venda
- Ao concluir, marcar MVP2-01 no backlog
