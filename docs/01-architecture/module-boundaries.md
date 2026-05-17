# Module Boundaries

## api

FastAPI route layer only.

Allowed:

- Request validation
- Response formatting
- Calling service functions

Forbidden:

- Log parsing logic
- Case writing logic
- Retrieval ranking logic
- Large file processing

## core

Shared infrastructure.

Responsibilities:

- config loading
- path whitelist validation
- shared models
- safe file state utilities
- common path utilities

## analyzer

Responsible for log analysis.

Responsibilities:

- directory scanning
- file filtering
- streaming reads
- gzip reads
- multiline stack trace merge
- complex header parsing
- rule-based classification
- sample extraction
- timeline generation
- evidence package generation
- report generation
- case draft generation

Must not:

- depend on FastAPI
- write final archived cases directly
- perform AI calls

## casebase

Responsible for fault case management.

Responsibilities:

- manual case creation
- case creation from task artifacts
- write `case.md`
- write `metadata.yaml`
- load cases
- update cases
- archive cases
- maintain `data/cases/index.yaml`

## retrieval

Responsible for local retrieval.

Responsibilities:

- build retrieval query from analysis result
- keyword search
- rule matching
- BM25 search
- optional vector search
- hybrid ranking
- prompt context generation

Must work with embedding disabled.

## exporter

Responsible for export formats.

Responsibilities:

- case Markdown export
- RAG JSONL dataset export
- zip export
- bugfix prompt export
