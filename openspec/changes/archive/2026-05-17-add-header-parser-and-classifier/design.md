## Context

DiagnoseToolPy currently supports server directory scanning, streaming text/gzip log reading, and multiline event candidate merging. The next analyzer step is converting raw event candidates into structured log records and assigning an initial category using configurable local YAML rules.

The implementation must follow the documented complex header strategy: parse timestamp and level with regex, scan bracket groups with balanced bracket logic, preserve raw content on failure, and avoid naive `split("[")` or `split("]")` parsing.

## Goals / Non-Goals

**Goals:**

- Add `diagnose_tool/analyzer/header_parser.py` for parsing complex log headers.
- Support the expected fields: timestamp, level, module, thread, logger, message, raw, file path, line number, and parse status.
- Support parse statuses `FULL`, `PARTIAL`, and `RAW`.
- Preserve raw event content for malformed or partially parsed lines.
- Add `diagnose_tool/analyzer/classifier.py` for loading YAML rules and classifying events by keyword.
- Add default rule files under `config/rules/`.
- Add tests for nested brackets, missing fields, malformed lines, and rule matching.
- Update `docs/00-project/current-state.md` after implementation.

**Non-Goals:**

- Do not generate reports, evidence packs, timelines, or task output files.
- Do not implement casebase, retrieval, AI integration, or database-backed storage.
- Do not add API routes for parsing/classification in this change.
- Do not implement sampling, aggregation, or full analysis task orchestration.

## Decisions

### Parser Input And Output

The parser will accept a raw event candidate or explicit raw text plus source metadata. It will return a structured parsed record, preferably a dataclass, containing all expected fields and `parse_status`.

Alternative considered: return plain dictionaries only. This is rejected because explicit models make tests and later analyzer composition safer.

### Regex Before Bracket Scanning

The parser will first match timestamp and level at the beginning of the event text. If timestamp/level are missing, it should return `RAW` or `PARTIAL` depending on what can be safely inferred. The parser then uses a balanced bracket scanner to extract bracket groups from the remaining header section.

Alternative considered: split by `[` and `]`. This is rejected by project rules because module/thread groups can contain nested brackets such as `[[order-core]worker-1]`.

### Module And Thread Extraction

The first balanced bracket group represents module/thread. For values like `[[order-core]worker-1]`, module should be `order-core` and thread should be `worker-1`. If module/thread cannot be separated safely, preserve the raw group and return `PARTIAL` rather than discarding the event.

Alternative considered: require all fields to be present for a parsed record. This is rejected because malformed logs must still be preserved.

### Classification Rules

Rules will be local YAML files under `config/rules/*.yaml`, with fields such as `category`, `display_name`, `severity`, and `keywords`. The classifier will load rule files with PyYAML and match keywords against parsed message and raw text. V0.1 can return the first matched rule and fall back to `unknown` when no rule matches.

Alternative considered: hard-code categories in Python. This is rejected because classification must be configurable by YAML.

### No Durable Output Files

The parser and classifier return in-memory structures only. This change does not write task or evidence output files.

Alternative considered: persist parsed events or classification results under `data/output`. This is rejected because file-based task state and evidence generation are separate later changes.

## Data Flow

1. Multiline merger emits a raw event candidate.
2. Header parser parses timestamp/level, scans balanced bracket groups, and returns a parsed log record.
3. Rule loader loads YAML classification rules from `config/rules/`.
4. Classifier checks rule keywords against parsed message and raw text.
5. Classifier returns a classification result with category, display name, severity, matched keyword, or `unknown` fallback.
6. Future analyzer orchestration can aggregate and sample these results.

## Module Responsibilities

- `diagnose_tool/analyzer/header_parser.py`: parse complex headers, balanced bracket scanning, parse status assignment, raw preservation.
- `diagnose_tool/analyzer/classifier.py`: YAML rule loading, validation, keyword matching, unknown fallback.
- `config/rules/*.yaml`: default local classification rules.
- `tests/test_header_parser.py`: parser edge cases and raw preservation.
- `tests/test_classifier.py`: rule loading, invalid rule handling, matching, and unknown fallback.

## File Outputs

This change adds configuration files under `config/rules/`. These are durable local configuration files, not analysis outputs. No `task.yaml`, `progress.json`, `evidence-pack.md`, `case.md`, `metadata.yaml`, `index.yaml`, or `retrieval-query.json` files are created or modified.

## Error Handling

- Header parsing failure must return a `RAW` parsed record containing the original raw text.
- Partial bracket/header parsing must return `PARTIAL` with any safe fields populated.
- Malformed YAML rules should raise a clear rule loading error.
- Rules missing required fields should be rejected with clear errors.
- No event should be discarded because parsing or classification is uncertain.

## Security Considerations

Rule loading reads local files from configured paths only and makes no network calls. Classification uses simple keyword matching and does not execute rule content.

## Memory Behavior

Header parsing and classification operate on one event at a time. Rule sets are small local YAML configuration files. This change does not read full log files and does not store all parsed events in memory.

## Tests

- Fully parse the documented nested bracket format.
- Parse module/thread from `[[module]thread]` without naive splitting.
- Return `PARTIAL` for missing logger or incomplete bracket groups while preserving raw content.
- Return `RAW` for malformed lines with no timestamp/level.
- Load valid YAML rule files.
- Reject malformed or incomplete rules.
- Match a rule keyword against parsed message/raw text.
- Return `unknown` when no rules match.

## Compatibility

This adds analyzer primitives consumed by later aggregation, evidence, and report work. It does not alter existing API routes or persisted analysis output contracts.

## Risks / Trade-offs

- [Risk] Real-world logs may vary beyond the first supported format. -> Mitigation: preserve raw text and use `PARTIAL`/`RAW` rather than failing hard.
- [Risk] Keyword classification can produce false positives. -> Mitigation: keep rules configurable and expose matched keyword in the classification result.
- [Risk] Rule schema could evolve. -> Mitigation: keep the initial rule shape small and explicit.

## Migration Plan

No data migration is required. Rollback is removing parser/classifier modules, default rules, tests, and current-state updates.

## Open Questions

None.
