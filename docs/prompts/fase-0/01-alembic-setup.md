# 01 — Configurar Alembic

**Estória:** F0-06
**Backlog:** [`docs/backlog/fase-0/fase-0-fundacao.md`](../../backlog/fase-0/fase-0-fundacao.md#f0-06--configurar-alembic-para-migrations)

> **Como invocar:** "Implemente a estória F0-06 conforme `docs/prompts/fase-0/01-alembic-setup.md`"
>
> **Momento recomendado:** antes da Fase 2 ou quando houver primeira alteração em `database/models.py`.

## Contexto

O projeto usa `Base.metadata.create_all()` em `database/connection.py`. Precisamos versionar o schema para evoluir o banco com segurança.

Leia: `database/models.py`, `database/connection.py`, `app/config.py`

## Escopo

1. Adicionar `alembic` ao `requirements.txt`
2. Inicializar `alembic/` integrado com `settings.database_url`
3. Gerar migration inicial a partir dos models atuais
4. Documentar comandos básicos (`upgrade`, `revision`) em `docs/` ou README

## Fora de escopo

- Alterar models existentes
- Migrations de dados (seed)

## Critérios de aceite

- [x] `alembic upgrade head` cria tabelas em banco limpo
- [x] `env.py` usa `DATABASE_URL` do projeto
- [x] Models importados corretamente para autogenerate
- [x] Instruções de uso documentadas
