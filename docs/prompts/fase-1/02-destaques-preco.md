# 02 — Destaques de preço e FII abaixo do VP

**Estórias:** MVP1-02, MVP1-03
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md)

> **Como invocar:** "Implemente as estórias MVP1-02 e MVP1-03 conforme `docs/prompts/fase-1/02-destaques-preco.md`"

## Contexto

O `PriceAnalyzer` hoje gera destaque apenas com variação do dia. Com MVP1-01 concluído, `QuoteData` já traz semana e mês.

**Pré-requisito:** MVP1-01 concluído.

Leia: `docs/product/roadmap.md` (exemplos de saída), `.cursor/rules/financial-disclaimer.mdc`

## Escopo

**Arquivo principal:** `analyzers/price_analyzer.py`

### Prioridade de destaque (um por ativo)

1. Variação mensal significativa (|Δ| >= 3%)
2. Senão, variação semanal significativa (|Δ| >= 2%)
3. Senão, variação do dia
4. Para FIIs (ticker termina em `11`): se VP disponível e preço < VP → `"negocia abaixo do valor patrimonial"`

### Formato das mensagens

```
PETR4 caiu 3,2% na semana.
VALE3 subiu 4,1% no mês.
HGLG11 negocia abaixo do valor patrimonial.
```

Se necessário, estender `QuoteData` com campo `book_value` ou similar — alteração mínima no collector, sem lógica de análise lá.

## Fora de escopo

- Agendamento (MVP1-04)
- Endpoints API (MVP1-05)
- Testes (MVP1-06)

## Critérios de aceite

- [x] Um destaque por ativo, sem redundância
- [x] Prioridade mês > semana > dia respeitada
- [x] FIIs com alerta de VP quando dados disponíveis
- [x] Fallback gracioso quando VP indisponível
- [x] `python run_job.py` gera mensagem no formato do roadmap
