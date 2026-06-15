# 07 — BRAPI: 1 ativo por requisição

**Estória:** MVP1-08
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md#mvp1-08--brapi-1-ativo-por-requisição)

> **Como invocar:** "Implemente a estória MVP1-08 conforme `docs/prompts/fase-1/07-brapi-um-ativo-por-requisicao.md`"

## Contexto

O plano gratuito da [brapi.dev](https://brapi.dev) limita a **1 ativo por requisição**. Com `MONITORED_ASSETS=PETR4,VALE3,HGLG11,MXRF11`, os collectors atuais concatenam símbolos e podem retornar erro 400 ou dados parciais.

Leia: `collectors/stocks_collector.py`, `collectors/fii_collector.py`, `jobs/daily_radar_job.py`, `.cursor/rules/local-dev-context.mdc`

## Escopo

### Configuração — `app/config.py` e `.env.example`

1. Adicionar `BRAPI_REQUEST_DELAY_SECONDS` (float, default `0.2`)
2. Pausa aplicada **entre** requisições consecutivas (não antes da primeira)

### `collectors/stocks_collector.py`

1. Refatorar `fetch_quotes()` para iterar **um ticker por vez**
2. Extrair lógica de uma única chamada (ex.: `_fetch_single_quote()`) reutilizável
3. Agregar resultados na mesma ordem dos tickers solicitados (ignorar tickers que falharem)
4. Manter `_safe_float`, timeout 30s e cálculo de variação semana/mês
5. **Falha parcial:** erro em um ticker (HTTP 4xx/5xx, rede ou payload vazio) → log de warning e **continuar** com os próximos
6. **401 (token):** continua propagando `ValueError` com mensagem atual — autenticação inválida afeta todas as chamadas

### `collectors/fii_collector.py`

1. Quote via `StocksCollector` herda o comportamento por ticker
2. `_fetch_indicators()` e `_fetch_historical_prices()`: **1 símbolo por requisição**
3. Mesma regra de continuidade: falha em um FII não bloqueia os demais
4. Reutilizar helper de delay do módulo de stocks (ex.: `apply_brapi_request_delay`)

### Testes — `tests/test_stocks_collector.py`

1. Teste com 2+ tickers verificando **N chamadas** `client.get` (mock)
2. Teste de falha parcial: um ticker retorna erro, outro retorna OK — lista final contém só o sucesso
3. Manter testes existentes passando

### Testes — `tests/test_fii_collector.py` *(obrigatório)*

1. Teste com 2 FIIs verificando requisições individuais nos endpoints de quote, indicadores e histórico (mock)
2. Teste de falha parcial em indicadores: um FII falha, outro retorna NAV — quote enriquecido só para o sucesso

## Fora de escopo

- Upgrade de plano BRAPI
- Cache de cotações ou fila assíncrona
- Alterar `PriceAnalyzer`, `SummaryAgent`, `DailyRadarJob` (exceto se necessário para imports)
- Novos endpoints de API
- Testes de integração real contra a BRAPI (apenas mock)

## Critérios de aceite

- [x] `fetch_quotes(["PETR4", "VALE3"])` dispara 2 requisições separadas à BRAPI (ações)
- [x] `FiiCollector` com 2 FIIs dispara requisições individuais nos endpoints de indicadores e histórico
- [x] `BRAPI_REQUEST_DELAY_SECONDS` configurável no `.env` / `.env.example`
- [x] `python run_job.py` completa com os 4 ativos padrão do `.env.example`
- [x] `pytest` passa sem erros (`test_stocks_collector` + `test_fii_collector`)
- [x] Nenhuma regressão em mensagens de erro 401 (token ausente/inválido)

## Referência — comportamento esperado

```python
# Antes (plano free quebra)
collector.fetch_quotes(["PETR4", "VALE3"])
# GET /api/quote/PETR4,VALE3

# Depois
collector.fetch_quotes(["PETR4", "VALE3"])
# GET /api/quote/PETR4
# sleep(BRAPI_REQUEST_DELAY_SECONDS)
# GET /api/quote/VALE3
```

## Notas para o implementador

- FIIs no `/api/quote` continuam **sem** `range`/`interval` (`include_historical=False`)
- Preservar mensagens de erro úteis já existentes (401 token)
- Não logar token nem URL com credenciais
- Nos testes, mockar `time.sleep` para não atrasar a suíte
- Ao concluir, marcar MVP1-08 como concluído no backlog
