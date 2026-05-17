# Archive Rule

## Purpose

Archiving records completed design decisions and implementation outcomes.

## Archive Requirements

When archiving an OpenSpec change:

- Confirm tasks are complete.
- Confirm tests or manual verification were performed.
- Record deviations from original design.
- Update current-state.md.
- Update ADRs if architectural decisions changed.
- Preserve final storage contract changes.

## Do Not Archive If

- tests are missing
- output file contracts are unclear
- current-state.md is stale
- implementation deviated without explanation
