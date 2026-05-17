# Task Execution Policy

## Change Size

Prefer small changes.

A change should usually affect one major capability:

- project skeleton
- directory scanning
- analyzer core
- evidence generation
- casebase
- retrieval
- export
- deployment

## Implementation Sequence

1. Define behavior.
2. Identify affected files.
3. Add or update tests.
4. Implement.
5. Verify.
6. Update docs/current state.

## Coding Sequence

For new modules:

1. model definitions
2. pure logic
3. service function
4. API route
5. UI integration
6. tests
7. docs

## Output Contract

If a task writes files, it must document:

- file path
- file name
- required fields
- failure behavior
- whether the file is durable truth or rebuildable cache
