# Radar Financeiro IA

Plataforma de monitoramento financeiro inteligente com automação, análise de dados e IA.

## MVP 1 — Radar Diário

Fluxo:

1. Coleta cotações (ações + FIIs)
2. Analisa destaques de preço
3. Gera resumo via IA (Gemini ou fallback automático)
4. Envia mensagem no Telegram
5. Salva histórico no PostgreSQL

## Estrutura

```
radar-financeiro-ia/
├── app/              # API FastAPI
├── collectors/       # Coleta de dados de mercado
├── analyzers/        # Processamento e regras
├── agents/           # Resumos com IA
├── notifications/    # Telegram / WhatsApp
├── jobs/             # Orquestração
├── alembic/          # Migrations do PostgreSQL
├── scripts/          # Operação local (cron)
├── logs/             # Logs do radar e eventos (gitignored)
└── database/         # Models e conexão
```

## Setup (WSL)

Requer **Python 3.8+** (recomendado **3.10+**). No Ubuntu 20.04 o padrão é 3.8 — funciona com as versões fixadas em `requirements.txt`.

```bash
cd ~/projects/radar-financeiro-ia

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edite .env com suas chaves

docker compose up -d
alembic upgrade head   # banco novo; se já usou create_all, veja docs abaixo
python run_job.py
```

## API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: `GET /health`

## Operação local (WSL)

Radar automático no seu PC via **cron** (padrão). A API é opcional para o envio diário.

### Ligar ambiente

```bash
cd ~/projects/radar-financeiro-ia
source .venv/bin/activate

# 1. Banco
docker compose up -d

# 2. Conferir .env (BRAPI, Gemini, Telegram, MONITORED_ASSETS)

# 3. Testar o script manualmente
chmod +x scripts/run_daily_radar.sh scripts/print-cron-entry.sh
./scripts/run_daily_radar.sh
tail logs/radar-$(date +%Y%m%d).log

# 4. Instalar agendamento no cron
./scripts/print-cron-entry.sh   # mostra a linha com horário do .env
crontab -e                      # cole a linha gerada (inclui CRON_TZ)

# 5. (Opcional) API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Exemplo de entrada no cron (18:30 Brasília):

```cron
CRON_TZ=America/Sao_Paulo
30 18 * * * /home/wneto/projects/radar-financeiro-ia/scripts/run_daily_radar.sh
```

> **WSL:** o cron só dispara com o WSL em execução. Se o PC reiniciar, abra o WSL antes do horário agendado.
>
> **Timezone:** use `CRON_TZ=America/Sao_Paulo` no crontab ou confira com `timedatectl`.

### Desligar ambiente

```bash
crontab -e          # remova ou comente as linhas do radar/eventos
docker compose down # opcional — para o Postgres
```

### Job de eventos (MVP 2)

Alertas de dividendos, JCP e fatos relevantes — **separado** do radar de preço. Não usa Gemini.

```bash
chmod +x scripts/run_events_job.sh scripts/print-events-cron-entry.sh

# Teste manual
python run_events_job.py
# ou com log:
./scripts/run_events_job.sh
tail logs/events-$(date +%Y%m%d).log

# Cron (ex.: 19:00, após radar 18:30)
./scripts/print-events-cron-entry.sh
crontab -e
```

Guia completo: [`docs/operations/events-job.md`](docs/operations/events-job.md).

Exemplo de crontab com os dois jobs:

```cron
CRON_TZ=America/Sao_Paulo
30 18 * * * /home/wneto/projects/radar-financeiro-ia/scripts/run_daily_radar.sh
0 19 * * * /home/wneto/projects/radar-financeiro-ia/scripts/run_events_job.sh
```

### Verificar se está funcionando

```bash
docker compose ps                          # Postgres em 0.0.0.0:5433
crontab -l                                 # entradas do radar e eventos
ls -la logs/                               # radar-YYYYMMDD.log, events-YYYYMMDD.log
tail -f logs/radar-$(date +%Y%m%d).log     # última execução do radar
tail -f logs/events-$(date +%Y%m%d).log    # última execução de eventos
python run_job.py                          # teste manual radar
python run_events_job.py                   # teste manual eventos
```

### Modo debug (tmux)

Alternativa ao cron — processo fica ativo e executa via APScheduler:

```bash
tmux new -s radar
cd ~/projects/radar-financeiro-ia && source .venv/bin/activate
docker compose up -d
python run_scheduler.py
# Desanexar: Ctrl+B, depois D
# Reanexar: tmux attach -t radar
```

## Migrations (Alembic)

Schema versionado em `alembic/`. Guia completo: [`docs/operations/database-migrations.md`](docs/operations/database-migrations.md).

```bash
source .venv/bin/activate
alembic upgrade head          # banco novo
alembic current               # revisão aplicada
alembic revision --autogenerate -m "descricao"   # após alterar models
```

> Banco já criado com `create_all()`? Use `alembic stamp head` uma vez (detalhes no guia).

## Documentação

Toda a visão, roadmap e plano de implementação (Fase 0 → MVP 5) está em [`docs/`](docs/README.md).

- [Plano de implementação](docs/plano-implementacao.md) — documento mestre
- [Backlog Fase 1](docs/backlog/fase-1/fase-1-mvp1.md) — estórias do MVP 1
- [Visão geral](docs/product/visao-geral.md)
- [Roadmap](docs/product/roadmap.md)
- [Arquitetura](docs/architecture/pipeline.md)

## Próximos passos

- [x] MVP 1 — radar diário (código, API, testes, operação local, BRAPI multi-ativo)
- [x] F0-06 — Alembic (migrations)
- [ ] MVP 2 — eventos relevantes — [backlog](docs/backlog/fase-2/fase-2-mvp2.md) · [prompts](docs/prompts/fase-2/README.md)
