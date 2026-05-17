## Why

DiagnoseToolPy can stream logs and merge multiline event candidates, but it cannot yet extract structured fields from the supported complex header format or classify events using configurable rules. This change adds the next analyzer layer: safe header parsing with balanced bracket scanning and YAML-driven exception/category classification.

## What Changes

- Add `diagnose_tool/analyzer/header_parser.py` for parsing the supported header format: `时间 级别 [[服务内部模块]线程名] [类名信息] message`.
- Parse timestamp and level with regex before bracket scanning.
- Parse bracket groups with balanced bracket scanning, not naive bracket splitting.
- Extract module, thread, logger, message, raw, file path, line number, and `parse_status`.
- Support `parse_status` values `FULL`, `PARTIAL`, and `RAW`.
- Preserve raw content when parsing fails or is incomplete.
- Add `diagnose_tool/analyzer/classifier.py` for loading YAML classification rules and matching parsed/raw events.
- Add default YAML rule files under `config/rules/` using category, display name, severity, and keywords.
- Add tests for nested brackets, missing fields, malformed lines, raw preservation, YAML rule loading, and rule matching.
- Update `docs/00-project/current-state.md` after implementation.

## Capabilities

### New Capabilities
- `header-parser-and-classifier`: Defines complex log header parsing with balanced bracket scanning and YAML rule-based event classification.

### Modified Capabilities

None.

## Impact

- Affected modules: `analyzer`, `config`, `docs`, `tests`.
- Builds on streaming reader and multiline event candidates without adding API behavior.
- Adds configurable local YAML rules only; no database, AI, casebase, retrieval, reports, or evidence output are introduced.
- Does not write analysis task outputs such as `task.yaml`, `progress.json`, `evidence-pack.md`, `case-draft.md`, or retrieval artifacts.
