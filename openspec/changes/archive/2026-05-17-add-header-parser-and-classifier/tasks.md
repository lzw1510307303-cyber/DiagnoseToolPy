## 1. Header Parser

- [x] 1.1 Define parsed log record model and parse status constants
  - Files: `diagnose_tool/analyzer/header_parser.py`, `tests/test_header_parser.py`
  - Behavior: represent timestamp, level, module, thread, logger, message, raw, file path, line number, and `parse_status` values `FULL`, `PARTIAL`, `RAW`
  - Tests: model fields verified through parser tests
  - Verification: `uv run pytest tests/test_header_parser.py`

- [x] 1.2 Implement timestamp and level extraction
  - Files: `diagnose_tool/analyzer/header_parser.py`, `tests/test_header_parser.py`
  - Behavior: parse timestamp and level from the start of the raw event using regex and preserve raw text if missing
  - Tests: valid timestamp/level, malformed line returns `RAW`
  - Verification: `uv run pytest tests/test_header_parser.py`

- [x] 1.3 Implement balanced bracket scanner
  - Files: `diagnose_tool/analyzer/header_parser.py`, `tests/test_header_parser.py`
  - Behavior: extract bracket groups such as `[[order-core]worker-1]` without naive bracket splitting
  - Tests: nested bracket module/thread group, incomplete bracket group
  - Verification: `uv run pytest tests/test_header_parser.py`

- [x] 1.4 Implement full and partial header parsing
  - Files: `diagnose_tool/analyzer/header_parser.py`, `tests/test_header_parser.py`
  - Behavior: extract module, thread, logger, and message when available; return `FULL`, `PARTIAL`, or `RAW` without discarding events
  - Tests: full nested header, missing logger partial parse, malformed raw parse, raw preservation
  - Verification: `uv run pytest tests/test_header_parser.py`

## 2. Rule Classifier

- [x] 2.1 Add default YAML rule files
  - Files: `config/rules/common.yaml`, optional additional `config/rules/*.yaml`
  - Behavior: provide small local rules using category, display name, severity, and keywords
  - Tests: rule loader consumes default-style YAML fixtures or temp files
  - Verification: `uv run pytest tests/test_classifier.py`

- [x] 2.2 Define classification rule and result models
  - Files: `diagnose_tool/analyzer/classifier.py`, `tests/test_classifier.py`
  - Behavior: represent loaded rules and classification results including category, display name, severity, and matched keyword
  - Tests: model fields verified through classifier tests
  - Verification: `uv run pytest tests/test_classifier.py`

- [x] 2.3 Implement YAML rule loader
  - Files: `diagnose_tool/analyzer/classifier.py`, `tests/test_classifier.py`
  - Behavior: load local YAML rule files, validate required fields, and raise clear errors for malformed or incomplete rules
  - Tests: valid rule loads, malformed YAML rejected, missing required field rejected
  - Verification: `uv run pytest tests/test_classifier.py`

- [x] 2.4 Implement keyword classification and unknown fallback
  - Files: `diagnose_tool/analyzer/classifier.py`, `tests/test_classifier.py`
  - Behavior: match configured keywords against parsed message and raw text, return first matching rule, and return `unknown` when no match exists
  - Tests: keyword match, raw-text match, no-match unknown fallback
  - Verification: `uv run pytest tests/test_classifier.py`

## 3. Verification And Documentation

- [x] 3.1 Run focused and full verification
  - Files: test suite
  - Behavior: verify parser and classifier behavior without reports, casebase, retrieval, AI, or database dependencies
  - Tests: `uv run pytest tests/test_header_parser.py tests/test_classifier.py`, then `uv run pytest`
  - Verification: `uv run pytest` and `uv run ruff check .`

- [x] 3.2 Update project current state
  - Files: `docs/00-project/current-state.md`
  - Behavior: mark complex log header parser and rule classifier as implemented; leave evidence, casebase, retrieval, and deployment incomplete
  - Tests: documentation review
  - Verification: confirm current-state reflects only this completed capability
