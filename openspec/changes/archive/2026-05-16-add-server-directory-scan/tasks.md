## 1. Scanner Core

- [x] 1.1 Define scan result models or dataclasses
  - Files: `diagnose_tool/analyzer/scanner.py`, optional `diagnose_tool/core/models.py`
  - Behavior: represent scan summary and per-file metadata with fields for counts, bytes, path, name, size, and type
  - Tests: covered by scanner tests that assert result shape
  - Verification: `uv run pytest tests/test_scanner.py`

- [x] 1.2 Implement supported file type detection
  - Files: `diagnose_tool/analyzer/scanner.py`, `tests/test_scanner.py`
  - Behavior: classify `.log`, `.txt`, `.out`, `.err`, and `.gz` as supported using case-insensitive suffix matching
  - Tests: supported extensions, unsupported extension, uppercase suffix
  - Verification: `uv run pytest tests/test_scanner.py`

- [x] 1.3 Implement metadata-only recursive directory scan
  - Files: `diagnose_tool/analyzer/scanner.py`, `tests/test_scanner.py`
  - Behavior: recursively scan files under a validated directory, collect file metadata, count supported and unsupported files, sum total bytes, and avoid reading file contents
  - Tests: nested files discovered, counts and total bytes correct, unsupported files counted separately
  - Verification: `uv run pytest tests/test_scanner.py`

## 2. Source APIs

- [x] 2.1 Implement source directory check route
  - Files: `diagnose_tool/api/routes_source.py`, `diagnose_tool/main.py`, `tests/test_source_api.py`
  - Behavior: validate requested path against configured allowed input roots and return whether it is accepted
  - Tests: allowed directory check succeeds, missing path rejected, outside path rejected
  - Verification: `uv run pytest tests/test_source_api.py`

- [x] 2.2 Implement source directory scan route
  - Files: `diagnose_tool/api/routes_source.py`, `diagnose_tool/main.py`, `tests/test_source_api.py`
  - Behavior: validate requested path before scanning and return scan summary and per-file metadata
  - Tests: scan endpoint succeeds for allowed directory, outside path rejected before scan
  - Verification: `uv run pytest tests/test_source_api.py`

- [x] 2.3 Ensure safe API error responses
  - Files: `diagnose_tool/api/routes_source.py`, `tests/test_source_api.py`
  - Behavior: return safe client errors for invalid, missing, non-existent, non-directory, and outside-root paths without stack traces
  - Tests: invalid path response and missing input response
  - Verification: `uv run pytest tests/test_source_api.py`

## 3. Verification And Documentation

- [x] 3.1 Run focused and full verification
  - Files: test suite
  - Behavior: verify scanner and source API behavior without reading log contents or adding durable output files
  - Tests: `uv run pytest tests/test_scanner.py tests/test_source_api.py`, then `uv run pytest`
  - Verification: `uv run pytest` and `uv run ruff check .`

- [x] 3.2 Update project current state
  - Files: `docs/00-project/current-state.md`
  - Behavior: mark server directory scan API as implemented and leave streaming reader, parser, casebase, retrieval, and deployment gaps incomplete
  - Tests: documentation review
  - Verification: confirm current-state reflects only this completed capability
