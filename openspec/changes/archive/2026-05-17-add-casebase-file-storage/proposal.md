## Why

DiagnoseToolPy has an analyzer that generates case drafts from log analysis, but those drafts cannot yet be archived as persistent fault cases. The casebase module needs file-based storage to create, load, and index fault cases as `case.md` + `metadata.yaml` documents.

## What Changes

- New `casebase` module with models, writer, loader, indexer, and service layers.
- Fault cases stored as `case.md` + `metadata.yaml` under `data/cases/{case_id}_{slug}/`.
- Evidence artifacts (evidence-pack.md, key-logs.txt) copied from analysis task output.
- `data/cases/index.yaml` maintained on case archive, rebuildable from directories.
- `case_writer.py` creates cases from analysis task artifacts.
- `case_indexer.py` maintains and rebuilds the case index.
- Tests for case writing and index rebuild.

## Capabilities

### New Capabilities
- `casebase-file-storage`: File-based fault case storage with case creation from analysis artifacts, metadata management, and rebuildable index.

### Modified Capabilities
- (none)

## Impact

- New module: `diagnose_tool/casebase/`
- New tests: `tests/test_case_writer.py`, `tests/test_case_indexer.py`
- Storage: `data/cases/` directory structure and `data/cases/index.yaml`
- No database introduced
- No embedding/vector search
