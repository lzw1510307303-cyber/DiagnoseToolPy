## Why

DiagnoseToolPy currently has project documentation and harness rules, but no runnable Python package, web entry point, configuration loader, or tests. This change creates the smallest executable foundation needed before log analysis, casebase, retrieval, or deployment work can be built safely.

## What Changes

- Create the planned package and data directory skeleton for the project.
- Add `config/app.yaml` as the initial file-based application configuration.
- Add `diagnose_tool/main.py` with FastAPI app initialization.
- Add a health check endpoint for runtime verification.
- Add a simple index page for the initial Web UI entry.
- Add `diagnose_tool/core/config.py` for YAML configuration loading.
- Add `diagnose_tool/core/security.py` for server directory whitelist validation.
- Add tests for config loading and path whitelist behavior.
- Update `docs/00-project/current-state.md` during implementation to record the completed skeleton state.

## Capabilities

### New Capabilities
- `project-skeleton`: Defines the initial runnable FastAPI project skeleton, file-based app configuration, and core path whitelist validation behavior.

### Modified Capabilities

None.

## Impact

- Affected modules: `api`, `core`, `templates`, `config`, `docs`, `tests`.
- Adds FastAPI runtime initialization but no log analysis, casebase, retrieval, AI integration, database, or deployment implementation.
- Adds YAML configuration as file-based source of runtime settings.
- Adds security validation for server-side directory access using configured whitelist roots.
- Adds pytest coverage for the initial core behavior.
