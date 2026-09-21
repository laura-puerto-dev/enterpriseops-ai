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

The deterministic enterprise-data foundation, semantic retrieval baseline, retrieval-evaluation foundation, controlled tool layer, LangGraph investigation workflow, evidence-grounded synthesis, and FastAPI investigation endpoint are implemented.

Currently implemented:

- FastAPI application foundation
- PostgreSQL + pgvector development environment
- SQLAlchemy data model
- Alembic schema migrations
- deterministic enterprise seed data
- repository layer for suppliers, purchase orders, and service tickets
- enterprise document corpus
- recursive document chunking
- OpenAI embedding generation
- document and chunk persistence with pgvector
- exact cosine-similarity retrieval with source metadata
- document ingestion and semantic-search scripts
- golden dataset covering answerable, partially answerable, and unanswerable retrieval scenarios
- deterministic retrieval metrics including source hit rate, source coverage, and mean reciprocal rank (MRR)
- semantic evidence-coverage evaluation using a constrained LLM judge with structured output
- deterministic validation of evaluator invariants
- executable retrieval-evaluation baseline
- separate PostgreSQL integration-test database
- pytest, Ruff, and strict mypy quality tooling
- GitHub Actions CI with PostgreSQL + pgvector, schema migrations, quality checks, and integration tests
- controlled read-only enterprise and document tools
- deterministic supplier alias resolution to canonical enterprise identity
- LangGraph investigation workflow with explicit state and conditional routing
- structured natural-language understanding
- evidence-grounded LLM synthesis with explicit sources and limitations
- controlled degradation when supplier resolution is unavailable
- reusable workflow composition shared by CLI and FastAPI
- `POST /ai/investigate` with typed request and response contracts
- API boundary tests using FastAPI dependency overrides

The retrieval baseline has been evaluated end-to-end using real embeddings and semantic retrieval. The evaluation suite now contains 15 cases, including multi-source and multi-evidence challenge scenarios. Across 13 source-evaluable cases, both `top_k=3` and `top_k=5` achieved 100% source hit, 100% mean source coverage, and an MRR of 0.949.

A controlled five-run comparison measured mean semantic evidence coverage of 94.6% for `top_k=3` and 96.1% for `top_k=5`. The LLM-based evidence judge also showed material run-to-run variance, so the small difference was not treated as sufficient evidence to increase the default retrieval context. The MVP therefore retains `top_k=3`, while evaluator calibration against human-labelled examples remains a production consideration.

These measurements establish a controlled baseline for subsequent retrieval experiments. They are intended for comparative evaluation as the retrieval strategy evolves rather than as a claim of production-level accuracy.

Observability, LLMOps, generation evaluation, and additional reliability and security behavior are being added incrementally.

## Architecture

The current investigation path is:

```text
FastAPI
   ↓
LangGraph investigation workflow
   ↓
controlled tools
   ├── structured enterprise tools → repositories → SQLAlchemy
   └── document tool → retrieval service → embeddings + pgvector
   ↓
PostgreSQL + pgvector
   ↓
evidence-grounded LLM synthesis
```

Structured enterprise facts are retrieved deterministically through controlled read-only capabilities rather than reconstructed by the LLM. LangGraph coordinates the known investigation path, including conditional routing and controlled degradation when canonical supplier resolution is unavailable.

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

Add an OpenAI API key to `.env` when running embedding-dependent functionality:

```text
OPENAI_API_KEY=...
```

Ingest the local enterprise document corpus:

```bash
uv run python -m enterpriseops_ai.scripts.ingest_documents
```

Run a semantic retrieval query:

```bash
uv run python -m enterpriseops_ai.scripts.search_documents "What should procurement do when a supplier reports a component shortage?"
```

Run the retrieval evaluation baseline:

```bash
uv run python -m enterpriseops_ai.scripts.evaluate_retrieval
```

The evaluation command requires `OPENAI_API_KEY` because it uses real query embeddings and an LLM-based semantic evidence judge.

Run the API:

```bash
uv run uvicorn enterpriseops_ai.main:app --reload
```

The investigation endpoint requires `OPENAI_API_KEY`. The application can still start and expose `/health` without AI-provider credentials; `/ai/investigate` returns `503 Service Unavailable` when the AI capability is not configured.

Example investigation request:

```bash
curl -X POST http://127.0.0.1:8000/ai/investigate \
  -H "Content-Type: application/json" \
  -d '{"question":"Why are purchase orders from supplier ACME being delayed?"}'
```

The endpoint returns a structured answer containing a summary, findings, evidence, sources, recommended actions, limitations, and any controlled workflow errors.

The same workflow can also be exercised directly through the diagnostic CLI:

```bash
uv run python -m enterpriseops_ai.scripts.run_investigation
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

The same quality pipeline runs automatically in GitHub Actions against a clean PostgreSQL + pgvector environment. CI creates the integration-test database, applies the Alembic migration history from scratch, and then runs formatting, linting, type checking, and tests.

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
