# Coding Style

## Python

- Use Python 3.11+.
- Use `pathlib.Path` for file paths.
- Use dataclasses or Pydantic for structured models.
- Keep API routes thin.
- Keep analyzer logic independent from FastAPI.
- Keep retrieval logic independent from FastAPI.
- Use explicit error handling.
- Handle unknown file encodings safely.

## Comments

- Code identifiers should be English.
- Comments may be Chinese for domain-specific logic.

## Large File Rules

- Do not call `read()` on full log files.
- Process line by line.
- Store bounded samples only.
- Flush progress periodically.
- Avoid storing full matching logs in memory.

## Error Handling

- Preserve raw data when parsing fails.
- Return safe error messages to UI.
- Log technical details locally if logging is available.
