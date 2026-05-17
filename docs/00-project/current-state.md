# Current State

This file is the **project continuity snapshot**. Update it after every completed change.

## Current Phase

React frontend shell implemented. Full UI business features remain.

## Implemented

- [x] Project concept defined
- [x] Harness document hierarchy defined
- [x] OpenSpec configuration draft prepared
- [x] Python package structure created
- [x] FastAPI app created
- [x] Config loading implemented
- [x] Directory whitelist validation implemented
- [x] Server directory scan API implemented
- [x] Streaming log reader implemented
- [x] Multiline stack trace merger implemented
- [x] Complex log header parser implemented
- [x] Rule classifier implemented
- [x] Evidence package generator implemented
- [x] Key logs generator implemented
- [x] Raw samples JSONL generator implemented
- [x] Timeline aggregation implemented
- [x] HTML report generator implemented
- [x] Case draft generator implemented
- [x] Case metadata draft generator implemented
- [x] Retrieval query generator implemented
- [x] Case base file storage implemented
- [x] Case index rebuild implemented
- [x] Manual case creation API implemented
- [x] Keyword retrieval implemented
- [x] Rule-based retrieval implemented
- [x] BM25 retrieval implemented (optional, requires rank-bm25)
- [x] Prompt context generator implemented
- [x] Docker Compose deployment implemented
- [x] React frontend shell implemented

## Current Constraints

- No mandatory external database.
- File-based task state.
- Markdown/YAML casebase.
- Embedding disabled by default.
- Vector retrieval optional only.

## Current Directory Plan

```text
DiagnoseToolPy/
├── AGENTS.md
├── openspec/config.yaml
├── docs/
├── config/
├── diagnose_tool/        # FastAPI backend
├── frontend/             # React + Vite + TypeScript frontend
├── data/
└── tests/
```

## Known Gaps

- Full retrieval API endpoint not yet wired to UI.
- Complete log analysis UI not implemented.
- Complete case management UI not implemented.

## Next Recommended Work

1. Wire retrieval to API endpoint.
2. Implement complete log analysis UI.
3. Implement complete case management UI.
