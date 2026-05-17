## Context

DiagnoseToolPy has an initial FastAPI app, YAML config loading, and server path whitelist validation. The next MVP step is allowing users to check and scan a server-side directory so later analyzer work can process selected log files without browser upload.

This change must keep API routes thin, place filesystem traversal in the analyzer module, enforce whitelist validation before scanning, and return metadata only. It must not read log file contents, parse logs, create analysis tasks, write durable scan outputs, or add any database.

## Goals / Non-Goals

**Goals:**

- Add API support for checking whether a source directory is valid and allowed.
- Add API support for recursively scanning an allowed source directory.
- Reuse `diagnose_tool/core/security.py` for whitelist enforcement.
- Add `diagnose_tool/analyzer/scanner.py` for metadata-only recursive directory scanning.
- Support `.log`, `.txt`, `.out`, `.err`, and `.gz` extensions.
- Return scan summary counts and per-file metadata.
- Add tests for scanner behavior and API invalid path rejection.
- Update `docs/00-project/current-state.md` after implementation.

**Non-Goals:**

- Do not read log file contents.
- Do not parse log lines or merge stack traces.
- Do not create `task.yaml`, `progress.json`, `evidence-pack.md`, case drafts, or retrieval queries.
- Do not implement casebase, retrieval, AI provider calls, Docker, or browser large-file upload.
- Do not add a mandatory database or external infrastructure service.

## Decisions

### Analyzer-Owned Scanning

Directory traversal and file type detection will live in `diagnose_tool/analyzer/scanner.py`. The API layer will validate requests, call core validation, call the scanner, and format responses.

Alternative considered: put scanning directly in the FastAPI route. This was rejected because API routes must remain thin and large-file-related logic belongs outside `api`.

### Metadata-Only Scan

The scanner will use directory iteration APIs such as `Path.rglob("*")` and file metadata such as `stat().st_size`. It will not open or read file contents. Results will include each file path, name, size, and file type, plus aggregate counts and byte totals.

Alternative considered: sample file headers during scan. This was rejected because content reading belongs to later streaming analyzer work.

### Extension-Based File Type Detection

Supported log files are identified by case-insensitive suffix matching for `.log`, `.txt`, `.out`, `.err`, and `.gz`. The returned file type can be derived from the suffix without inspecting contents.

Alternative considered: MIME detection or magic bytes. This was rejected because it would require content reads and add unnecessary complexity.

### Whitelist Enforcement Before Traversal

The source check and scan APIs will validate the requested path against configured allowed input roots before scanning. Invalid, missing, non-directory, traversal, and outside-root paths should return safe API errors.

Alternative considered: allow scanner to reject invalid paths only after traversal begins. This was rejected because security validation should happen before filesystem traversal.

### No Durable Scan Output Yet

The scan response is returned directly to the caller. This change does not create analysis task state or durable output files.

Alternative considered: persist scan results under `data/runtime/`. This was rejected to keep the change focused and avoid creating task-state contracts before the task workflow exists.

## Data Flow

1. Client sends a source directory path to the check or scan endpoint.
2. API loads app config to get allowed input roots.
3. API calls whitelist validation with the requested path.
4. Check endpoint returns whether the path is accepted and safe metadata.
5. Scan endpoint calls analyzer scanner only after validation succeeds.
6. Scanner recursively walks files and builds bounded metadata objects without opening file contents.
7. API returns summary counts, total bytes, and per-file metadata.

## Module Responsibilities

- `diagnose_tool/api/routes_source.py`: request validation, safe error responses, and calls to core/analyzer services.
- `diagnose_tool/analyzer/scanner.py`: recursive directory traversal, supported extension detection, and scan summary construction.
- `diagnose_tool/core/security.py`: existing path whitelist validation reused by APIs.
- `diagnose_tool/core/config.py`: existing config loading for allowed roots.
- `diagnose_tool/core/models.py`: optional shared request/response models if useful for keeping schemas explicit.
- `diagnose_tool/main.py`: route registration for source APIs.
- `tests/test_scanner.py`: scanner unit tests.
- `tests/test_source_api.py`: API success and invalid path tests.

## File Outputs

This change does not write durable application output files. It reads filesystem metadata and returns an HTTP response.

No changes are made to `task.yaml`, `progress.json`, `case.md`, `metadata.yaml`, `index.yaml`, `evidence-pack.md`, or `retrieval-query.json` contracts.

## Error Handling

- Missing `path` input should return a safe client error.
- Paths outside configured whitelist roots should return a safe client error.
- Non-existent paths and non-directory paths should return a safe client error.
- Individual files that cannot be statted during traversal should not crash the full scan; the scanner should either skip them or report safe unsupported/error metadata in a deterministic way.
- API responses must not expose stack traces or unsafe internal exception details.

## Security Considerations

- Validate paths with the existing resolved-path whitelist logic before scanning.
- Do not trust browser-provided paths.
- Do not support arbitrary root browsing.
- Do not follow a string-prefix whitelist strategy.
- Keep returned paths scoped to validated scan results; if absolute paths are returned, they must only be from allowed roots.

## Memory Behavior

The scanner must not read log contents into memory. It only stores metadata for discovered files in the response. This is acceptable for the initial scan capability; later large-directory pagination or result persistence can be added if needed.

## Tests

- Scanner recursively finds files in nested directories.
- Scanner classifies supported extensions `.log`, `.txt`, `.out`, `.err`, and `.gz` case-insensitively.
- Scanner counts unsupported files separately.
- Scanner reports total bytes from file metadata.
- Source check API accepts allowed directories and rejects invalid paths.
- Source scan API rejects paths outside whitelist roots.
- API tests verify safe error status and response body for invalid paths.

## Compatibility

This builds on the existing skeleton and path whitelist modules. It does not alter persisted storage contracts. Future agents can continue by adding analysis task creation after a successful scan.

## Risks / Trade-offs

- [Risk] Large directories can produce large JSON responses. -> Mitigation: keep this as MVP metadata scanning and leave pagination/limits for a later focused change if needed.
- [Risk] Path validation could be bypassed if routes call the scanner directly. -> Mitigation: route tests must cover invalid path rejection and implementation should centralize validation before scanning.
- [Risk] Symlink traversal may expose unexpected filesystem locations. -> Mitigation: resolved path validation applies to the requested root; implementation should avoid following directory symlinks or validate resolved file paths if symlink traversal is supported.

## Migration Plan

No data migration is required. Rollback is removing the new source API route, scanner module, tests, and current-state update.

## Open Questions

None.
