# Job de eventos — operação local

Pipeline separada do radar diário: dividendos, JCP e fatos relevantes (CVM). Entrypoint: `run_events_job.py`.

## Pré-requisitos

- Mesmo setup do radar: venv, `.env`, Postgres (`docker compose up -d`), migrations (`alembic upgrade head`)
- Variáveis: `BRAPI_TOKEN`, `TELEGRAM_*`, `MONITORED_ASSETS`, `EVENTS_LOOKBACK_DAYS`

## Teste manual

```bash
cd ~/projects/radar-financeiro-ia
source .venv/bin/activate
docker compose up -d

python run_events_job.py
```

Saídas possíveis:

- `Alertas de eventos enviados com sucesso.` — houve eventos novos; Telegram enviado
- `Nenhum evento novo. Telegram não enviado.` — pipeline OK, sem novidade (dedup ou janela vazia)

## Script com log

```bash
chmod +x scripts/run_events_job.sh scripts/print-events-cron-entry.sh
./scripts/run_events_job.sh
tail logs/events-$(date +%Y%m%d).log
```

Logs diários em `logs/events-YYYYMMDD.log` (gitignored).

## Agendamento (cron)

Horário sugerido: **após o radar diário** (ex.: radar 18:30, eventos 19:00). Configure no `.env`:

```env
EVENTS_SCHEDULE_HOUR=19
EVENTS_SCHEDULE_MINUTE=0
```

Gere a linha do cron:

```bash
./scripts/print-events-cron-entry.sh
crontab -e
```

Exemplo com radar às 18:30 e eventos às 19:00:

```cron
CRON_TZ=America/Sao_Paulo
30 18 * * * /home/wneto/projects/radar-financeiro-ia/scripts/run_daily_radar.sh
0 19 * * * /home/wneto/projects/radar-financeiro-ia/scripts/run_events_job.sh
```

> **WSL:** o cron só dispara com o WSL em execução. Abra o WSL antes do horário agendado após reiniciar o PC.

## Verificação

```bash
crontab -l
ls -la logs/events-*.log
tail -f logs/events-$(date +%Y%m%d).log
```

## Referências

- Estória: [MVP2-07](../backlog/fase-2/fase-2-mvp2.md#mvp2-07--operação-local-run_events_job)
- Fontes de dados: [events-data-sources.md](events-data-sources.md)
- Prompt: [05-operacao-eventos.md](../prompts/fase-2/05-operacao-eventos.md)
