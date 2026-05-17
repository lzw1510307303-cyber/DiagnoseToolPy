## Context

DiagnoseToolPy has evidence/report generation that outputs case drafts. The casebase module must now persist these drafts as durable fault cases stored as files. Each fault case is a directory containing `case.md` (human-readable report) and `metadata.yaml` (structured fields). The case index at `data/cases/index.yaml` tracks all archived cases and must be rebuildable from case directories.

Existing storage contract defines the case directory structure. This design adds the code to create, read, and index those files.

## Goals / Non-Goals

**Goals:**
- Create `diagnose_tool/casebase/` module with clear sub-module responsibilities
- Create fault cases from analysis task artifacts (case-draft.md, case-metadata-draft.yaml, evidence-pack.md, key-logs.txt)
- Write `case.md` and `metadata.yaml` following the fault-case-template.md schema
- Copy evidence artifacts into case directory
- Maintain `data/cases/index.yaml` on archive
- Support rebuilding index.yaml from case directories
- Keep casebase logic independent from FastAPI

**Non-Goals:**
- Do not implement vector search or embedding-based retrieval
- Do not implement AI API calls
- Do not implement manual case editor UI
- Do not introduce any database
- Do not implement case update/delete (archive only for v1)

## Decisions

### Case directory naming: `{case_id}_{slug}`

Case directories are named `{case_id}_{slug}` where slug is derived from title. This makes directories human-readable and unique. Alternative (numeric ID only) was rejected because slug provides immediate context.

### metadata.yaml is the case schema of record

All structured case metadata lives in `metadata.yaml`. `case.md` is the human-readable document. This separation keeps files focused and rebuildable. Alternative (embed metadata in case.md front-matter) was rejected for simplicity and easier programmatic access.

### Index rebuild reads directories, not files

The indexer scans `data/cases/` directories to rebuild `index.yaml`. It reads each `metadata.yaml` to extract case metadata. This avoids maintaining a separate index as a source of truth. Alternative (track index entries on every write) was rejected because it creates index corruption risk.

### Copy evidence artifacts, don't reference

When archiving a case, evidence-pack.md and key-logs.txt are copied into the case directory. This makes the case self-contained and resilient to task output cleanup. Alternative (reference task output path) was rejected because task output is temporary.

### Separate writer and indexer

`case_writer.py` handles case creation and file writing. `case_indexer.py` handles index maintenance and rebuild. `case_service.py` orchestrates. Separation allows independent testing and future extension.

## Module Responsibilities

### `case_models.py`
Pydantic/dataclass models for case structures:
- `FaultCaseMetadata`: case_id, title, slug, source_type, status, confidence, tags, components, fault_modes, exception_classes, key_phrases, created_at
- `FaultCase`: metadata + case_path + evidence_path
- `CaseIndexEntry`: case_id, title, slug, status, source_type, created_at for index records

### `case_writer.py`
- `archive_case_from_task(task_output_path, case_metadata)`: create case directory, copy evidence, write case.md from template, write metadata.yaml
- Validates task output exists before archiving
- Creates directory structure under `data/cases/{case_id}_{slug}/`

### `case_loader.py`
- `load_case(case_path)`: load case.md and metadata.yaml from case directory
- `load_metadata(case_path)`: load only metadata.yaml
- Returns structured FaultCase object

### `case_indexer.py`
- `rebuild_index()`: scan data/cases/, read each metadata.yaml, produce list of CaseIndexEntry
- `add_case_to_index(case_metadata)`: append or update index entry
- `get_index()`: read and return current index.yaml
- Index stored at `data/cases/index.yaml`

### `case_service.py`
- `create_case_from_analysis(task_output_path, case_metadata)`: orchestrate writer + indexer
- `get_all_cases()`: return all cases
- `get_case(case_id)`: return specific case

## File Outputs

### Case Directory Structure
```
data/cases/{case_id}_{slug}/
├── case.md           (from template, user-filled or AI-assisted)
├── metadata.yaml     (structured fields)
├── evidence-pack.md  (copied from task output)
├── key-logs.txt      (copied from task output)
├── ai-diagnosis.md   (optional, from AI)
├── review.md         (optional, human review notes)
├── actions.md        (optional, action items)
└── artifacts/        (optional, additional artifacts)
```

### Index File
```
data/cases/index.yaml
```
Schema: list of CaseIndexEntry objects

## Error Handling

- Case directory already exists: raise `CaseExistsError`
- Task output missing required files: raise `MissingTaskArtifactError`
- Invalid metadata.yaml: raise `InvalidMetadataError` with field details
- Index write failure: log error, do not fail case creation

## Security Considerations

- Case paths derived from case_id and slug, not user input
- No network calls
- No code execution from case content
- Path traversal protection via Path validation

## Memory Behavior

- Streaming reads for case.md when loading large cases
- Bounded list for index rebuild (scan directories, not load all content)
- No full evidence files held in memory

## Tests

- `test_case_writer.py`: archive from task, metadata validation, evidence copy
- `test_case_indexer.py`: rebuild index, add case, malformed metadata handling
- `test_case_loader.py`: load case, load metadata
- `test_case_service.py`: end-to-end create and retrieve

## Compatibility

- Uses existing storage contract for case directory structure
- No changes to analyzer or API routes
- Casebase module does not import FastAPI
- Existing evidence/report generation unchanged
