# Casebase Design

## Goal

The casebase stores reusable fault cases as local documents.

It supports:

- auto-generated case drafts from analysis tasks
- manual case creation
- imported cases
- template-based cases
- retrieval and export

## Case Source Types

- `auto`: generated from log analysis
- `manual`: manually created
- `imported`: imported from external documents
- `template`: created from built-in templates

## Case States

- `DRAFT`
- `REVIEWING`
- `ARCHIVED`
- `DEPRECATED`

## Case Directory

```text
data/cases/{case_id}_{slug}/
├── case.md
├── metadata.yaml
├── evidence-pack.md
├── key-logs.txt
├── ai-diagnosis.md
├── review.md
├── actions.md
└── artifacts/
```

## Case Creation from Analysis Task

```text
task completed
→ load case-draft.md
→ user fills confirmed root cause
→ write case.md
→ write metadata.yaml
→ copy evidence artifacts
→ update index.yaml
→ update retrieval indexes
```

## Manual Case Creation

```text
open casebase
→ new case
→ select template
→ fill fields
→ preview case.md
→ archive
→ update index
```

## Manual Case Importance

Manual cases support:

- cold-start environments
- new operational systems without logs
- legacy experience migration
- known fault pattern initialization
- internal training material setup

## Required Case Sections

- Basic Information
- Symptom
- Impact Scope
- Key Timeline
- Key Log Features
- AI Preliminary Diagnosis
- Human-confirmed Root Cause
- Handling Process
- Fix Plan
- Lessons Learned
- Follow-up Checklist
