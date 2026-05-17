## Context

DiagnoseToolPy has casebase file storage implemented for auto-generated cases from analysis tasks. The casebase module provides `archive_case_from_task` for creating cases from task artifacts. However, users cannot yet create cases manually for scenarios where no log analysis exists (cold-start, legacy systems, known fault patterns).

Manual case creation enables capturing operational knowledge and historical experience without requiring actual incident logs.

## Goals / Non-Goals

**Goals:**
- Provide API endpoint for manual fault case creation
- Support source_type=manual in metadata
- Support DRAFT and ARCHIVED statuses
- Write case.md and metadata.yaml to data/cases/{case_id}_{slug}/
- Update index.yaml on case archive
- Keep casebase logic independent from FastAPI (service layer only)
- Add tests for manual case creation

**Non-Goals:**
- Do not implement full rich-text editor
- Do not implement authentication
- Do not implement vector search or AI calls
- Do not implement case update/delete (archive only)
- Do not introduce database

## Decisions

### API route creates case via service, not directly

The API route (`POST /api/cases`) validates input and delegates to `case_service.create_manual_case()`. The service handles writing files and updating index. This keeps API thin and casebase testable without FastAPI.

Alternative (write in route) was rejected because it mixes validation with file I/O and makes unit testing harder.

### Slug auto-generated from title

If slug is not provided, it is auto-generated from the title using lowercase, spaces-to-hyphens, and non-alphanumeric removal. This simplifies the API.

Alternative (require slug) was rejected because it adds friction to manual case creation.

### Case ID uses counter or timestamp

Case IDs follow the pattern "CASE-{timestamp}" for simplicity. No centralized counter is needed.

Alternative (sequential counter) was rejected because it requires state management.

### Existing case_writer reused

`archive_case_from_task` and `create_manual_case` share the same `case_writer` logic for writing metadata.yaml and case.md. The difference is input source (task artifacts vs direct parameters).

Alternative (separate writer) was rejected to avoid duplication.

## Risks / Trade-offs

- **[Risk]** Case ID collision if two cases created in same second → [Mitigation] Append random suffix if collision detected
- **[Risk]** Large manual case content in memory → [Mitigation] Stream writes for case.md content; bounded metadata fields
- **[Risk]** Index corruption on partial write → [Mitigation] Write index last; original index preserved on failure

## Migration Plan

- Deploy new route alongside existing routes
- Manual cases are distinguishable by source_type=manual
- No data migration needed
- Rollback: remove route and service function

## Open Questions

- Should manual cases support copying evidence from existing cases?
- Should there be a template selection for manual cases?
