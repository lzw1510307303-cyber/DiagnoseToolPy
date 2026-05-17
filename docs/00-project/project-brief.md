# Project Brief

## Project Name

DiagnoseToolPy

## Positioning

DiagnoseToolPy is a lightweight Web-based diagnostic assistant for system stability work.

It organizes fault evidence from server-side log directories, generates AI-ready evidence packages, and converts each diagnosis into reusable fault cases.

## Core Value

The project turns:

```text
scattered logs + personal experience + temporary troubleshooting
```

into:

```text
structured evidence + reusable cases + searchable knowledge + AI-ready context
```

## Primary Users

- Test engineers
- Operations engineers
- Frontline support engineers
- Backend developers
- AI-assisted development users

## Main Workflows

### Workflow 1: Analyze Logs

```text
upload logs to server directory
→ select directory in Web UI
→ scan and analyze logs
→ generate report and evidence-pack
→ copy AI prompt or download artifacts
```

### Workflow 2: Archive a Case

```text
analysis task completed
→ generate case draft
→ user fills confirmed root cause and resolution
→ archive as case.md + metadata.yaml
→ update index
```

### Workflow 3: Manual Case Creation

```text
open casebase
→ create manual case
→ fill fault symptom/root cause/handling experience
→ archive case
→ use for future retrieval
```

### Workflow 4: AI Diagnosis with Retrieval

```text
current evidence-pack
→ extract retrieval query
→ retrieve similar cases without embeddings by default
→ inject similar cases into prompt
→ send to LLM
→ human confirms root cause
```

## Core Principles

- File system is the source of truth.
- No mandatory database.
- Server-side directory scanning is the primary log input path.
- Large logs must be processed by streaming reads.
- Case documents are long-term knowledge assets.
- Retrieval must work without embeddings by default.
- Vector search is optional and disabled by default.
- AI diagnosis is assistive, not authoritative.

## Non-goals

- Not an ELK replacement.
- Not a real-time log collection platform.
- Not a distributed log search engine.
- Not a database-backed ticket system.
- Not a mandatory AI platform.
