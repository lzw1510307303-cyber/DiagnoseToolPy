# Bugfix Rule

For bug fixes, avoid oversized OpenSpec changes unless architecture or behavior changes.

## Required Bugfix Notes

1. Symptom
2. Reproduction
3. Root cause
4. Affected files
5. Fix approach
6. Regression tests
7. Risk assessment

## Rules

- Do not perform unrelated refactoring.
- Do not change storage contract unless required.
- Add a regression test.
- Update current-state.md if the bug affects known project behavior.
