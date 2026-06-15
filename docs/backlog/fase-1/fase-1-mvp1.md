# Fase 1 — MVP 1: Radar Diário

**Objetivo:** completar o radar diário funcional de ponta a ponta.

**Referência:** [`docs/product/roadmap.md`](../../product/roadmap.md#mvp-1--radar-diário)

## Critério de aceite da fase

Quando todas as estórias estiverem concluídas, `python run_job.py` deve gerar:

```
Radar Financeiro - 14/06/2026

• PETR4 caiu 3,2% na semana.
• VALE3 subiu 4,1% no mês.
• HGLG11 negocia abaixo do valor patrimonial.

Resumo IA:
O mercado apresenta sinais mistos, com destaque para o setor de commodities e fundos imobiliários.
```

---

## Resumo

| ID | Estória | Prompt | Prioridade | Status |
|---|---|---|---|---|
| MVP1-01 | Coletar variação semana/mês | [01-coletar-variacoes.md](../../prompts/fase-1/01-coletar-variacoes.md) | Alta | concluído |
| MVP1-02 | Destaques inteligentes de preço | [02-destaques-preco.md](../../prompts/fase-1/02-destaques-preco.md) | Alta | concluído |
| MVP1-03 | Alerta FII abaixo do VP | [02-destaques-preco.md](../../prompts/fase-1/02-destaques-preco.md) | Média | concluído |
| MVP1-04 | Agendamento diário automático | [03-scheduler.md](../../prompts/fase-1/03-scheduler.md) | Alta | concluído |
| MVP1-05 | Endpoints de radar e histórico | [04-api-endpoints.md](../../prompts/fase-1/04-api-endpoints.md) | Média | concluído |
| MVP1-06 | Testes do fluxo principal | [05-testes.md](../../prompts/fase-1/05-testes.md) | Média | concluído |
| MVP1-07 | Operação local do radar (WSL) | [06-operacao-local-wsl.md](../../prompts/fase-1/06-operacao-local-wsl.md) | Alta | concluído |
| MVP1-08 | BRAPI — 1 ativo por requisição | [07-brapi-um-ativo-por-requisicao.md](../../prompts/fase-1/07-brapi-um-ativo-por-requisicao.md) | Alta | concluído |

**Ordem recomendada:** MVP1-01 → MVP1-02/03 → MVP1-04 → MVP1-05 → MVP1-06 → MVP1-07 → MVP1-08

---

## MVP1-01 — Coletar variação semana/mês

**Como** investidor
**Quero** que o sistema colete variações semanais e mensais dos ativos
**Para** receber destaques com tendências, não só o dia

**Critérios de aceite:**
- [x] `QuoteData` populada com `change_percent_week` e `change_percent_month`
- [x] Dados obtidos via brapi.dev (quote ou histórico, conforme disponível)
- [x] `FiiCollector` herda os mesmos dados automaticamente
- [x] Tratamento de erro mantido (`_safe_float`, timeout httpx)

**Prompt:** [`docs/prompts/fase-1/01-coletar-variacoes.md`](../../prompts/fase-1/01-coletar-variacoes.md)
**Status:** concluído

---

## MVP1-02 — Destaques inteligentes de preço

**Como** investidor
**Quero** ver o destaque mais relevante de cada ativo (mês, semana ou dia)
**Para** entender rapidamente o que mudou sem informação redundante

**Critérios de aceite:**
- [x] Um destaque por ativo (não três)
- [x] Prioridade: mês (|Δ| >= 3%) → semana (|Δ| >= 2%) → dia
- [x] Formato: `PETR4 caiu 3,2% na semana.` / `VALE3 subiu 4,1% no mês.`
- [x] Depende de MVP1-01

**Prompt:** [`docs/prompts/fase-1/02-destaques-preco.md`](../../prompts/fase-1/02-destaques-preco.md)
**Status:** concluído

---

## MVP1-03 — Alerta FII abaixo do VP

**Como** investidor de FIIs
**Quero** ser alertado quando um FII negocia abaixo do valor patrimonial
**Para** acompanhar oportunidades de desconto sem consultar manualmente

**Critérios de aceite:**
- [x] FIIs identificados por ticker terminado em `11`
- [x] Mensagem: `HGLG11 negocia abaixo do valor patrimonial.`
- [x] Regra aplicada quando dados de VP estiverem disponíveis na API
- [x] Se VP indisponível, fallback para destaque de preço (MVP1-02)
- [x] Implementado junto com MVP1-02 no mesmo prompt

**Prompt:** [`docs/prompts/fase-1/02-destaques-preco.md`](../../prompts/fase-1/02-destaques-preco.md)
**Status:** concluído

---

## MVP1-04 — Agendamento diário automático

**Como** investidor
**Quero** receber o radar automaticamente todo dia
**Para** não depender de execução manual do job

**Critérios de aceite:**
- [x] `jobs/scheduler.py` com APScheduler
- [x] Horário configurável via `.env` (`RADAR_SCHEDULE_HOUR`, `RADAR_SCHEDULE_MINUTE`)
- [x] Default: 18:30
- [x] Entrypoint `run_scheduler.py` ou integração com API
- [x] `.env.example` atualizado

**Prompt:** [`docs/prompts/fase-1/03-scheduler.md`](../../prompts/fase-1/03-scheduler.md)
**Status:** concluído

---

## MVP1-05 — Endpoints de radar e histórico

**Como** desenvolvedor / integrador
**Quero** endpoints para disparar o radar e consultar histórico
**Para** testar, integrar e consultar alertas via API

**Critérios de aceite:**
- [x] `POST /radar/run` dispara o job manualmente
- [x] `GET /alerts` lista alertas (query: `limit`, `alert_type`)
- [x] `GET /messages` lista mensagens enviadas
- [x] Routers registrados em `app/main.py`
- [x] Usa `get_db()` de `database/connection.py`

**Prompt:** [`docs/prompts/fase-1/04-api-endpoints.md`](../../prompts/fase-1/04-api-endpoints.md)
**Status:** concluído

---

## MVP1-06 — Testes do fluxo principal

**Como** desenvolvedor
**Quero** testes automatizados do fluxo do MVP 1
**Para** garantir que mudanças futuras não quebrem o radar

**Critérios de aceite:**
- [x] Testes de `PriceAnalyzer` (prioridade mês/semana/dia, FII)
- [x] Teste de formato da mensagem do job
- [x] Mock de API externa nos testes de collector
- [x] `pytest` passa sem erros

**Prompt:** [`docs/prompts/fase-1/05-testes.md`](../../prompts/fase-1/05-testes.md)
**Status:** concluído

---

## MVP1-07 — Operação local do radar (WSL)

**Como** usuário do radar no meu PC
**Quero** o ambiente configurado para executar o radar automaticamente todo dia
**Para** receber o Telegram sem rodar comandos manualmente

**Contexto:** o MVP1-04 entregou o código do scheduler (`run_scheduler.py`), mas ainda falta documentar e configurar a **operação no dia a dia** no WSL (banco ativo, agendamento em background, checklist de subida/parada e verificação).

**Critérios de aceite:**
- [x] Documentação de como subir o ambiente completo (Postgres + agendamento)
- [x] Estratégia de agendamento definida e configurada no WSL (**cron** como padrão; **tmux** documentado como alternativa para debug)
- [x] Horário respeita `RADAR_SCHEDULE_HOUR` e `RADAR_SCHEDULE_MINUTE` do `.env`
- [x] Checklist "ligar ambiente" e "desligar ambiente" no README ou `docs/`
- [x] Instruções de verificação (processo ativo, logs, teste manual do job)
- [x] Dependências mínimas documentadas: Postgres via Docker; API **não** obrigatória para o radar diário

**Fora de escopo:**
- Deploy em VPS ou servidor remoto
- systemd em produção
- API sempre ligada
- Múltiplos horários por usuário (MVP 4)

**Prompt:** [`docs/prompts/fase-1/06-operacao-local-wsl.md`](../../prompts/fase-1/06-operacao-local-wsl.md)
**Status:** concluído

---

## MVP1-08 — BRAPI: 1 ativo por requisição

**Como** investidor no plano gratuito da BRAPI
**Quero** que a coleta funcione com vários ativos em `MONITORED_ASSETS`
**Para** receber o radar completo sem erro 400 por limite de símbolos por chamada

**Contexto:** o plano gratuito da brapi.dev aceita **1 ativo por requisição**. Hoje `StocksCollector` e `FiiCollector` enviam vários tickers em uma única URL (`/quote/PETR4,VALE3` ou `symbols=HGLG11,MXRF11`), o que falha ou retorna dados incompletos com token free.

**Critérios de aceite:**
- [x] `StocksCollector.fetch_quotes()` faz uma requisição **por ticker** (ações)
- [x] `FiiCollector.fetch_quotes()` respeita o mesmo limite nos endpoints de quote, indicadores e histórico
- [x] Falha em um ticker não impede a coleta dos demais (resultado parcial + continuidade do job)
- [x] Delay configurável via `BRAPI_REQUEST_DELAY_SECONDS` no `.env`
- [x] `python run_job.py` funciona com `MONITORED_ASSETS=PETR4,VALE3,HGLG11,MXRF11`
- [x] `tests/test_stocks_collector.py` e `tests/test_fii_collector.py` validam múltiplas chamadas HTTP (mock)

**Fora de escopo:**
- Upgrade de plano BRAPI ou cache distribuído
- Retry avançado com fila/backoff exponencial
- Alterar `PriceAnalyzer`, `DailyRadarJob` ou endpoints da API

**Prompt:** [`docs/prompts/fase-1/07-brapi-um-ativo-por-requisicao.md`](../../prompts/fase-1/07-brapi-um-ativo-por-requisicao.md)
**Status:** concluído
