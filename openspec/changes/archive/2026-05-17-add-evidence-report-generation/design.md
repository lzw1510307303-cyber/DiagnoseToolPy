## Context

DiagnoseToolPy has completed the analyzer foundation: directory scanning, streaming log reading, multiline merging, header parsing, and rule-based classification. The storage contract (storage-contract.md) defines the output file structure for analysis tasks, but no module yet generates these files.

The output system must take in-memory structured data from the analyzer chain and produce file artifacts under `data/output/{task_id}/`. No database, no AI calls, no full-file loading.

## Goals / Non-Goals

**Goals:**
- Generate `summary.html` from parsed log records and classification results using a Jinja2 template.
- Generate `evidence-pack.md` containing classification stats, timeline, key log features, and top exception samples.
- Generate `key-logs.txt` with bounded excerpt lines per classification category.
- Generate `case-draft.md` and `case-metadata-draft.yaml` from analysis results for casebase creation.
- Generate `retrieval-query.json` containing keywords, exception classes, components, fault modes for retrieval.
- Generate `artifacts/timeline.json` with time-windowed error/warn counts.
- Generate `artifacts/raw-samples.jsonl` with bounded samples per category.
- Write all files under `data/output/{task_id}/` following the storage contract.
- Keep samples bounded (e.g., max 20 samples per category) to avoid memory issues.

**Non-Goals:**
- Do not call AI APIs or generate AI diagnoses.
- Do not archive final cases or maintain case indexes.
- Do not implement manual case creation flows.
- Do not implement retrieval ranking or hybrid search.
- Do not re-read log files for output generation.

## Decisions

### Generate from In-Memory Data, Not Re-Reading Files

Output generation consumes the in-memory results already produced by the analyzer chain: parsed log records, classification results, and statistics. It does not re-open or re-read log files.

Alternative considered: re-scan log files for output generation. Rejected because it would require re-streaming large files and would duplicate scanner/reader logic.

### Jinja2 for HTML Template

The `summary.html` is generated using Jinja2 templates, consistent with the tech stack (pyyaml, jinja2 listed in AGENT.md dependencies).

Alternative considered: string formatting or hand-written HTML. Rejected because Jinja2 provides cleaner template maintenance, looping, and conditional rendering for dynamic content.

### Bounded Samples via In-Memory Lists

Samples are collected into in-memory lists with a configurable max per category (default 20). When the limit is reached, no more samples are added for that category.

Alternative considered: streaming sample writes. Rejected because output files need complete bounded lists, not open-ended streams.

### Separate Modules per Output Type

Each output file type has its own module: `evidence.py`, `report.py`, `case_draft.py`, `retrieval_query.py`. They share a common `OutputContext` that holds shared data (task_id, source_path, timestamps, file counts, statistics).

Alternative considered: single monolithic generator. Rejected because separate modules are easier to test and maintain.

### Timeline from Pre-Aggregated Buckets

Timeline generation uses pre-aggregated time buckets (e.g., 1-minute windows) computed during the analysis pass, not re-scanning logs.

Alternative considered: scan log files to build timeline. Rejected because it would duplicate parsing logic already done during classification.

## Data Flow

```
Analyzer Chain Output (in-memory):
  - List[ParsedLogRecord]
  - List[ClassificationResult]
  - ErrorCount, WarnCount, TotalBytes
  - TimelineBuckets

        v
+-------------------+
|  OutputContext     |  (shared task metadata)
+-------------------+

        v
   +----+----+----+----+
   |    |    |    |    |
   v    v    v    v    v
 evidence report case_ retrieval_
   .py   .py   draft.py  query.py

   |    |    |    |    |
   v    v    v    v    v
 evidence key   case case  retrieval
 -pack .logs  _draft metadata _query
 .md   .txt   .md  .yaml   .json
 summary timeline raw
 .html   .json samples
              .jsonl
```

## Module Responsibilities

### `diagnose_tool/analyzer/evidence.py`

Generates `evidence-pack.md` and `key-logs.txt`.
- Input: OutputContext, classification results, parsed records, error/warn counts
- Output: markdown evidence pack with stats table, timeline table, key features, top samples; plain text key logs
- Bounded: max 20 samples per category for evidence pack

### `diagnose_tool/analyzer/report.py`

Generates `summary.html` using Jinja2.
- Input: OutputContext, classification results, error/warn counts, timeline
- Output: HTML report with classification summary, error levels, key features
- Template: `diagnose_tool/templates/report.html`

### `diagnose_tool/analyzer/case_draft.py`

Generates `case-draft.md` and `case-metadata-draft.yaml`.
- Input: OutputContext, top classification category, parsed record samples
- Output: markdown case draft and YAML metadata following casebase schema
- Metadata fields: case_id, title, source_type=auto, status=draft, confidence=unconfirmed

### `diagnose_tool/analyzer/retrieval_query.py`

Generates `retrieval-query.json`.
- Input: OutputContext, classification results, parsed records
- Output: JSON with task_id, summary, components, fault_modes, exception_classes, keywords, stack_symbols, log_templates
- Follows retrieval-query-template.md schema

### `diagnose_tool/analyzer/timeline.py`

Generates `artifacts/timeline.json`.
- Input: time-bucketed error/warn counts
- Output: JSON array of {timestamp, error_count, warn_count} objects

### `diagnose_tool/templates/report.html`

Jinja2 HTML template for summary report.
- Variables: task_id, source_path, error_count, warn_count, classification_stats, timeline_data, top_exceptions
- Renders classification pie/bar summary, timeline chart placeholder, exception table

## File Outputs

All files written under `data/output/{task_id}/`:

| File | Module | Format |
|------|--------|--------|
| summary.html | report.py | HTML |
| evidence-pack.md | evidence.py | Markdown |
| key-logs.txt | evidence.py | Plain text |
| case-draft.md | case_draft.py | Markdown |
| case-metadata-draft.yaml | case_draft.py | YAML |
| retrieval-query.json | retrieval_query.py | JSON |
| artifacts/timeline.json | timeline.py | JSON |
| artifacts/raw-samples.jsonl | evidence.py | JSONL |

## Error Handling

- If output directory cannot be created: raise `OutputWriteError`.
- If template rendering fails: raise `TemplateRenderError` with template path context.
- If any required input field is missing: raise `MissingInputError` with field name.
- Partial output: if one generator fails, others should still complete if possible.

## Security Considerations

- Output paths are controlled by task_id (not user-provided paths).
- No user-provided content is executed.
- No network calls made.

## Memory Behavior

- All input data is in-memory already from analyzer chain.
- Sample bounded lists: max 20 per category.
- Timeline buckets: fixed number of time windows (e.g., minute-level buckets).
- No full log files loaded for output generation.

## Tests

- `tests/test_evidence.py`: verifies evidence-pack.md structure, key-logs.txt bounded lines, raw-samples.jsonl format
- `tests/test_report.py`: verifies summary.html renders with required sections, Jinja2 template variables
- `tests/test_case_draft.py`: verifies case-draft.md and case-metadata-draft.yaml have required fields
- `tests/test_retrieval_query.py`: verifies retrieval-query.json follows schema, has required fields
- `tests/test_timeline.py`: verifies timeline.json array structure with timestamp/error/warn fields

## Compatibility

- Output files follow existing storage-contract.md schema.
- No changes to existing API routes or data models.
- New modules do not import FastAPI.
- Existing scanner/reader/parser/classifier remain unchanged.

## Migration Plan

No data migration required. Rollback: remove the new modules, tests, and template file. Existing analyzer chain remains functional.

## Open Questions

- Should sample limits be configurable via `config/app.yaml`?
- Should timeline granularity (minute/hour/day buckets) be configurable?
