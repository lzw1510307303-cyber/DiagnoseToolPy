## Why

DiagnoseToolPy can now start as a runnable FastAPI skeleton, but users still cannot select or inspect server-side log directories. This change adds the next MVP capability: securely checking and scanning an allowed server directory without reading log contents.

## What Changes

- Add a source directory check API that validates a requested path against configured whitelist roots.
- Add a source directory scan API that validates the path and recursively scans files under the selected directory.
- Reuse existing path whitelist validation from `diagnose_tool/core/security.py`.
- Add analyzer-side directory scanning in `diagnose_tool/analyzer/scanner.py`, independent from FastAPI.
- Detect supported log files by extension: `.log`, `.txt`, `.out`, `.err`, `.gz`.
- Return total file count, supported file count, unsupported file count, total bytes, and per-file path, name, size, and type.
- Add tests for scanner behavior, supported/unsupported file detection, recursive scanning, and invalid path rejection through the API.
- Update `docs/00-project/current-state.md` after implementation.

## Capabilities

### New Capabilities
- `server-directory-scan`: Defines secure server-side directory checking and metadata-only recursive log file scanning.

### Modified Capabilities

None.

## Impact

- Affected modules: `api`, `analyzer`, `core`, `docs`, `tests`.
- Adds request/response models only as needed for source directory check and scan behavior.
- Adds metadata-only filesystem traversal; it must not read file contents or parse log lines.
- Does not create analysis task output files such as `task.yaml`, `progress.json`, `evidence-pack.md`, or case artifacts.
- Does not introduce a database, retrieval, casebase, AI integration, browser large-file upload, or deployment changes.
