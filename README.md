# EnterpriseOps AI

Enterprise AI investigation platform combining structured enterprise data, RAG, controlled agentic workflows, evaluation, observability, and reliability engineering.

> Work in progress — the system is being developed incrementally, with a focus on production-oriented AI engineering practices.

## Use Case

EnterpriseOps AI investigates operational questions across structured enterprise data and internal enterprise knowledge.

The initial scenario focuses on investigating why purchase orders from a supplier are being delayed.

The system is designed to progressively combine:

- deterministic enterprise data retrieval
- retrieval-augmented generation (RAG)
- controlled AI tools and orchestration
- evidence-grounded LLM synthesis
- evaluation and observability
- reliability and controlled degradation

## Current Status

The deterministic enterprise-data foundation is complete.

Currently implemented:

- FastAPI application foundation
- PostgreSQL + pgvector development environment
- SQLAlchemy data model
- Alembic schema migrations
- deterministic enterprise seed data
- repository layer for suppliers, purchase orders, and service tickets
- separate PostgreSQL integration-test database
- pytest, Ruff, and strict mypy quality tooling

AI functionality is intentionally being added incrementally after establishing deterministic enterprise data access.

## Architecture

The current deterministic data path is:

```text
Repositories
     ↓
SQLAlchemy
     ↓
PostgreSQL + pgvector
```

The FastAPI application currently exposes the health endpoint and is not yet connected to the repository layer through application routes.

Future AI capabilities will build on the deterministic data foundation rather than replacing enterprise queries with LLM calls.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the evolving system architecture and target MVP design.

## Development

This project uses Python 3.12 and `uv`.

Install dependencies:

```bash
uv sync
```

Create the local environment configuration:

```bash
cp .env.example .env
```

On PowerShell:

```powershell
Copy-Item .env.example .env
```

The example configuration matches the local PostgreSQL service defined in `compose.yaml`.

Start PostgreSQL:

```bash
docker compose up -d
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

Create the deterministic development scenario:

```bash
uv run python -m enterpriseops_ai.db.seed
```

Run the API:

```bash
uv run uvicorn enterpriseops_ai.main:app --reload
```

## Integration Test Database

Repository integration tests use a separate PostgreSQL database named `enterpriseops_test`.

Create it once after starting PostgreSQL:

```bash
docker compose exec postgres psql -U enterpriseops -d postgres -c "CREATE DATABASE enterpriseops_test;"
```

Apply the application migrations to the test database.

### Bash

```bash
POSTGRES_DB=enterpriseops_test uv run alembic upgrade head
```

### PowerShell

```powershell
$env:POSTGRES_DB="enterpriseops_test"
uv run alembic upgrade head
Remove-Item Env:POSTGRES_DB
```

The test database should not be seeded. Individual integration tests create the data they require and run inside transactions that are rolled back afterwards.

## Quality

Run the complete quality suite:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src tests
uv run pytest
```

## Project Roadmap

The MVP is being developed incrementally:

1. deterministic enterprise data foundation
2. baseline RAG over internal enterprise documentation
3. RAG evaluation and retrieval experiments
4. controlled tools and LangGraph orchestration
5. observability and LLMOps
6. reliability and security experiments
7. consolidation, documentation, and demo

The architecture and documentation will evolve as each capability is implemented and evaluated.

## License

MIT
