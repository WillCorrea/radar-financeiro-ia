# 01 — Coletar variações semana/mês

**Estória:** MVP1-01
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md#mvp1-01--coletar-variação-semanamês)

> **Como invocar:** "Implemente a estória MVP1-01 conforme `docs/prompts/fase-1/01-coletar-variacoes.md`"

## Contexto

O `StocksCollector` popula apenas `change_percent_day`. O roadmap exige destaques semanais e mensais, então precisamos enriquecer a `QuoteData` antes de alterar os analyzers.

Leia: `docs/architecture/pipeline.md`, `.cursor/rules/architecture-pipeline.mdc`

## Escopo

**Arquivo principal:** `collectors/stocks_collector.py`

1. Popular `change_percent_week` e `change_percent_month` em `QuoteData`
2. Usar brapi.dev — verificar campos no endpoint `/quote/{symbols}`; se insuficiente, usar endpoint histórico
3. Manter `_safe_float`, timeout de 30s e `raise_for_status`
4. `FiiCollector` não precisa de alteração se delegar ao `StocksCollector`

## Fora de escopo

- Alterar `PriceAnalyzer` (estória MVP1-02)
- Novos endpoints de API
- Testes (estória MVP1-06)

## Critérios de aceite

- [x] `fetch_quotes()` retorna `change_percent_week` e `change_percent_month` quando a API permitir
- [x] Valores `None` quando dados indisponíveis (sem quebrar o fluxo)
- [x] `python run_job.py` continua funcionando

## Referência

```python
@dataclass
class QuoteData:
    ticker: str
    price: float
    change_percent_day: float | None = None
    change_percent_week: float | None = None   # ← popular
    change_percent_month: float | None = None  # ← popular
    name: str | None = None
```
