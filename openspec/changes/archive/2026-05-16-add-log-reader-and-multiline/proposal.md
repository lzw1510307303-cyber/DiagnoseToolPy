## Why

DiagnoseToolPy can scan server directories and identify log files, but it cannot yet stream log contents or preserve multiline stack traces as coherent event candidates. This change adds the next analyzer foundation: safe line-by-line reading for text and gzip logs plus Java stack trace multiline grouping.

## What Changes

- Add `diagnose_tool/analyzer/reader.py` for streaming normal text logs line by line.
- Add gzip log streaming support for `.gz` files.
- Handle uncertain encodings safely using replacement behavior rather than failing or discarding logs.
- Add `diagnose_tool/analyzer/multiline.py` for grouping Java stack traces and continuation lines into single log event candidates.
- Preserve raw text and line numbers for every emitted event candidate.
- Add small unit test fixtures under `tests/fixtures/`.
- Add tests for text reading, gzip reading, encoding replacement, multiline stack trace merging, continuation handling, and malformed lines.
- Update `docs/00-project/current-state.md` after implementation.

## Capabilities

### New Capabilities
- `log-reader-and-multiline`: Defines streaming text/gzip log reading and multiline Java stack trace event candidate merging.

### Modified Capabilities

None.

## Impact

- Affected modules: `analyzer`, `docs`, `tests`.
- Adds streaming file-read primitives that future parser/classifier work can consume.
- Adds multiline grouping before complex header parsing, without parsing headers or classifying exceptions.
- Does not create analysis task outputs, evidence packs, casebase records, retrieval indexes, AI integrations, or database dependencies.
