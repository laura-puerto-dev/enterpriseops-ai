# EnterpriseOps AI — Architecture

| | |
|---|---|
| **Status** | In progress |
| **Last updated** | 2026-09-19 |
| **Scope** | MVP |

## Overview

EnterpriseOps AI is an enterprise investigation platform designed to answer operational questions by combining structured enterprise data, internal knowledge, and AI-assisted reasoning.

The initial use case is:

> Investigate why purchase orders from a supplier are being delayed.

The architecture deliberately separates deterministic enterprise data access from probabilistic AI reasoning.

The system is being built incrementally. This document describes the architecture that has actually been implemented or deliberately designed for the current MVP and will evolve as new capabilities are introduced.

---

## Architectural Principles

### Deterministic data before probabilistic reasoning

Structured enterprise facts should be retrieved deterministically whenever possible.

Information such as supplier identity, purchase-order status, delivery dates, and service tickets belongs to systems of record and should not require an LLM to retrieve or reconstruct it.

LLMs are reserved for capabilities where they add value, such as natural-language understanding, reasoning across heterogeneous evidence, synthesis of structured and unstructured information, and generation of evidence-grounded explanations.

### Evidence-grounded answers

AI-generated conclusions should be traceable to retrieved evidence.

The architecture will preserve the distinction between source data, retrieved evidence, and model-generated synthesis so that answers can expose their supporting sources.

### Controlled AI capabilities

Future AI components will not receive unrestricted access to enterprise systems.

Enterprise operations will be exposed through explicit, controlled tools with narrow responsibilities.

This makes AI behavior easier to test, observe, constrain, and reason about.

### Evaluation and observability are first-class concerns

Evaluation, tracing, monitoring, and failure behavior are part of the MVP architecture rather than post-production additions.

The system should provide evidence not only that it works, but also how well it works and how it behaves when dependencies fail.

### Complexity must be justified

The MVP favors the simplest architecture capable of demonstrating the required production-oriented AI engineering concepts.

Additional services, infrastructure, abstractions, or agent autonomy should only be introduced when they solve a concrete problem.

---

## Current Architecture

The current implementation contains four foundations that are not yet connected through application routes:

1. the FastAPI application foundation,
2. deterministic enterprise data access,
3. document ingestion and semantic retrieval over enterprise knowledge,
4. retrieval evaluation over a deterministic golden dataset.

```text
┌──────────────────────────────┐
│       FastAPI Backend        │
│          /health             │
└──────────────────────────────┘


┌──────────────────────────────┐
│   Deterministic Repositories │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│         SQLAlchemy           │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│ PostgreSQL + pgvector        │
└──────────────────────────────┘
               ▲
               │
┌──────────────┴───────────────┐
│ Semantic Document Retrieval  │
└──────────────▲───────────────┘
               │
┌──────────────┴───────────────┐
│ Chunking + OpenAI Embeddings │
└──────────────▲───────────────┘
               │
┌──────────────┴───────────────┐
│ Enterprise Markdown Corpus   │
└──────────────────────────────┘
```

The FastAPI application currently exposes only the health endpoint.

The deterministic repository layer is implemented and tested directly against PostgreSQL, but it is not yet exposed through API routes.

The document retrieval foundation is also implemented independently of the API. Enterprise documents can be chunked, embedded, persisted in pgvector, and retrieved through exact cosine similarity search.

Future AI capabilities will connect these foundations through controlled tools and orchestration.

---

## Structured Enterprise Data

PostgreSQL acts as the system of record for the structured enterprise scenario used by the MVP.

The initial domain includes suppliers, purchase orders, purchase-order lines, and service tickets.

These records provide deterministic facts and operational evidence that future AI workflows can consume.

The database schema is managed through Alembic migrations.

A deterministic synthetic dataset provides a reproducible investigation scenario that can later serve as ground truth for evaluation.

---

## Data Access Layer

Database access is encapsulated through focused repositories.

The current repositories provide deterministic operations for supplier lookup, delayed purchase-order retrieval, supplier-related service-ticket retrieval, and semantic document-chunk retrieval.

Repositories receive their SQLAlchemy session externally and do not own transaction boundaries.

This keeps persistence concerns separate from future AI tools and allows deterministic data access to be independently tested and reused.

The intended boundary is:

```text
AI workflow
    ↓
controlled tool
    ↓
repository
    ↓
SQLAlchemy
    ↓
PostgreSQL
```

AI components should therefore operate through explicit capabilities rather than directly constructing database queries.

---

## Persistence

The MVP uses PostgreSQL for structured enterprise data and vector persistence.

The PostgreSQL environment includes pgvector, allowing relational enterprise data and document embeddings to coexist without introducing a separate vector database.

Document chunks store 1536-dimensional embeddings together with their textual content and document relationship. A surrogate identifier provides stable technical identity, while document ID and chunk index are constrained to be unique together.

Schema evolution is managed through Alembic rather than application-startup table creation.

---

## Testing Strategy

The project distinguishes between testing persistence behavior and testing higher-level application or AI behavior.

Repository integration tests execute against a dedicated PostgreSQL test database.

Each test runs inside an isolated transaction that is rolled back afterwards.

This verifies real database behavior while keeping tests repeatable and independent.

The document ingestion service is tested against real PostgreSQL while chunking and external embedding generation are replaced with controlled test doubles. This isolates ingestion orchestration while still verifying persistence behavior.

The semantic retrieval repository is tested against real PostgreSQL and pgvector using controlled vectors, verifying cosine-distance ordering without depending on an external embedding provider.

End-to-end diagnostic retrieval has also been exercised using real enterprise documents and real OpenAI embeddings.

Retrieval evaluation uses a deterministic golden dataset containing answerable, partially answerable, and unanswerable cases. Deterministic metrics measure source retrieval and ranking, while semantic evidence coverage is evaluated separately using a constrained LLM judge with structured output.

The evaluator validates deterministic invariants around the LLM judge rather than treating schema compliance as proof of semantic correctness. Returned criteria must exactly match the requested evidence criteria before evidence coverage is calculated.

The current quality pipeline includes Ruff formatting, Ruff linting, strict mypy, and pytest. The same pipeline runs in GitHub Actions against a clean PostgreSQL + pgvector service, where the integration-test database is created and the complete Alembic migration history is applied before the test suite executes.

---

## Target MVP Architecture

The architecture will evolve toward the following system:

```text
                         ┌────────────────────┐
                         │       User         │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │      FastAPI       │
                         └─────────┬──────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │      AI Orchestration      │
                    │         LangGraph          │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │ Structured Tools │        │  Document RAG    │
          └────────┬─────────┘        └────────┬─────────┘
                   │                           │
                   ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │   Repositories   │        │ Vector Retrieval │
          └────────┬─────────┘        └────────┬─────────┘
                   │                           │
                   └─────────────┬─────────────┘
                                 ▼
                     ┌──────────────────────┐
                     │PostgreSQL + pgvector │
                     └──────────────────────┘
                                 │
                                 ▼
                     ┌──────────────────────┐
                     │    LLM Synthesis     │
                     │  answer + evidence   │
                     └──────────────────────┘

        ┌─────────────────────────────────────────────────┐
        │ Evaluation & Observability — cross-cutting      │
        │ across retrieval, tools, orchestration and LLM  │
        └─────────────────────────────────────────────────┘
```

Evaluation and observability are cross-cutting concerns over the AI execution path rather than a final processing step.

The exact implementation of the AI portion will be refined through experimentation rather than assumed in advance.

---

## RAG Retrieval Layer

The first RAG retrieval baseline is implemented over a small corpus of internal enterprise documents.

The ingestion path is:

```text
Enterprise Markdown document
    ↓
recursive chunking
    ↓
OpenAI embedding
    ↓
Document + DocumentChunk
    ↓
PostgreSQL + pgvector
```

The retrieval path is:

```text
Question
    ↓
OpenAI embedding
    ↓
exact cosine similarity search
    ↓
top-k document chunks
    ↓
content + source metadata + distance
```

### Baseline configuration

The initial retrieval baseline uses:

- `RecursiveCharacterTextSplitter`
- chunk size: 500 characters
- chunk overlap: 50 characters
- embedding model: `text-embedding-3-small`
- embedding dimensions: 1536
- vector store: PostgreSQL + pgvector
- similarity metric: cosine distance
- retrieval strategy: exact vector search
- `top_k`: 3

These values are baseline parameters for evaluation rather than assumed optimal configuration.

### Retrieval strategy

The MVP intentionally starts with exact vector similarity search rather than an approximate nearest-neighbor (ANN) index.

At the current corpus size, an ANN index such as HNSW or IVFFlat would add indexing and tuning complexity without solving a measured performance problem. Exact search also provides a clean retrieval baseline, allowing retrieval quality to be evaluated without introducing ANN approximation as an additional variable.

Initial end-to-end diagnostic queries showed relevant retrieval for supplier delivery delays, quality inspection holds, and component shortages.

They also exposed an important limitation: vector search will still return the nearest chunks for an out-of-domain question even when none of those chunks is actually relevant. For this reason, nearest-neighbor retrieval must not be interpreted as proof of sufficient evidence.

Relevance thresholds are not being chosen from a few manually inspected examples. The evaluation phase will use representative queries and a golden dataset to determine how retrieval behavior should distinguish relevant evidence from insufficient information.

The retrieval architecture is designed to evolve based on measured quality and scale rather than adding retrieval techniques by default.

Potential future improvements include:

- HNSW or IVFFlat indexing when corpus size or query volume makes exact search too expensive.
- Hybrid retrieval combining semantic vector search with lexical search for identifiers, product codes, purchase-order numbers, and enterprise terminology.
- Reranking retrieved candidates to improve the ordering and relevance of the final context.
- Query rewriting or multi-query retrieval when evaluation shows that user phrasing reduces recall.
- Metadata filtering to constrain retrieval by document type, supplier, business domain, or other enterprise attributes.

These techniques will be introduced incrementally only when evaluation or scale provides a concrete reason for them.

### Document ingestion boundaries

The current corpus is intentionally local and Markdown-based so that ingestion remains reproducible while retrieval behavior is being developed and evaluated.

Document source discovery is kept separate from the ingestion pipeline. The ingestion service receives textual content and is responsible for chunking, embedding, and persistence, while the current executable adapter loads documents from the local `data/documents` directory.

The current MVP ingestion process is not yet idempotent or version-aware. Re-running ingestion can create duplicate documents and embeddings. A production-oriented evolution would introduce stable document identity, content hashes or versions, and explicit behavior for new, unchanged, and modified documents.

Future source adapters may load content from systems such as S3, SharePoint, upload APIs, or other enterprise repositories. A parsing layer can also be introduced for formats such as PDF, DOCX, and HTML without changing the core ingestion pipeline.

---

## Planned Tool and Orchestration Layer

Structured enterprise capabilities will be exposed as a small allow-list of read-only tools.

The MVP is expected to include capabilities equivalent to supplier lookup, purchase-order search, service-ticket search, and document search.

LangGraph will coordinate these capabilities.

The initial workflow will favor deterministic orchestration because the primary investigation path is known in advance.

Limited dynamic routing may be introduced later if it demonstrates a concrete benefit.

The system will not introduce unrestricted agent autonomy merely to make the architecture more agentic.

---

## Evaluation Layer

Retrieval evaluation is implemented as an independent layer so that retrieval failures can be measured separately from future generation failures.

The current golden dataset contains 15 representative cases covering answerable, partially answerable, and unanswerable questions, including multi-source and multi-evidence challenge scenarios. Ground truth is expressed through expected sources and semantic evidence criteria rather than chunk identifiers, keeping the evaluation dataset independent of a specific chunking configuration.

The current retrieval baseline measures:

- source hit@k
- source coverage@k
- first relevant source rank
- mean reciprocal rank (MRR)
- semantic evidence coverage
- retrieval latency

Source-based metrics are deterministic. Semantic evidence coverage uses a constrained LLM judge because exact lexical matching would be too brittle for determining whether retrieved context supports a semantic evidence criterion.

The LLM judge returns structured results, but schema compliance is not treated as sufficient validation. Deterministic invariants require the judge to return exactly the requested criteria, in the expected order, before evidence coverage is calculated. Evaluation failures therefore fail explicitly rather than being silently converted into quality scores.

The strengthened 15-case evaluation produced identical deterministic retrieval quality for the two tested configurations:

- 100% source hit for both `top_k=3` and `top_k=5` across 13 source-evaluable cases
- 100% mean source coverage for both configurations
- MRR of 0.949 for both configurations

Semantic evidence coverage was evaluated over five runs per configuration because repeated runs exposed material variance in the LLM-based judge. Mean evidence coverage was 94.6% for `top_k=3` and 96.1% for `top_k=5`. The observed ranges were 91.7–96.2% and 90.4–98.1%, respectively.

Retrieval latency covers query embedding and vector retrieval. The offline LLM judge is intentionally excluded from that measurement because it is evaluation infrastructure rather than part of the runtime retrieval path.

These measurements establish a controlled baseline for comparison rather than a claim of production-level retrieval quality. Individual retrieval results remain inspectable so that changes in metrics can be attributed to retrieval behavior, evaluator behavior, or evaluation-dataset assumptions.

The `top_k` experiment retained `top_k=3` as the MVP default. Although `top_k=5` produced a small increase in mean semantic evidence coverage, deterministic source retrieval did not improve and the additional chunks introduced less relevant context in some cases. Given the observed judge variance, the difference was not treated as sufficient evidence to increase the default context size.

The experiment also demonstrated that an LLM-based evaluator is itself a probabilistic system. Identical retrieved context produced different evidence-support judgments across runs. For production use, the judge should be calibrated against human-labelled examples and its model, prompt, and evaluation configuration should be versioned before small metric differences are used to drive retrieval decisions.

Partially answerable cases deliberately preserve the distinction between retrieval evidence coverage and overall answerability. Retrieving all available evidence does not imply that sufficient evidence exists to fully answer the user's question.

Unanswerable cases with no expected evidence are excluded from evidence-coverage aggregation. Vector retrieval may still return nearest-neighbor chunks for these questions, reinforcing the distinction between retrieving candidates and establishing sufficient evidence.

The first controlled retrieval experiment has compared `top_k=3` with `top_k=5`. Further retrieval changes will be introduced only when evaluation identifies a concrete failure mode or measurable need. Generation-specific evaluation will be introduced when evidence-grounded LLM synthesis is implemented.

---

## Planned Observability and Reliability

AI execution will expose operational information such as request and run identifiers, tool execution, retrieval behavior, model calls, latency, token usage, estimated cost where practical, retries, errors, and total execution time.

The MVP will also exercise controlled failure scenarios.

A dependency failure should not cause the model to fabricate unavailable enterprise information.

The system should instead degrade explicitly and communicate incomplete evidence.

---

## Scope Boundaries

The current MVP intentionally excludes infrastructure and features that do not materially contribute to demonstrating the target AI engineering capabilities.

Examples currently outside the MVP include sophisticated frontend development, full authentication and authorization, multitenancy, unrestricted database access from the LLM, production-scale microservice decomposition, Kafka, Kubernetes, multiple vector databases, multiple AI frameworks, complex infrastructure as code, and full human-in-the-loop workflows.

These capabilities may be appropriate in a production system, but introducing them now would reduce the time available for RAG evaluation, orchestration, observability, and reliability engineering.

---

## Architecture Evolution

This document will evolve with the implementation.

Sections describing planned components should be replaced with concrete architecture and measured decisions as those components are built.

Significant decisions involving meaningful alternatives and trade-offs may later be captured as individual Architecture Decision Records (ADRs).
