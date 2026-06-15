# 06 — Operação local do radar (WSL)

**Estória:** MVP1-07
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md#mvp1-07--operação-local-do-radar-wsl)

> **Como invocar:** "Implemente a estória MVP1-07 conforme `docs/prompts/fase-1/06-operacao-local-wsl.md`"

## Contexto

O MVP1-04 entregou `jobs/scheduler.py` e `run_scheduler.py`, mas o radar ainda depende de execução manual ou de um terminal aberto. Para uso no PC (WSL), precisamos de **operação documentada e configurada**.

**Pré-requisitos já concluídos:** MVP1-04 (scheduler), banco Docker na porta 5433, `.env` configurado, fluxo validado com `run_job.py` e API.

Leia: `run_scheduler.py`, `run_job.py`, `docker-compose.yml`, `README.md`, `.env.example`

## Objetivo

Permitir que o usuário ligue o ambiente no WSL e receba o radar no Telegram **todo dia no horário configurado**, sem intervenção manual.

## Escopo

### 1. Estratégia de agendamento (escolher uma como padrão)

| Opção | Quando usar | Prós | Contras |
|---|---|---|---|
| **cron** (padrão) | Uso diário no PC | Sem processo 24/7; dispara `run_job.py` no horário | WSL precisa estar ativo; cron do Linux |
| **tmux** (alternativa) | Debug e validação | Simples de inspecionar logs ao vivo | Terminal/sessão; processo sempre ativo |

**Implementar cron como padrão.** Documentar tmux como alternativa na seção "Modo debug".

### 2. Script de execução do job (cron)

Criar `scripts/run_daily_radar.sh` que:

- Ativa o venv do projeto
- Carrega variáveis do `.env` (ou garante cwd correto para o pydantic-settings ler `.env`)
- Executa `python run_job.py`
- Redireciona saída para log em `logs/radar-YYYYMMDD.log` (criar pasta `logs/` se necessário; adicionar `logs/` ao `.gitignore` se ausente)

O cron deve chamar esse script, não `run_scheduler.py` diretamente (evita processo 24/7).

Exemplo de entrada cron (horário de Brasília, alinhado ao `.env`):

```cron
30 18 * * * /home/wneto/projects/radar-financeiro-ia/scripts/run_daily_radar.sh
```

> Ajustar usuário/caminho conforme o ambiente real do usuário.

### 3. Documentação operacional

Atualizar `README.md` com seção **"Operação local (WSL)"** contendo:

**Ligar ambiente:**
1. `docker compose up -d` (Postgres)
2. Verificar `.env` (chaves BRAPI, Gemini, Telegram, `MONITORED_ASSETS`)
3. Instalar/configurar entrada no cron (comando `crontab -e` e exemplo)
4. (Opcional) subir API: `uvicorn app.main:app --reload`

**Desligar ambiente:**
1. Remover ou comentar entrada do cron (`crontab -e`)
2. `docker compose down` (se quiser parar o banco)

**Verificar se está funcionando:**
- `docker compose ps` — Postgres na porta 5433
- `crontab -l` — entrada do radar presente
- `tail -f logs/radar-*.log` — última execução
- Teste manual: `python run_job.py` ou `POST /radar/run`

**Modo debug (tmux):**
- Comandos para `tmux new -s radar`, rodar `python run_scheduler.py`, desanexar e reanexar

### 4. Arquivos auxiliares

| Arquivo | Ação |
|---|---|
| `scripts/run_daily_radar.sh` | Criar (executável) |
| `logs/.gitkeep` ou `.gitignore` | Garantir que logs não vão pro git |
| `README.md` | Seção operação local |
| `.env.example` | Comentário sobre `RADAR_SCHEDULE_*` usado pelo cron (referência manual) |

### 5. Validação pós-implementação

Checklist para o usuário validar:

- [ ] Postgres sobe com `docker compose up -d`
- [ ] `scripts/run_daily_radar.sh` executa `run_job.py` com sucesso
- [ ] Entrada no `crontab -l` aparece com horário correto
- [ ] Log gerado em `logs/` após execução manual do script
- [ ] Telegram recebe mensagem no teste manual
- [ ] Documentação no README está clara para repetir o processo

## Fora de escopo

- VPS, systemd, Docker para o app Python
- Auto-start do WSL no boot do Windows (mencionar como nota, não implementar)
- Alterar lógica do `DailyRadarJob` ou collectors
- BRAPI 1 ativo por requisição (estória separada)

## Critérios de aceite

- [x] `scripts/run_daily_radar.sh` existe e roda o job com log
- [x] Cron documentado e configurável conforme `RADAR_SCHEDULE_HOUR/MINUTE`
- [x] README com checklist ligar/desligar/verificar
- [x] tmux documentado como alternativa
- [x] `logs/` ignorado pelo git
- [x] Usuário consegue validar com teste manual do script (sem esperar o horário real)

## Notas para o implementador

- **WSL:** o cron só dispara se o WSL estiver rodando. Mencionar isso no README.
- **Horário:** cron do Linux usa timezone do sistema; documentar `timedatectl` ou `TZ=America/Sao_Paulo` se necessário.
- **Segurança:** não commitar `.env`; o script deve rodar a partir do diretório do projeto.
- Se o caminho do projeto for diferente de `/home/wneto/projects/radar-financeiro-ia`, usar variável ou detectar via `dirname` no script.
