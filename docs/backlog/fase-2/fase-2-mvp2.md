# Fase 2 — MVP 2: Eventos Relevantes

**Objetivo:** alertar o investidor sobre eventos além de variação de preço (dividendos, JCP e comunicados).

**Referência:** [`docs/product/roadmap.md`](../../product/roadmap.md#mvp-2--eventos-relevantes)

## Critério de aceite da fase

Quando as estórias obrigatórias estiverem concluídas, `python run_events_job.py` deve gerar e enviar (quando houver novidade):

```
Alerta — Eventos

• PETR4 anunciou dividendos de R$ 1,25 por ação.
  Data-base: 15/08/2026 | Pagamento: 30/08/2026

• VALE3 anunciou JCP de R$ 0,80 por ação.
  Data-base: 10/08/2026 | Pagamento: 25/08/2026
```

Eventos já alertados **não** devem ser reenviados no dia seguinte (deduplicação).

---

## Resumo

| ID | Estória | Prompt | Prioridade | Status |
|---|---|---|---|---|
| MVP2-01 | Coletar dividendos e JCP | [01-coletar-dividendos-jcp.md](../../prompts/fase-2/01-coletar-dividendos-jcp.md) | Alta | concluído |
| MVP2-02 | Coletar fatos relevantes (CVM) | [02-coletar-fatos-relevantes.md](../../prompts/fase-2/02-coletar-fatos-relevantes.md) | Média | concluído |
| MVP2-03 | EventAnalyzer e deduplicação | [03-event-analyzer-e-alertas.md](../../prompts/fase-2/03-event-analyzer-e-alertas.md) | Alta | concluído |
| MVP2-04 | Migration — tipos de alerta de evento | [03-event-analyzer-e-alertas.md](../../prompts/fase-2/03-event-analyzer-e-alertas.md) | Alta | concluído |
| MVP2-05 | Job de eventos (orquestração) | [04-events-job-e-telegram.md](../../prompts/fase-2/04-events-job-e-telegram.md) | Alta | concluído |
| MVP2-06 | Formato Telegram com datas | [04-events-job-e-telegram.md](../../prompts/fase-2/04-events-job-e-telegram.md) | Alta | concluído |
| MVP2-07 | Operação local (`run_events_job`) | [05-operacao-eventos.md](../../prompts/fase-2/05-operacao-eventos.md) | Média | concluído |
| MVP2-08 | Testes do fluxo de eventos | [06-testes-eventos.md](../../prompts/fase-2/06-testes-eventos.md) | Média | concluído |
| MVP2-09 | Endpoints API de eventos | [07-api-endpoints-eventos.md](../../prompts/fase-2/07-api-endpoints-eventos.md) | Baixa | concluído |

**Ordem recomendada:** MVP2-01 → MVP2-02 → MVP2-03/04 → MVP2-05/06 → MVP2-07 → MVP2-08 → MVP2-09

> **MVP2-02** pode ser entregue em versão mínima (estrutura + fonte documentada) se a API CVM exigir mais pesquisa; dividendos/JCP (MVP2-01) são o núcleo obrigatório da fase.

---

## MVP2-01 — Coletar dividendos e JCP

**Como** investidor
**Quero** que o sistema colete proventos em dinheiro anunciados nos meus ativos
**Para** ser alertado sobre dividendos e JCP sem consultar manualmente

**Critérios de aceite:**
- [x] `collectors/dividends_collector.py` criado
- [x] Usa brapi.dev: `GET /api/quote/{ticker}?dividends=true` (1 ticker por requisição + `BRAPI_REQUEST_DELAY_SECONDS`)
- [x] Retorna estrutura tipada (`DividendEvent`) com ticker, tipo (`dividend` / `jcp`), valor, data-base, pagamento
- [x] Falha parcial por ticker (mesmo padrão MVP1-08)
- [x] FIIs: mesmo endpoint; lista vazia quando `cashDividends` indisponível

**Prompt:** [`docs/prompts/fase-2/01-coletar-dividendos-jcp.md`](../../prompts/fase-2/01-coletar-dividendos-jcp.md)
**Status:** concluído

---

## MVP2-02 — Coletar fatos relevantes (CVM)

**Como** investidor
**Quero** ser informado sobre fatos relevantes das empresas que monitoro
**Para** acompanhar comunicados oficiais sem ler o site da CVM

**Critérios de aceite:**
- [x] `collectors/events_collector.py` criado
- [x] Coleta fatos relevantes recentes filtrados por ticker monitorado
- [x] Fonte documentada em `docs/operations/events-data-sources.md`
- [x] Retorna estrutura tipada (`CorporateEvent`): ticker, título, data, url
- [x] Falha da CVM ou CNPJ ausente não quebra o fluxo (lista vazia + log)

**Prompt:** [`docs/prompts/fase-2/02-coletar-fatos-relevantes.md`](../../prompts/fase-2/02-coletar-fatos-relevantes.md)
**Status:** concluído

---

## MVP2-03 — EventAnalyzer e deduplicação

**Como** investidor
**Quero** receber apenas eventos **novos** e relevantes
**Para** não ser spammado com o mesmo dividendo todo dia

**Critérios de aceite:**
- [x] `EventAnalyzer` implementado em `analyzers/event_analyzer.py`
- [x] Filtra eventos recentes (janela configurável, ex.: últimos 7 dias ou desde última execução)
- [x] Deduplica por fingerprint (`ticker + tipo + data-base + valor` ou hash estável)
- [x] Consulta alertas já persistidos antes de incluir na saída
- [x] Formata mensagem conforme exemplo da fase

**Prompt:** [`docs/prompts/fase-2/03-event-analyzer-e-alertas.md`](../../prompts/fase-2/03-event-analyzer-e-alertas.md)
**Status:** concluído

---

## MVP2-04 — Migration — tipos de alerta de evento

**Como** desenvolvedor
**Quero** tipos de alerta explícitos para eventos no banco
**Para** consultar histórico e filtrar na API

**Critérios de aceite:**
- [x] Novos `alert_type`: `dividend`, `jcp`, `corporate_event` (ou equivalente documentado)
- [x] Migration Alembic gerada e aplicável com `alembic upgrade head`
- [x] Sem alteração breaking nos alertas existentes (`price_highlight`, `daily_summary`)

**Prompt:** [`docs/prompts/fase-2/03-event-analyzer-e-alertas.md`](../../prompts/fase-2/03-event-analyzer-e-alertas.md)
**Status:** concluído

---

## MVP2-05 — Job de eventos (orquestração)

**Como** investidor
**Quero** um job dedicado que rode a pipeline de eventos
**Para** separar alertas de preço (radar diário) de alertas corporativos

**Critérios de aceite:**
- [x] `jobs/events_job.py` com classe `EventsJob`
- [x] Fluxo: resolver tickers → collectors → `EventAnalyzer` → persistir `Alert` → Telegram
- [x] Entrypoint `run_events_job.py` na raiz
- [x] Reutiliza `settings.asset_list` / carteira do usuário (mesmo padrão do `DailyRadarJob`)
- [x] Não envia mensagem vazia se não houver eventos novos

**Prompt:** [`docs/prompts/fase-2/04-events-job-e-telegram.md`](../../prompts/fase-2/04-events-job-e-telegram.md)
**Status:** concluído

---

## MVP2-06 — Formato Telegram com datas

**Como** investidor
**Quero** alertas legíveis com datas de data-base e pagamento
**Para** saber quando comprar/vender para ter direito ao provento (informação, sem recomendação)

**Critérios de aceite:**
- [x] Mensagem segue tom neutro (rule `financial-disclaimer`)
- [x] Formato: ticker, tipo, valor, data-base, pagamento (quando disponível)
- [x] Datas em `DD/MM/AAAA`
- [x] HTML Telegram compatível (mesmo padrão do radar diário)

**Prompt:** [`docs/prompts/fase-2/04-events-job-e-telegram.md`](../../prompts/fase-2/04-events-job-e-telegram.md)
**Status:** concluído

---

## MVP2-07 — Operação local (`run_events_job`)

**Como** usuário local
**Quero** rodar e agendar o job de eventos no WSL
**Para** receber alertas automaticamente

**Critérios de aceite:**
- [x] Documentação no README ou `docs/operations/`
- [x] Variáveis no `.env.example`: janela de eventos, horário opcional (`EVENTS_SCHEDULE_*`)
- [x] Script shell opcional (ex.: `scripts/run_events_job.sh`) seguindo padrão do radar
- [x] Cron documentado (pode ser 1x/dia em horário diferente do radar)

**Prompt:** [`docs/prompts/fase-2/05-operacao-eventos.md`](../../prompts/fase-2/05-operacao-eventos.md)
**Status:** concluído

---

## MVP2-08 — Testes do fluxo de eventos

**Como** desenvolvedor
**Quero** testes automatizados do MVP 2
**Para** evitar regressões nos collectors e no analyzer

**Critérios de aceite:**
- [x] Testes de `DividendsCollector` (mock httpx)
- [x] Testes de `EventAnalyzer` (dedup + formatação)
- [x] Teste do `EventsJob` (mock collectors + telegram)
- [x] `pytest` passa sem erros

**Prompt:** [`docs/prompts/fase-2/06-testes-eventos.md`](../../prompts/fase-2/06-testes-eventos.md)
**Status:** concluído

---

## MVP2-09 — Endpoints API de eventos

**Como** desenvolvedor / integrador
**Quero** disparar o job de eventos e filtrar alertas por tipo via API
**Para** testar e integrar sem CLI

**Critérios de aceite:**
- [x] `POST /events/run` dispara `EventsJob`
- [x] `GET /alerts?alert_type=dividend` (ou tipos novos) funciona com filtros existentes
- [x] Router registrado em `app/main.py`

**Prompt:** [`docs/prompts/fase-2/07-api-endpoints-eventos.md`](../../prompts/fase-2/07-api-endpoints-eventos.md)
**Status:** concluído

---

## Fora de escopo da Fase 2

- Interpretação IA de eventos (MVP 3)
- Resultados trimestrais com análise profunda
- Mudanças de rating de agências
- Carteira por usuário avançada (MVP 4)
- WhatsApp
