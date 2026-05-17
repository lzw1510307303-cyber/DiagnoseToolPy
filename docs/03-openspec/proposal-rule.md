# Proposal Rule

A proposal must explain why the change is needed and what it changes.

## Required Sections

### 1. Problem

Describe the user-visible or engineering problem.

### 2. Goal

Describe the intended outcome.

### 3. Scope

List what is included.

### 4. Out of Scope

List what is explicitly excluded.

### 5. Affected Modules

Choose from:

- api
- core
- analyzer
- casebase
- retrieval
- exporter
- templates
- config
- docs
- deployment

### 6. Storage Impact

State whether the change affects:

- task.yaml
- progress.json
- case.md
- metadata.yaml
- index.yaml
- evidence-pack.md
- retrieval-query.json

### 7. Constraints

Must confirm:

- No mandatory database introduced.
- No full log file read into memory.
- No browser-first large log upload flow.
- File-based source of truth remains unchanged.

### 8. Risks

List implementation risks.

### 9. Verification

Describe how to verify.

## Proposal Quality Bar

A good proposal is small enough to implement and test in one focused change.
