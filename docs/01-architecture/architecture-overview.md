# Architecture Overview

## Layers

```text
Web UI
  ↓
FastAPI API
  ↓
Service Modules
  ↓
File-based Storage
```

## Major Components

### API Layer

Exposes endpoints for:

- source directory check/scan
- task creation/status
- report access
- case management
- retrieval search
- exports

### Analyzer Layer

Handles log analysis.

It must be independent from FastAPI so it can be unit tested.

### Casebase Layer

Handles durable knowledge assets.

It writes and reads:

- `case.md`
- `metadata.yaml`
- `index.yaml`

### Retrieval Layer

Handles similar case search.

Default retrieval does not require embeddings.

### Exporter Layer

Exports:

- single case zip
- RAG dataset JSONL
- bugfix prompt
- Markdown reports

## Cross-cutting Concerns

- Path security
- Streaming file processing
- Atomic file writes where practical
- Testable pure functions
- File-based contracts
