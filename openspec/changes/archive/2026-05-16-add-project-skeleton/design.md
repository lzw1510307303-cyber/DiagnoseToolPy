## Context

DiagnoseToolPy is currently documented but not runnable. The first implementation change needs to establish the Python package layout, a minimal FastAPI app, file-based YAML configuration, and core path validation without introducing log analysis, casebase, retrieval, AI, Docker, or database concerns.

The design must preserve the project constraints: no mandatory database, file system as source of truth, server-side directory access controlled by a whitelist, and small testable modules.

## Goals / Non-Goals

**Goals:**

- Create the planned package and data directory skeleton.
- Provide a runnable FastAPI application in `diagnose_tool/main.py`.
- Provide a health check endpoint that can verify the app starts.
- Provide a simple index page as the initial Web UI entry.
- Load app settings from `config/app.yaml` through `diagnose_tool/core/config.py`.
- Validate selected server directories against configured whitelist roots through `diagnose_tool/core/security.py`.
- Add pytest coverage for config loading and whitelist behavior.
- Update `docs/00-project/current-state.md` after implementation.

**Non-Goals:**

- Do not implement log scanning or log analysis.
- Do not implement analysis task state files.
- Do not implement casebase, retrieval, exporter, or AI provider integration.
- Do not implement browser upload flows.
- Do not implement Docker or production deployment.
- Do not add any mandatory database or external infrastructure service.

## Decisions

### Minimal FastAPI Entry Point

`diagnose_tool/main.py` will initialize a FastAPI app and expose the initial routes directly or through a small route module if the implementation benefits from it. The index route returns simple HTML using Jinja2 templates or a direct HTML response, keeping MVP UI work minimal.

Alternative considered: build a full API/router/template structure immediately. This was rejected because the change should remain focused on the initial runnable skeleton.

### YAML Configuration Loader

`diagnose_tool/core/config.py` will load `config/app.yaml` using `pathlib.Path` and PyYAML. The loader should return an explicit settings object or dictionary with normalized paths. Missing or malformed YAML should fail with a clear exception that tests can assert.

Alternative considered: use environment-only settings or a database-backed settings store. This was rejected because project runtime configuration should begin as simple file-based YAML.

### Directory Whitelist Validation

`diagnose_tool/core/security.py` will validate requested paths by resolving them and checking that they are equal to or contained within one configured allowed root. Traversal attempts and sibling-prefix paths must be rejected by path relationship checks, not string prefix checks.

Alternative considered: accept any existing local path and rely on UI controls. This was rejected because server-side validation is required before directory scanning features are added.

### File System Skeleton

The implementation will create placeholder package directories with `__init__.py` where needed and data directories matching the documented plan. Durable data remains file-based; this change does not create task or case output contracts yet.

Alternative considered: defer empty module directories until feature implementation. This was rejected because the change goal is to create the planned package structure so subsequent changes have stable module boundaries.

## Data Flow

1. App startup imports `diagnose_tool.main:app`.
2. Config-related code loads `config/app.yaml` only when called by the app or tests.
3. The health endpoint returns static app health metadata.
4. The index endpoint returns a minimal landing page.
5. Future directory-selection routes will call whitelist validation before scanning, but this change only implements the core validator and tests.

## Module Responsibilities

- `diagnose_tool/main.py`: FastAPI app construction and initial route registration.
- `diagnose_tool/core/config.py`: YAML loading, defaults, and path normalization.
- `diagnose_tool/core/security.py`: whitelist path validation logic.
- `diagnose_tool/templates/`: initial index template if templates are used.
- `config/app.yaml`: default file-based runtime settings.
- `tests/`: unit tests for config loading and path validation.

## File Outputs

- `config/app.yaml`: durable project configuration file, edited by humans or deployment automation.
- `data/input/`, `data/output/`, `data/cases/`, `data/indexes/`, `data/runtime/`: file-system locations reserved for future features.
- No `task.yaml`, `progress.json`, `case.md`, `metadata.yaml`, `index.yaml`, `evidence-pack.md`, or `retrieval-query.json` files are created by this change.

## Error Handling

- Missing config file should raise a clear file-not-found style error.
- Malformed YAML should raise a clear config loading error without silently falling back to unsafe defaults.
- Invalid whitelist roots should be handled deterministically in tests.
- Requested paths outside allowed roots, traversal attempts, and non-directory paths should be rejected with safe errors or false validation results, depending on the chosen function API.

## Security Considerations

- Use `Path.resolve()` before comparing paths.
- Use `Path.is_relative_to()` or equivalent parent checks rather than string prefix matching.
- Do not expose arbitrary server filesystem access.
- Do not treat browser-provided paths as trusted.

## Memory Behavior

This change does not read log files. Config loading reads only small YAML files. No full-log or unbounded file loading behavior is introduced.

## Tests

- Config loader reads a valid YAML file and exposes expected fields.
- Config loader rejects missing or malformed YAML.
- Whitelist validation accepts a directory inside an allowed root.
- Whitelist validation rejects paths outside allowed roots.
- Whitelist validation rejects traversal attempts.
- Whitelist validation rejects sibling-prefix paths that only look similar by string prefix.

## Compatibility

This is an initial skeleton change, so there is no runtime compatibility migration. Future features should build on these module boundaries and keep route layers thin while core logic remains independently testable.

## Risks / Trade-offs

- [Risk] Creating too much structure before behavior exists could add noise. -> Mitigation: add only documented directories and minimal package markers.
- [Risk] Path validation can be implemented incorrectly with string prefixes. -> Mitigation: require resolved path relationship checks and regression tests.
- [Risk] Config schema may change later. -> Mitigation: keep the initial YAML small and focused on app metadata and allowed input roots.

## Migration Plan

No data migration is required. Implementation can be rolled back by removing the new package/config/test files and restoring `current-state.md` to the previous skeleton-not-created state.

## Open Questions

None.
