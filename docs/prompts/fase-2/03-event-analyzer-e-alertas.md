# 03 — EventAnalyzer e alertas (Alembic)

**Estórias:** MVP2-03, MVP2-04
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md)

> **Como invocar:** "Implemente as estórias MVP2-03 e MVP2-04 conforme `docs/prompts/fase-2/03-event-analyzer-e-alertas.md`"

## Contexto

Collectors retornam eventos brutos. O analyzer filtra, deduplica e produz **destaques** prontos para alerta. Novos `alert_type` precisam de migration Alembic (sem mudar schema de colunas — só convenção de valores + doc).

Leia: `analyzers/price_analyzer.py`, `analyzers/event_analyzer.py`, `database/models.py`, `docs/operations/database-migrations.md`

## Escopo

### `analyzers/event_analyzer.py`

1. Substituir placeholder por implementação real
2. Entrada: `list[DividendEvent]`, `list[CorporateEvent]`, `Session` (para dedup)
3. Saída: `list[EventHighlight]` (dataclass com `ticker`, `alert_type`, `message`, `fingerprint`)
4. **Filtro temporal:** eventos dentro de `EVENTS_LOOKBACK_DAYS` (`.env`, default 30)
5. **Deduplicação:** não incluir se já existir `Alert` com mesmo `fingerprint` ou combinação (`ticker`, `alert_type`, data-base)
6. Formatação de mensagem (texto plano; HTML fica no job):

   ```
   PETR4 anunciou dividendos de R$ 1,25 por ação.
   Data-base: 15/08/2026 | Pagamento: 30/08/2026
   ```

### Config — `app/config.py` + `.env.example`

- `events_lookback_days: int = 30`

### Migration Alembic

- Documentar novos valores de `alert_type`: `dividend`, `jcp`, `corporate_event`
- Se necessário índice em `(alert_type, created_at)` — criar migration apenas se justificado
- `alembic revision --autogenerate` + revisar

## Fora de escopo

- Job, Telegram, API
- IA interpretativa

## Critérios de aceite

- [x] `EventAnalyzer.build_highlights(...)` retorna só eventos novos
- [x] Dedup funciona contra registros existentes em `alerts`
- [x] Migration aplicável com `alembic upgrade head`
- [x] Testes unitários do analyzer (sem HTTP)

## Notas para o implementador

- Valores monetários: formato brasileiro `R$ X,XX`
- Datas: `DD/MM/AAAA`
- Tom neutro — rule `financial-disclaimer`
- Marcar MVP2-03 e MVP2-04 concluídos no backlog
