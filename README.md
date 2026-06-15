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
├── scripts/          # Operação local (cron)
├── logs/             # Logs do radar diário (gitignored)
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
crontab -e          # remova ou comente a linha do radar
docker compose down # opcional — para o Postgres
```

### Verificar se está funcionando

```bash
docker compose ps                          # Postgres em 0.0.0.0:5433
crontab -l                                 # entrada do radar presente
ls -la logs/                               # arquivos radar-YYYYMMDD.log
tail -f logs/radar-$(date +%Y%m%d).log     # última execução
python run_job.py                          # teste manual
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

## Documentação

Toda a visão, roadmap e plano de implementação (Fase 0 → MVP 5) está em [`docs/`](docs/README.md).

- [Plano de implementação](docs/plano-implementacao.md) — documento mestre
- [Backlog Fase 1](docs/backlog/fase-1/fase-1-mvp1.md) — estórias do MVP 1
- [Visão geral](docs/product/visao-geral.md)
- [Roadmap](docs/product/roadmap.md)
- [Arquitetura](docs/architecture/pipeline.md)

## Próximos passos

- [x] MVP 1 — radar diário (código, API, testes)
- [ ] Validar operação local (cron + logs) — [`docs/prompts/fase-1/06-operacao-local-wsl.md`](docs/prompts/fase-1/06-operacao-local-wsl.md)
- [ ] F0-06: Alembic (migrations)
- [ ] MVP 2: eventos relevantes (dividendos, fatos relevantes)
