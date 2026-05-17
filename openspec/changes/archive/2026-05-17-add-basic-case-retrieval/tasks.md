## 1. Retrieval Module Structure

- [x] 1.1 Create diagnose_tool/retrieval/__init__.py
- [x] 1.2 Verify retrieval directory exists and is accessible

## 2. Query Builder

- [x] 2.1 Create diagnose_tool/retrieval/query_builder.py with build_retrieval_query function
- [x] 2.2 Implement reading from retrieval-query.json file path
- [x] 2.3 Implement reading from analyzer output directory
- [x] 2.4 Write tests: test_build_query_from_file, test_build_query_from_directory

## 3. Keyword Search

- [x] 3.1 Create diagnose_tool/retrieval/keyword_search.py with search_by_keywords function
- [x] 3.2 Implement keyword overlap scoring with case content and metadata
- [x] 3.3 Write tests: test_keyword_search_returns_scores, test_keyword_search_empty_on_no_match

## 4. Rule Matcher

- [x] 4.1 Create diagnose_tool/retrieval/rule_matcher.py with match_by_rules function
- [x] 4.2 Implement scoring for tags, components, fault_modes, exception_classes, key_phrases
- [x] 4.3 Write tests: test_rule_matcher_returns_scores, test_rule_matcher_empty_on_no_match

## 5. BM25 Search

- [x] 5.1 Create diagnose_tool/retrieval/bm25_search.py with search_bm25 function
- [x] 5.2 Implement optional rank-bm25 integration with import check
- [x] 5.3 Return empty list when rank-bm25 not available
- [x] 5.4 Write tests: test_bm25_returns_scores, test_bm25_empty_when_not_available

## 6. Prompt Context

- [x] 6.1 Create diagnose_tool/retrieval/prompt_context.py with generate_prompt_context function
- [x] 6.2 Include reference-only markers in output
- [x] 6.3 Implement bounded results (max_cases parameter)
- [x] 6.4 Write tests: test_prompt_context_has_markers, test_prompt_context_bounded

## 7. Integration Tests

- [x] 7.1 Write tests/test_retrieval.py with integration tests for full retrieval flow
- [x] 7.2 Run full test suite: uv run pytest tests/
- [x] 7.3 Run lint: uv run ruff check .
- [x] 7.4 Update docs/00-project/current-state.md to mark retrieval as implemented
- [x] 7.5 Final verification: all tests pass, ruff clean
