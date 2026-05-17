## Why

DiagnoseToolPy can scan directories, stream logs, merge multiline events, parse complex headers, and classify exceptions by keyword. However, it cannot yet produce the analysis output files defined in the storage contract: summary HTML reports, evidence packs, key log excerpts, case drafts, case metadata, and retrieval queries.

## What Changes

- Add `diagnose_tool/analyzer/evidence.py` to generate `evidence-pack.md`, `key-logs.txt`, and bounded raw samples.
- Add `diagnose_tool/analyzer/report.py` to generate `summary.html` from parsed log records and classification results.
- Add `diagnose_tool/analyzer/case_draft.py` to generate `case-draft.md` and `case-metadata-draft.yaml` from analysis results.
- Add `diagnose_tool/analyzer/retrieval_query.py` to generate `retrieval-query.json` from classification and parsed record data.
- Add `diagnose_tool/templates/report.html` as a Jinja2 template for the summary HTML.
- Add bounded sample extraction to avoid loading full log files into memory.
- Add output module that writes files under `data/output/{task_id}/`.
- Add tests for each output module verifying file structure and required fields.
- Update `docs/00-project/current-state.md` after implementation.
- Do not archive final cases, implement manual case creation, implement retrieval ranking, call AI APIs, or introduce databases.

## Capabilities

### New Capabilities
- `evidence-report-generation`: Generates diagnostic output files from analyzer results including evidence packs, HTML summaries, key log excerpts, case drafts, case metadata, and retrieval queries. Operates on in-memory structured data from parser/classifier and produces bounded samples.

### Modified Capabilities
- `log-reader-and-multiline`: The existing capability's sample extraction is extended to support bounded sample writing to `artifacts/raw-samples.jsonl`.

## Impact

- Affected modules: `analyzer`, `templates`
- Produces new output files: `summary.html`, `evidence-pack.md`, `key-logs.txt`, `case-draft.md`, `case-metadata-draft.yaml`, `retrieval-query.json`
- Produces new artifacts: `timeline.json`, `raw-samples.jsonl`
- Uses existing `task.yaml` and `progress.json` output directories from analysis tasks
- No database introduced; all output is file-based
- No AI API calls made

## Constraints

- No mandatory database introduced.
- No full log file read into memory.
- Samples must be bounded (max sample count per category).
- File-based source of truth remains unchanged.
- Evidence must be useful for AI diagnosis but must not invent conclusions.

## Risks

- Large log sets could produce very large output files if samples are not properly bounded.
- HTML template may need customization for different log formats.

## Verification

Run focused tests: `uv run pytest tests/test_evidence.py tests/test_report.py tests/test_case_draft.py tests/test_retrieval_query.py`
Run full test suite: `uv run pytest`
Run lint: `uv run ruff check .`
