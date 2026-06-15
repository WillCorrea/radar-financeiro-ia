# 05 — Testes do fluxo principal

**Estória:** MVP1-06
**Backlog:** [`docs/backlog/fase-1/fase-1-mvp1.md`](../../backlog/fase-1/fase-1-mvp1.md#mvp1-06--testes-do-fluxo-principal)

> **Como invocar:** "Implemente a estória MVP1-06 conforme `docs/prompts/fase-1/05-testes.md`"

## Contexto

O projeto não tem testes. Com MVP1-01 a MVP1-05 concluídos, precisamos de cobertura mínima do fluxo.

**Pré-requisito:** MVP1-01 e MVP1-02 concluídos (mínimo para testes de analyzer).

## Escopo

**Novo diretório:** `tests/`

1. `tests/test_price_analyzer.py`
   - Prioridade mês > semana > dia
   - Formato das mensagens
   - FII abaixo do VP (quando dados disponíveis)

2. `tests/test_daily_radar_job.py`
   - `_build_message` gera formato esperado
   - Mock de dependências externas

3. `tests/test_stocks_collector.py`
   - Mock httpx para resposta da brapi
   - Verificar parsing de `QuoteData`

4. Adicionar `pytest` ao `requirements.txt` se ausente

## Fora de escopo

- Testes de integração com banco real
- Testes E2E com Telegram

## Critérios de aceite

- [ ] `pytest` passa sem erros
- [ ] Testes não dependem de API externa (mocks)
- [ ] Cobertura dos cenários principais do MVP 1
