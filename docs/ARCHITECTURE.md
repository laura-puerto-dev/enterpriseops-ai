# EnterpriseOps AI — Architecture

| | |
|---|---|
| **Status** | In progress |
| **Last updated** | 2026-09-17 |
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

Day 1 establishes two foundations that are not yet connected through application routes.

```text
┌──────────────────────────────┐
│       FastAPI Backend        │
│          /health             │
└──────────────────────────────┘


┌──────────────────────────────┐
│        Repositories          │
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
```

The FastAPI application currently exposes only the health endpoint.

The deterministic repository layer is implemented and tested directly against PostgreSQL, but it is not yet exposed through API routes.

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

The current repositories provide deterministic operations for supplier lookup, delayed purchase-order retrieval, and supplier-related service-ticket retrieval.

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

The MVP uses PostgreSQL for structured enterprise data.

The PostgreSQL environment includes pgvector so that vector retrieval can be introduced without adding a separate vector database during the initial RAG implementation.

This keeps the infrastructure small while allowing relational and vector retrieval to coexist.

Schema evolution is managed through Alembic rather than application-startup table creation.

---

## Testing Strategy

The project distinguishes between testing persistence behavior and testing higher-level application or AI behavior.

Repository integration tests execute against a dedicated PostgreSQL test database.

Each test runs inside an isolated transaction that is rolled back afterwards.

This verifies real database behavior while keeping tests repeatable and independent.

As higher layers are introduced, tests may use controlled substitutes for lower-level dependencies when the behavior of those dependencies is not the subject of the test.

The current quality pipeline includes Ruff formatting, Ruff linting, strict mypy, and pytest.

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

## Planned RAG Layer

The next architectural increment introduces retrieval over internal enterprise documents.

The baseline flow will be:

```text
Document
   ↓
chunking
   ↓
embedding
   ↓
pgvector

Question
   ↓
embedding
   ↓
vector retrieval
   ↓
relevant document chunks
   ↓
LLM context
```

Chunking strategy, embedding configuration, retrieval parameters, and evaluation criteria will be documented after they have been implemented and tested.

---

## Planned Tool and Orchestration Layer

Structured enterprise capabilities will be exposed as a small allow-list of read-only tools.

The MVP is expected to include capabilities equivalent to supplier lookup, purchase-order search, service-ticket search, and document search.

LangGraph will coordinate these capabilities.

The initial workflow will favor deterministic orchestration because the primary investigation path is known in advance.

Limited dynamic routing may be introduced later if it demonstrates a concrete benefit.

The system will not introduce unrestricted agent autonomy merely to make the architecture more agentic.

---

## Planned Evaluation Layer

The RAG and AI pipeline will be evaluated against a small deterministic golden dataset.

Evaluation will cover both retrieval and generation behavior.

Experiments will compare concrete retrieval configurations rather than relying only on subjective inspection.

The selected configuration should therefore be supported by measured evidence.

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
