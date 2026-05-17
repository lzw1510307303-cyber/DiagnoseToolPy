# Harness Standard

## Purpose

The harness ensures that AI-assisted development remains aligned with the project architecture, constraints, and verification expectations.

## Harness Layers

### 1. Context Layer

Defines what the agent must know before work.

Includes:

- project brief
- current state
- design documents
- module boundaries
- storage contract

### 2. Constraint Layer

Defines what the agent must not violate.

Includes:

- no mandatory database
- no full-file log loading
- no browser-first large log upload
- no unbounded sample storage
- no hidden durable state outside documented files

### 3. Execution Layer

Defines how work should be implemented.

Includes:

- small changes
- testable modules
- API routes as thin wrappers
- business logic in service modules
- file-based state
- clear output file contracts

### 4. Verification Layer

Defines how work is validated.

Includes:

- unit tests
- fixture-based parser tests
- manual Web flow checklist
- output file contract validation
- regression tests for bugfixes

### 5. Continuity Layer

Defines how future agents resume work.

Includes:

- update `current-state.md`
- update relevant docs
- preserve ADRs
- archive completed OpenSpec changes
- avoid hidden assumptions

## Required Agent Behavior

Before implementation:

1. Read the relevant docs.
2. Identify affected modules.
3. Identify storage contract impact.
4. Identify tests to add.
5. Keep scope small.

During implementation:

1. Prefer minimal changes.
2. Avoid unrelated refactoring.
3. Keep logic testable.
4. Preserve file-based architecture.

After implementation:

1. Run or specify tests.
2. Update docs if needed.
3. Update `docs/00-project/current-state.md`.
