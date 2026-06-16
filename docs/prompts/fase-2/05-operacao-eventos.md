# 05 — Operação local (job de eventos)

**Estória:** MVP2-07
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md#mvp2-07--operação-local-run_events_job)

> **Como invocar:** "Implemente a estória MVP2-07 conforme `docs/prompts/fase-2/05-operacao-eventos.md`"

## Contexto

O radar diário já roda via cron (`scripts/run_daily_radar.sh`). O job de eventos precisa do mesmo tratamento operacional.

Leia: `scripts/run_daily_radar.sh`, `README.md` (seção Operação local), `.env.example`

## Escopo

1. **`scripts/run_events_job.sh`**
   - Ativa venv, `cd` no projeto, log em `logs/events-YYYYMMDD.log`
   - Executa `python run_events_job.py`
2. **`.env.example`**
   - `EVENTS_LOOKBACK_DAYS=7`
   - `EVENTS_SCHEDULE_HOUR=19` / `EVENTS_SCHEDULE_MINUTE=0` (exemplo — após radar)
3. **`scripts/print-events-cron-entry.sh`** (opcional) — gera linha cron
4. **Documentação** em `README.md` ou `docs/operations/events-job.md`:
   - Teste manual
   - Exemplo crontab
   - WSL precisa estar ativo

## Fora de escopo

- systemd, VPS
- Integrar no mesmo script do radar (manter separados)

## Critérios de aceite

- [x] `./scripts/run_events_job.sh` roda e grava log
- [x] README ou doc de operações atualizado
- [x] `.env.example` com variáveis de eventos
- [x] Scripts com LF (`.gitattributes`)

## Notas para o implementador

- `chmod +x` documentado
- Marcar MVP2-07 concluída no backlog
