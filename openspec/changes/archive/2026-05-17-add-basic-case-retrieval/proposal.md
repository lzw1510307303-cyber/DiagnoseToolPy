## Why

DiagnoseToolPy can analyze logs and generate case drafts, but without retrieval, each new incident is diagnosed in isolation. The retrieval system enables finding similar historical cases by matching metadata fields (tags, components, fault_modes, exception_classes, key_phrases) and optionally using BM25 full-text search. This improves AI-assisted diagnosis by providing relevant context without requiring embedding models.

## What Changes

- New `diagnose_tool/retrieval/` module with keyword search, rule matching, BM25 search, and prompt context generation.
- `query_builder.py`: builds retrieval query from retrieval-query.json or analyzer output.
- `keyword_search.py`: matches cases by keyword overlap.
- `rule_matcher.py`: matches cases by tags, components, fault_modes, exception_classes, key_phrases.
- `bm25_search.py`: optional BM25 full-text search (requires rank-bm25).
- `prompt_context.py`: generates similar case prompt context with reference-only markers.
- Tests for retrieval with embedding disabled.

## Capabilities

### New Capabilities
- `basic-case-retrieval`: Keyword and rule-based case retrieval without embedding, with optional BM25 and future vector support.

### Modified Capabilities
- (none)

## Impact

- New module: `diagnose_tool/retrieval/`
- No database introduced
- No AI API calls
- Retrieval works when embedding is disabled
