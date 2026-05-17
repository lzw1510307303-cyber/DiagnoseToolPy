## 1. Case Service Extension

- [x] 1.1 Add create_manual_case function to diagnose_tool/casebase/case_service.py
- [x] 1.2 Implement slug auto-generation from title
- [x] 1.3 Implement unique case_id generation with collision handling
- [x] 1.4 Implement case_writer call for manual case
- [x] 1.5 Write tests: test_create_manual_case, test_slug_auto_generation, test_case_id_collision

## 2. API Route

- [x] 2.1 Create diagnose_tool/api/routes_case.py with POST /api/cases endpoint
- [x] 2.2 Implement request validation (title required, content optional)
- [x] 2.3 Implement HTTP response with created case info
- [x] 2.4 Wire route into main FastAPI app
- [x] 2.5 Write tests: test_post_cases_success, test_post_cases_validation_error

## 3. Integration and Verification

- [x] 3.1 Run full test suite: uv run pytest tests/
- [x] 3.2 Run lint: uv run ruff check .
- [x] 3.3 Update docs/00-project/current-state.md to mark manual case creation as implemented
- [x] 3.4 Final verification: all 160 tests pass, ruff clean
