# 02 — Coletar fatos relevantes

**Estória:** MVP2-02
**Backlog:** [`docs/backlog/fase-2/fase-2-mvp2.md`](../../backlog/fase-2/fase-2-mvp2.md#mvp2-02--coletar-fatos-relevantes-cvm)

> **Como invocar:** "Implemente a estória MVP2-02 conforme `docs/prompts/fase-2/02-coletar-fatos-relevantes.md`"

## Contexto

Fatos relevantes são publicados na **CVM**. A brapi pode não expor endpoint dedicado no plano atual — pesquise fontes antes de implementar.

Leia: `collectors/dividends_collector.py` (padrão do MVP2-01), `docs/architecture/pipeline.md`

## Escopo

**Arquivo principal:** `collectors/events_collector.py`

1. Dataclass `CorporateEvent`:
   - `ticker`, `title`, `published_at`, `summary` (opcional), `source_url` (opcional)
2. `EventsCollector.fetch_events(tickers: list[str]) -> list[CorporateEvent]`
3. **Investigar fonte** (ordem sugerida):
   - API/documentação brapi.dev
   - Dados abertos CVM (RSS, JSON, scraping estável)
   - Fallback: estrutura pronta + retorno vazio + comentário `TODO` com link da fonte escolhida
4. Filtrar por tickers monitorados
5. Janela temporal configurável (ex.: últimos 30 dias) — preparar param ou constante
6. Timeout, falha parcial, sem logar secrets

## Fora de escopo

- Análise IA do conteúdo (MVP 3)
- Resultados trimestrais completos
- Rating de agências

## Critérios de aceite

- [x] Módulo `events_collector.py` existe com interface estável para o `EventAnalyzer`
- [x] Fonte de dados documentada em `docs/operations/events-data-sources.md`
- [x] Teste unitário com mock (httpx)
- [x] Não quebra o fluxo se a fonte falhar (lista vazia + log warning)

## Entrega mínima aceitável

Se a integração CVM exigir mais tempo:

- Collector implementado com **mock/fixture** realista
- Doc explicando bloqueio e próximo passo
- Estória marcada como concluída **somente** se o contrato (`CorporateEvent` + `fetch_events`) estiver estável

## Notas para o implementador

- Preferir httpx + timeout 30s
- 1 requisição por ticker quando a fonte exigir
- Ao concluir, marcar MVP2-02 no backlog
