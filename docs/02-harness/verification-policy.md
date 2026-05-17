# Verification Policy

Every change must define verification.

## Required Verification Types

### Parser / Analyzer

- Unit tests with fixtures
- Edge cases
- Invalid input cases
- Streaming behavior where practical
- Encoding error handling

### File Storage

- Verify generated file names
- Verify YAML fields
- Verify Markdown content sections
- Verify index rebuild

### API

- Verify success response
- Verify invalid path response
- Verify missing input response
- Verify safe error message

### Retrieval

- Verify keyword match
- Verify rule match
- Verify disabled embedding behavior
- Verify ranking behavior

### UI

- Provide manual verification steps.
- Keep UI flows simple for MVP.

## Forbidden

Do not mark a task complete without tests or a manual verification checklist.
