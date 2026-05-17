# ADR-0002: No Mandatory Database

## Status

Accepted

## Context

A mandatory database would complicate internal deployment.

Traditional databases also provide limited direct value for RAG retrieval compared with normalized documents and rebuildable indexes.

## Decision

Do not introduce mandatory databases in the MVP.

Forbidden unless explicitly approved:

- MySQL
- PostgreSQL
- Elasticsearch
- ClickHouse
- Redis
- MongoDB
- mandatory SQLite

## Allowed

- YAML files
- Markdown files
- JSON/JSONL files
- rank-bm25 corpus files
- optional LanceDB/FAISS local indexes as rebuildable caches

## Consequences

The system remains portable and simple to deploy.

Complex multi-user features are deferred.
