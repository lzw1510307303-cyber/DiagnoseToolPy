# Testing Guide

## Test Framework

Use pytest.

## Required Tests

### core

- config loading
- path whitelist validation
- path traversal rejection
- safe file write behavior

### analyzer

- directory scanning
- streaming reader
- gzip reader
- multiline stack trace merge
- complex header parser
- rule classifier
- bounded sample collection

### casebase

- manual case writing
- case from task
- metadata.yaml generation
- index.yaml rebuild
- invalid metadata handling

### retrieval

- query builder
- keyword search
- rule match
- BM25 search if enabled
- embedding disabled behavior

## Fixtures

Store small fixtures under:

```text
tests/fixtures/
```

Do not commit large logs.

Generate temporary large files in tests if needed.

## Commands

```bash
uv run pytest
uv run pytest --cov=diagnose_tool
```
