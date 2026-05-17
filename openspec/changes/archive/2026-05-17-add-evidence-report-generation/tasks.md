## 1. Output Foundation

- [x] 1.1 Define OutputContext dataclass and output directory creation
  - Files: `diagnose_tool/analyzer/output_context.py`
  - Behavior: hold shared task metadata (task_id, source_path, timestamps, file counts, error/warn counts); create `data/output/{task_id}/artifacts/` directories
  - Tests: directory creation, context field access
  - Verification: `uv run pytest tests/test_output_context.py`

- [x] 1.2 Add bounded sample collection utilities
  - Files: `diagnose_tool/analyzer/sampling.py`, `tests/test_sampling.py`
  - Behavior: maintain bounded lists per category with max 20 items
  - Tests: bounded list respects limit, categories isolated
  - Verification: `uv run pytest tests/test_sampling.py`

## 2. Timeline Generator

- [x] 2.1 Implement timeline bucket aggregation
  - Files: `diagnose_tool/analyzer/timeline.py`, `tests/test_timeline.py`
  - Behavior: compute minute-level time buckets from parsed records; emit list of {timestamp, error_count, warn_count}
  - Tests: bucket counts correct, empty input produces empty list
  - Verification: `uv run pytest tests/test_timeline.py`

- [x] 2.2 Implement timeline JSON file writer
  - Files: `diagnose_tool/analyzer/timeline.py`
  - Behavior: write timeline list to `data/output/{task_id}/artifacts/timeline.json`
  - Tests: file written with valid JSON structure
  - Verification: `uv run pytest tests/test_timeline.py`

## 3. Evidence Pack Generator

- [x] 3.1 Implement evidence pack markdown generator
  - Files: `diagnose_tool/analyzer/evidence.py`, `tests/test_evidence.py`
  - Behavior: generate `evidence-pack.md` with basic info, classification stats table, timeline table, key features, top samples
  - Tests: required sections present, stats table has rows, samples bounded to 20
  - Verification: `uv run pytest tests/test_evidence.py`

- [x] 3.2 Implement key logs text generator
  - Files: `diagnose_tool/analyzer/evidence.py`
  - Behavior: generate `key-logs.txt` with labeled excerpts per category, bounded to 20 per category
  - Tests: lines include category label and raw excerpt, samples bounded
  - Verification: `uv run pytest tests/test_evidence.py`

- [x] 3.3 Implement raw samples JSONL writer
  - Files: `diagnose_tool/analyzer/evidence.py`
  - Behavior: write `artifacts/raw-samples.jsonl` with one JSON object per line (category, raw, timestamp, level), bounded to 20 per category
  - Tests: valid JSONL format, one object per line, samples bounded
  - Verification: `uv run pytest tests/test_evidence.py`

## 4. HTML Report Generator

- [x] 4.1 Create Jinja2 HTML template for summary report
  - Files: `diagnose_tool/templates/report.html`
  - Behavior: template receives task_id, source_path, error_count, warn_count, classification_stats, top_exceptions, timeline_data
  - Tests: template renders without errors with valid context
  - Verification: `uv run pytest tests/test_report.py`

- [x] 4.2 Implement report generator module
  - Files: `diagnose_tool/analyzer/report.py`, `tests/test_report.py`
  - Behavior: render summary.html using Jinja2 template with provided context
  - Tests: rendered HTML contains required sections and data
  - Verification: `uv run pytest tests/test_report.py`

## 5. Case Draft Generator

- [x] 5.1 Implement case draft markdown generator
  - Files: `diagnose_tool/analyzer/case_draft.py`, `tests/test_case_draft.py`
  - Behavior: generate `case-draft.md` with basic info, fault description placeholder, key evidence references
  - Tests: required sections present, title derived from top category
  - Verification: `uv run pytest tests/test_case_draft.py`

- [x] 5.2 Implement case metadata YAML generator
  - Files: `diagnose_tool/analyzer/case_draft.py`
  - Behavior: generate `case-metadata-draft.yaml` with case_id, title, slug, source_type=auto, status=draft, confidence=unconfirmed, tags, components, fault_modes, exception_classes, key_phrases
  - Tests: required YAML fields present and correctly typed
  - Verification: `uv run pytest tests/test_case_draft.py`

## 6. Retrieval Query Generator

- [x] 6.1 Implement retrieval query JSON generator
  - Files: `diagnose_tool/analyzer/retrieval_query.py`, `tests/test_retrieval_query.py`
  - Behavior: generate `retrieval-query.json` with task_id, summary, components, fault_modes, exception_classes, keywords, stack_symbols, log_templates
  - Tests: required JSON fields present, no raw logs included
  - Verification: `uv run pytest tests/test_retrieval_query.py`

## 7. Verification and Documentation

- [x] 7.1 Run focused and full test verification
  - Files: test suite
  - Behavior: run all evidence, report, case draft, retrieval query, and timeline tests
  - Tests: `uv run pytest tests/test_evidence.py tests/test_report.py tests/test_case_draft.py tests/test_retrieval_query.py tests/test_timeline.py`, then `uv run pytest`
  - Verification: `uv run pytest` and `uv run ruff check .`

- [x] 7.2 Update project current state
  - Files: `docs/00-project/current-state.md`
  - Behavior: mark evidence package generator and report generator as implemented; leave casebase archiving, retrieval, and deployment incomplete
  - Tests: documentation review
  - Verification: confirm current-state reflects only this completed capability
