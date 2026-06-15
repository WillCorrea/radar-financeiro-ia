# Migrations do banco (Alembic)

O schema do PostgreSQL é versionado com [Alembic](https://alembic.sqlalchemy.org/), integrado aos models em `database/models.py` e à `DATABASE_URL` do `.env`.

## Pré-requisitos

```bash
cd ~/projects/radar-financeiro-ia
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d
```

## Comandos básicos

| Comando | Uso |
|---|---|
| `alembic current` | Revisão aplicada no banco |
| `alembic history` | Lista migrations |
| `alembic upgrade head` | Aplica todas as migrations pendentes |
| `alembic downgrade -1` | Reverte a última migration |
| `alembic revision --autogenerate -m "descricao"` | Gera migration a partir de mudanças nos models |

## Banco novo (primeiro setup)

Quando o Postgres está vazio:

```bash
alembic upgrade head
```

Isso cria as 6 tabelas: `users`, `assets`, `user_assets`, `market_snapshots`, `alerts`, `messages_sent`.

## Banco já existente (migração do `create_all`)

Se as tabelas já foram criadas por `init_db()` / `create_all()` (ambiente local em uso), **não** rode `upgrade head` de imediato — marque a migration inicial como já aplicada:

```bash
alembic stamp head
alembic current   # deve mostrar 001_initial (head)
```

Depois disso, novas alterações em `database/models.py` seguem o fluxo normal com `revision --autogenerate` + `upgrade head`.

## Fluxo para alterar o schema

1. Edite `database/models.py`
2. Gere a migration:
   ```bash
   alembic revision --autogenerate -m "adiciona tabela eventos"
   ```
3. Revise o arquivo em `alembic/versions/` (autogenerate pode omitir detalhes)
4. Aplique:
   ```bash
   alembic upgrade head
   ```

## `init_db()` vs Alembic

`database/connection.py` ainda expõe `init_db()` com `create_all()` para compatibilidade com o MVP 1. Em novos ambientes, prefira `alembic upgrade head`. O `init_db()` será removido quando todas as entradas do app usarem apenas migrations.

## Referência

- Estória: [F0-06](../backlog/fase-0/fase-0-fundacao.md#f0-06--configurar-alembic-para-migrations)
- Prompt: [01-alembic-setup.md](../prompts/fase-0/01-alembic-setup.md)
