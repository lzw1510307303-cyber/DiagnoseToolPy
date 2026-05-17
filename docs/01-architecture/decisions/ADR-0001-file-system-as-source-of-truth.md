# ADR-0001: File System as Source of Truth

## Status

Accepted

## Context

DiagnoseToolPy must be easy to deploy in internal Linux environments.

Installing and operating databases increases deployment cost and reduces portability.

The project also needs to export normalized documents for RAG and internal learning.

## Decision

Use the file system as the source of truth.

Durable knowledge must be stored as:

- Markdown
- YAML
- JSONL
- HTML reports
- plain text artifacts

## Consequences

Benefits:

- Easy deployment
- Easy backup and migration
- Git-friendly
- Human-readable
- RAG-friendly
- No database operations

Trade-offs:

- Less suitable for high-concurrency editing
- Requires careful file locking and atomic writes for future multi-user scenarios
- Indexes must be explicitly rebuildable
