# Context Policy

Agents must not read every document blindly.

Read documents based on task type.

## Always Read

- `AGENTS.md`
- `docs/README.md`
- `docs/00-project/project-brief.md`
- `docs/00-project/current-state.md`

## For Architecture Work

- `docs/01-architecture/design.md`
- `docs/01-architecture/module-boundaries.md`
- `docs/01-architecture/storage-contract.md`

## For OpenSpec Work

- `docs/03-openspec/proposal-rule.md`
- `docs/03-openspec/design-rule.md`
- `docs/03-openspec/spec-rule.md`
- `docs/03-openspec/tasks-rule.md`

## For Bugfix

- `docs/03-openspec/bugfix-rule.md`
- relevant module docs
- relevant tests
- relevant source files

## For Log Analyzer Work

- `docs/05-domain/log-format-guide.md`
- `docs/05-domain/log-analysis-rules.md`
- `docs/01-architecture/module-boundaries.md`

## For Casebase Work

- `docs/01-architecture/casebase-design.md`
- `docs/01-architecture/storage-contract.md`
- `docs/05-domain/fault-case-template.md`

## For Retrieval Work

- `docs/01-architecture/retrieval-design.md`
- `docs/05-domain/retrieval-query-template.md`

## Rule

If context is insufficient, inspect relevant source files before inventing behavior.
