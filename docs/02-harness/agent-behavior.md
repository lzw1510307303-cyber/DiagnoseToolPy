# Agent Behavior

## Required Behavior

Agents working on this project must:

- preserve the file-system-first architecture
- keep changes small and reviewable
- write tests for core logic
- update current-state.md after completion
- avoid introducing infrastructure not requested by the user
- keep API routes thin
- keep business logic in service modules
- treat AI diagnosis as assistive, not final truth

## Forbidden Behavior

Agents must not:

- introduce mandatory databases
- load entire log files into memory
- make browser upload the main path for large logs
- write hidden durable state outside documented directories
- silently discard parsing failures
- convert AI diagnosis directly into confirmed root cause
- perform unrelated refactoring
- change storage contracts without documentation

## When Unclear

If the task is unclear:

1. inspect relevant docs
2. inspect source files
3. propose a small plan
4. avoid broad implementation
