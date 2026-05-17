## 1. Case Models

- [x] 1.1 Create diagnose_tool/casebase/__init__.py
- [x] 1.2 Create diagnose_tool/casebase/case_models.py with FaultCaseMetadata, CaseIndexEntry, FaultCase dataclasses
- [x] 1.3 Write tests for case models: test_fault_case_metadata_fields, test_case_index_entry_fields
- [x] 1.4 Verify: uv run pytest tests/test_case_models.py

## 2. Case Writer

- [x] 2.1 Create diagnose_tool/casebase/case_writer.py with archive_case_from_task function
- [x] 2.2 Implement directory creation with {case_id}_{slug} naming
- [x] 2.3 Implement metadata.yaml writing with all required fields
- [x] 2.4 Implement evidence-pack.md and key-logs.txt copying from task output
- [x] 2.5 Write tests: test_archive_creates_directory, test_metadata_written, test_evidence_copied
- [x] 2.6 Verify: uv run pytest tests/test_case_writer.py

## 3. Case Loader

- [x] 3.1 Create diagnose_tool/casebase/case_loader.py with load_case and load_metadata functions
- [x] 3.2 Implement FileNotFoundError for missing case directory
- [x] 3.3 Write tests: test_load_case_returns_content, test_load_metadata, test_missing_raises_error
- [x] 3.4 Verify: uv run pytest tests/test_case_loader.py

## 4. Case Indexer

- [x] 4.1 Create diagnose_tool/casebase/case_indexer.py with rebuild_index and add_case_to_index functions
- [x] 4.2 Implement directory scanning to collect CaseIndexEntry from each case
- [x] 4.3 Implement index.yaml reading and writing
- [x] 4.4 Handle malformed metadata.yaml gracefully with warning log
- [x] 4.5 Write tests: test_rebuild_index_returns_entries, test_malformed_metadata_skipped
- [x] 4.6 Verify: uv run pytest tests/test_case_indexer.py

## 5. Case Service

- [x] 5.1 Create diagnose_tool/casebase/case_service.py with create_case_from_analysis, get_all_cases, get_case
- [x] 5.2 Orchestrate writer and indexer in create_case_from_analysis
- [x] 5.3 Write tests: test_create_case_orchestrates, test_get_all_cases, test_get_case_by_id
- [x] 5.4 Verify: uv run pytest tests/test_case_service.py

## 6. Integration and Verification

- [x] 6.1 Run full test suite: uv run pytest tests/
- [x] 6.2 Run lint: uv run ruff check .
- [x] 6.3 Update docs/00-project/current-state.md to mark casebase file storage as implemented
- [x] 6.4 Final verification: all 142 tests pass, ruff clean
