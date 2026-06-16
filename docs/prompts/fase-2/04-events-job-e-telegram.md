# 04 — EventsJob e Telegram

**Estórias:** MVP2-05, MVP2-06
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md)

> **Como invocar:** "Implemente as estórias MVP2-05 e MVP2-06 conforme `docs/prompts/fase-2/04-events-job-e-telegram.md`"

## Contexto

Orquestrar a pipeline de eventos de ponta a ponta, espelhando o `DailyRadarJob` mas **separado** do radar de preço.

Leia: `jobs/daily_radar_job.py`, `notifications/telegram_sender.py`, `run_job.py`

## Escopo

### `jobs/events_job.py`

1. Classe `EventsJob(db: Session)` com método `run(user_email: str | None = None) -> str | None`
2. Fluxo:
   - Resolver usuário e tickers (`settings.asset_list` / carteira)
   - Separar ações e FIIs se necessário
   - `DividendsCollector.fetch_events(stock_tickers + fii_tickers)`
   - `EventsCollector.fetch_events(...)` (fatos relevantes)
   - `EventAnalyzer.build_highlights(...)`
   - Se vazio → retornar `None` (sem Telegram)
   - Persistir `Alert` + `MessageSent`
   - Enviar Telegram
3. Mensagem:

   ```
   Alerta — Eventos

   • PETR4 anunciou dividendos de R$ 1,25 por ação.
     Data-base: 15/08/2026 | Pagamento: 30/08/2026
   ```

4. HTML Telegram: `<b>Alerta — Eventos</b>`, bullets `•`, quebras de linha

### `run_events_job.py`

Entrypoint CLI na raiz (espelhar `run_job.py`):

```python
if __name__ == "__main__":
    init_db()  # ou alembic — manter padrão atual
    ...
```

## Fora de escopo

- Cron/scripts (prompt 05)
- Endpoints API (prompt 07)
- Mesclar com mensagem do radar diário

## Critérios de aceite

- [x] `python run_events_job.py` executa sem erro (com mocks ou API real)
- [x] Não envia Telegram quando não há eventos novos
- [x] Alertas persistidos com `alert_type` correto
- [x] Tom neutro; sem recomendação de compra/venda

## Notas para o implementador

- Reutilizar `_get_user`, `_resolve_tickers` — extrair helper compartilhado **somente** se reduzir duplicação real (evitar over-engineering)
- Marcar MVP2-05 e MVP2-06 concluídos no backlog
