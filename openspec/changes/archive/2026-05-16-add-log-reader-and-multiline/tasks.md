## 1. Reader Fixtures And Models

- [x] 1.1 Add small reader fixtures
  - Files: `tests/fixtures/reader-sample.log`, `tests/fixtures/reader-invalid-utf8.log`, `tests/fixtures/reader-sample.log.gz`
  - Behavior: provide small text, invalid-byte, and gzip inputs for deterministic tests
  - Tests: fixtures are consumed by reader tests
  - Verification: `uv run pytest tests/test_reader.py`

- [x] 1.2 Define streaming line record model
  - Files: `diagnose_tool/analyzer/reader.py`, `tests/test_reader.py`
  - Behavior: represent each physical line with `file_path`, `line_no`, and `raw`
  - Tests: text reader assertions verify record fields
  - Verification: `uv run pytest tests/test_reader.py`

## 2. Streaming Readers

- [x] 2.1 Implement normal text log streaming reader
  - Files: `diagnose_tool/analyzer/reader.py`, `tests/test_reader.py`
  - Behavior: stream normal text files line by line using iteration, preserve raw text, and avoid full-file reads
  - Tests: multiple lines, empty file, line numbers, raw text preservation
  - Verification: `uv run pytest tests/test_reader.py`

- [x] 2.2 Implement gzip log streaming reader
  - Files: `diagnose_tool/analyzer/reader.py`, `tests/test_reader.py`
  - Behavior: stream `.gz` files line by line without decompressing full contents to memory or disk
  - Tests: gzip fixture yields expected line records
  - Verification: `uv run pytest tests/test_reader.py`

- [x] 2.3 Implement encoding-safe reading
  - Files: `diagnose_tool/analyzer/reader.py`, `tests/test_reader.py`
  - Behavior: use replacement error handling for undecodable bytes and continue reading subsequent lines
  - Tests: invalid UTF-8 fixture yields replacement character and later lines
  - Verification: `uv run pytest tests/test_reader.py`

## 3. Multiline Merger

- [x] 3.1 Define multiline event candidate model
  - Files: `diagnose_tool/analyzer/multiline.py`, `tests/test_multiline.py`
  - Behavior: represent merged event candidates with source file, start line, end line, and raw text
  - Tests: model fields verified through merge tests
  - Verification: `uv run pytest tests/test_multiline.py`

- [x] 3.2 Implement Java stack trace and continuation merging
  - Files: `diagnose_tool/analyzer/multiline.py`, `tests/test_multiline.py`
  - Behavior: append exception lines, stack frames, `Caused by:`, `Suppressed:`, and continuation lines to the previous event
  - Tests: Java stack trace fixture merges into one event and preserves raw content
  - Verification: `uv run pytest tests/test_multiline.py`

- [x] 3.3 Preserve malformed leading lines
  - Files: `diagnose_tool/analyzer/multiline.py`, `tests/test_multiline.py`
  - Behavior: emit leading malformed or continuation-like lines as raw event candidates instead of discarding them
  - Tests: input beginning with malformed line produces preserved event
  - Verification: `uv run pytest tests/test_multiline.py`

- [x] 3.4 Ensure merger remains streaming-safe
  - Files: `diagnose_tool/analyzer/multiline.py`, `tests/test_multiline.py`
  - Behavior: buffer only the current event candidate and yield completed events while iterating
  - Tests: multiple events are emitted in order without requiring full input materialization
  - Verification: `uv run pytest tests/test_multiline.py`

## 4. Verification And Documentation

- [x] 4.1 Run focused and full verification
  - Files: test suite
  - Behavior: verify reader and multiline behavior without full-file reads or out-of-scope parsing/classification
  - Tests: `uv run pytest tests/test_reader.py tests/test_multiline.py`, then `uv run pytest`
  - Verification: `uv run pytest` and `uv run ruff check .`

- [x] 4.2 Update project current state
  - Files: `docs/00-project/current-state.md`
  - Behavior: mark streaming log reader and multiline stack trace merger as implemented; keep header parser, classifier, evidence generation, casebase, retrieval, and deployment incomplete
  - Tests: documentation review
  - Verification: confirm current-state reflects only this completed capability
