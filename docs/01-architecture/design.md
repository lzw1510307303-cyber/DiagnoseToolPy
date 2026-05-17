# DiagnoseToolPy Design

## Overview

DiagnoseToolPy is a lightweight Web-based diagnostic assistant for operational stability.

It supports:

- server-side log directory scanning
- large-log streaming analysis
- multiline stack trace merge
- complex log header parsing
- rule-based exception classification
- evidence package generation
- case draft generation
- manual case creation
- file-based case knowledge base
- retrieval without mandatory embeddings
- optional vector search

## Architecture Principle

```text
File documents are the source of truth.
Indexes are rebuildable caches.
AI diagnosis is assistive.
Human confirmation is required for final root cause.
```

## Overall Architecture

```plantuml
@startuml
title DiagnoseToolPy Overall Architecture

actor User
actor Developer
actor LLM as "AI Model"

rectangle "Browser Web UI" as UI {
  component "Directory Selection"
  component "Task Progress"
  component "Report View"
  component "Casebase"
  component "Prompt Copy"
}

rectangle "FastAPI Backend" as API {
  component "Source API"
  component "Task API"
  component "Report API"
  component "Case API"
  component "Retrieval API"
}

rectangle "Analyzer" as Analyzer {
  component "Scanner"
  component "Reader"
  component "Multiline Merger"
  component "Header Parser"
  component "Classifier"
  component "Timeline Builder"
  component "Evidence Builder"
  component "Report Builder"
  component "Case Draft Builder"
}

rectangle "Casebase" as Casebase {
  component "Case Writer"
  component "Case Loader"
  component "Case Indexer"
  component "Case Templates"
}

rectangle "Retrieval" as Retrieval {
  component "Keyword Search"
  component "BM25 Search"
  component "Rule Matcher"
  component "Optional Vector Search"
  component "Hybrid Ranker"
}

database "File System" as FS {
  folder "data/input"
  folder "data/output"
  folder "data/cases"
  folder "data/indexes"
  folder "data/runtime"
}

User --> UI
Developer --> UI
UI --> API
API --> Analyzer
API --> Casebase
API --> Retrieval

Analyzer --> FS
Casebase --> FS
Retrieval --> FS

API --> LLM : evidence-pack + similar cases

@enduml
```

## Main Flow

```text
server log directory
→ scan
→ stream read
→ merge multiline events
→ parse headers
→ classify exceptions
→ generate timeline
→ sample key logs
→ generate evidence-pack
→ retrieve similar cases
→ build AI prompt
→ archive as case
```

## Key Output Files

Analysis task:

```text
data/output/{task_id}/
├── task.yaml
├── progress.json
├── summary.html
├── evidence-pack.md
├── key-logs.txt
├── case-draft.md
├── case-metadata-draft.yaml
├── retrieval-query.json
└── artifacts/
```

Archived case:

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

## Memory Behavior

Large files must be processed by streaming reads.

Forbidden:

```python
content = file.read()
```

Required:

```python
for line in file:
    process(line)
```

Samples must be bounded.

## Security Boundary

The backend may only scan directories under configured input roots.

Invalid or unauthorized paths must be rejected before scanning.
