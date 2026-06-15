# 03 — Agendamento diário

**Estória:** MVP1-04
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md#mvp1-04--agendamento-diário-automático)

> **Como invocar:** "Implemente a estória MVP1-04 conforme `docs/prompts/fase-1/03-scheduler.md`"

## Contexto

O job roda apenas via `python run_job.py`. O `apscheduler` já está no `requirements.txt` mas não é usado.

Leia: `jobs/daily_radar_job.py`, `database/connection.py`

## Escopo

1. **Novo arquivo:** `jobs/scheduler.py`
   - APScheduler com trigger diário
   - Executa `DailyRadarJob.run()` com sessão do banco
   - Tratamento básico de erros (log, não derrubar o scheduler)

2. **Novo entrypoint:** `run_scheduler.py` (ou integrar no lifespan da API)

3. **Configuração** em `app/config.py`:
   - `radar_schedule_hour: int = 18`
   - `radar_schedule_minute: int = 30`

4. **Atualizar** `.env.example`:
   ```env
   RADAR_SCHEDULE_HOUR=18
   RADAR_SCHEDULE_MINUTE=30
   ```

## Fora de escopo

- Endpoints API (MVP1-05)
- Múltiplos horários por usuário (MVP 4)

## Critérios de aceite

- [ ] `python run_scheduler.py` inicia e agenda o job
- [ ] Horário configurável via `.env`
- [ ] Default 18:30
- [ ] Job executa sem erro com banco e Telegram configurados
