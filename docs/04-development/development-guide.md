# Development Guide

## Recommended Implementation Order

1. Project skeleton
2. Config loading
3. Path whitelist validation
4. Directory scan API
5. File-based task state
6. Streaming reader
7. Multiline merger
8. Header parser
9. Rule classifier
10. Evidence package generator
11. Report generator
12. Case draft generator
13. Manual case creation
14. Case index rebuild
15. Basic retrieval
16. Docker deployment

## Change Size

Prefer small changes.

A change should usually affect one major module.

## Completion Criteria

A change is complete only when:

- Code is implemented.
- Tests are added.
- Output file contracts are respected.
- Relevant docs are updated.
- `docs/00-project/current-state.md` is updated.

## MVP Done Criteria

The MVP is done when this flow works:

```text
select server directory
→ scan logs
→ create analysis task
→ generate evidence-pack
→ generate report
→ generate case draft
→ archive case
→ retrieve case by keyword
```
