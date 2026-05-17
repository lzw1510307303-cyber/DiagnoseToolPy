# ADR-0003: Retrieval Without Embedding First

## Status

Accepted

## Context

Some deployment environments may not have embedding models or GPU/CPU resources for semantic retrieval.

Fault diagnosis often relies on precise tokens such as exception classes, error codes, stack symbols, and key log phrases.

## Decision

Retrieval must work without embedding models.

Default retrieval channels:

- keyword matching
- exception class matching
- key phrase matching
- tag matching
- fault mode matching
- BM25 when available

Vector retrieval is optional and disabled by default.

## Consequences

The system is useful in resource-constrained environments.

Embedding can be added later without changing the core architecture.
