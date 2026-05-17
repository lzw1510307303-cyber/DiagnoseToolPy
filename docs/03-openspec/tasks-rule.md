# Tasks Rule

Tasks must be small and verifiable.

## Task Format

```markdown
- [ ] Task name
  - Files:
  - Behavior:
  - Tests:
  - Verification:
```

## Rules

- Do not combine unrelated modules in one task.
- Do not add broad refactoring tasks.
- Every implementation task must include tests or manual verification.
- Docs must be updated when behavior or storage contract changes.
- `docs/00-project/current-state.md` must be updated at the end.

## Good Task Example

```markdown
- [ ] Implement path whitelist validation
  - Files: diagnose_tool/core/security.py, tests/test_security.py
  - Behavior: reject paths outside configured input roots
  - Tests: valid path, invalid path, traversal attempt
  - Verification: uv run pytest tests/test_security.py
```
