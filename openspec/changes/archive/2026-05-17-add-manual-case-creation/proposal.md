## Why

DiagnoseToolPy supports case creation from analysis task artifacts (auto cases), but cold-start environments, legacy systems, and new deployments need the ability to create fault cases manually. Manual case creation enables capturing historical experience, known fault patterns, and operational knowledge without requiring actual log analysis.

## What Changes

- New API route for creating manual fault cases via POST request.
- Support for source_type=manual in metadata.
- Support for DRAFT and ARCHIVED statuses.
- Case creation via API writes case.md and metadata.yaml to data/cases/.
- Index.yaml updated on case archive.
- Simple HTML form for manual case entry (optional, if UI exists).
- Tests for manual case creation API.

## Capabilities

### New Capabilities
- `manual-case-creation`: API endpoint and service for creating fault cases manually, supporting DRAFT and ARCHIVED states, with file-based storage and index updates.

### Modified Capabilities
- (none)

## Impact

- New API route: `POST /api/cases` for manual case creation.
- Modified `diagnose_tool/casebase/case_service.py` to support manual case creation.
- New test file: `tests/test_manual_case.py`.
- No new dependencies introduced.
- No database introduced.
