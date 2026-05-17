## 1. Project Structure

- [x] 1.1 Create package, config, data, and test directories
  - Files: `diagnose_tool/`, `diagnose_tool/api/`, `diagnose_tool/core/`, `diagnose_tool/analyzer/`, `diagnose_tool/casebase/`, `diagnose_tool/retrieval/`, `diagnose_tool/exporter/`, `diagnose_tool/templates/`, `diagnose_tool/static/`, `config/`, `data/`, `tests/`
  - Behavior: establish documented module boundaries with package markers where needed
  - Tests: covered by import and runtime tests added later in this change
  - Verification: inspect directory structure and run `uv run pytest`

- [x] 1.2 Add initial application configuration file
  - Files: `config/app.yaml`
  - Behavior: define app metadata and server directory whitelist roots using file-based YAML
  - Tests: config loader test uses a temporary config and may assert default shape
  - Verification: `uv run pytest tests/test_config.py`

## 2. Core Modules

- [x] 2.1 Implement YAML config loading
  - Files: `diagnose_tool/core/config.py`, `tests/test_config.py`
  - Behavior: load valid YAML with `pathlib.Path`, expose app settings and allowed input roots, reject missing or malformed config clearly
  - Tests: valid YAML loads, missing config fails, malformed YAML fails
  - Verification: `uv run pytest tests/test_config.py`

- [x] 2.2 Implement server directory whitelist validation
  - Files: `diagnose_tool/core/security.py`, `tests/test_security.py`
  - Behavior: resolve requested paths and accept only directories equal to or contained by configured whitelist roots
  - Tests: allowed path, outside path, traversal attempt, sibling-prefix rejection
  - Verification: `uv run pytest tests/test_security.py`

## 3. Web Entry Point

- [x] 3.1 Implement FastAPI app initialization and health endpoint
  - Files: `diagnose_tool/main.py`, optional `tests/test_main.py`
  - Behavior: expose `diagnose_tool.main:app` and a health endpoint returning successful status without external services
  - Tests: FastAPI test client verifies health response
  - Verification: `uv run pytest tests/test_main.py`

- [x] 3.2 Implement simple index page
  - Files: `diagnose_tool/main.py`, optional `diagnose_tool/templates/index.html`, optional `tests/test_main.py`
  - Behavior: root route returns minimal HTML identifying DiagnoseToolPy
  - Tests: FastAPI test client verifies HTML response contains DiagnoseToolPy
  - Verification: `uv run pytest tests/test_main.py`

## 4. Verification And Documentation

- [x] 4.1 Run focused and full verification
  - Files: test suite
  - Behavior: verify config, security, and app skeleton behavior
  - Tests: `uv run pytest`
  - Verification: `uv run pytest` and `uv run ruff check .` if project tooling is available

- [x] 4.2 Update project current state
  - Files: `docs/00-project/current-state.md`
  - Behavior: mark package structure, FastAPI app, config loading, and whitelist validation as implemented; keep future analyzer/casebase/retrieval gaps unchanged
  - Tests: documentation review
  - Verification: confirm current-state reflects this completed change and no out-of-scope features are marked complete
