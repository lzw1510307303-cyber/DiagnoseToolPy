# Dependency Policy

## Principles

- Keep dependencies minimal.
- Avoid services that require extra installation.
- Prefer pure Python or embedded libraries.
- Optional features must be disabled by default.

## Base Dependencies

- fastapi
- uvicorn
- pydantic
- pydantic-settings
- pyyaml
- jinja2
- python-multipart

## Optional Retrieval Dependency

- rank-bm25

## Optional Vector Dependency

- lancedb
- faiss, if explicitly selected later

## Forbidden as Mandatory Dependencies

- MySQL
- PostgreSQL
- Elasticsearch
- ClickHouse
- Redis
- Celery
- Qdrant server
- mandatory embedding model

## Rule

If a dependency introduces service deployment requirements, propose it as optional only.
