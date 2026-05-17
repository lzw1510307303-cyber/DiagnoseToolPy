# Glossary

## Analysis Task

A single log analysis execution.

It reads a server-side log directory and generates task artifacts under:

```text
data/output/{task_id}/
```

## Evidence Pack

A Markdown document generated from analysis results and intended for AI diagnosis.

File name:

```text
evidence-pack.md
```

## Fault Case

A reusable knowledge asset representing a diagnosed or known fault.

A case is stored as:

```text
case.md
metadata.yaml
```

## Casebase

The local file-based fault case knowledge base under:

```text
data/cases/
```

## Retrieval Query

A structured query extracted from current analysis results.

It contains exception classes, key phrases, components, fault modes, tags, and stack symbols.

## Source of Truth

The durable data representation.

In this project, the source of truth is the file system, especially Markdown/YAML files.

## Index

A rebuildable cache used for faster search.

Examples:

- `data/cases/index.yaml`
- `data/indexes/fulltext/index.jsonl`
- optional vector index

## Harness

The project-level control system for AI-assisted development.

It includes context rules, constraints, execution policies, verification rules, and continuity practices.
