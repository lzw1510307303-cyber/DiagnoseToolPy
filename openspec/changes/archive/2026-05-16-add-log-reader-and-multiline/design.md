## Context

DiagnoseToolPy currently has a runnable app, secure server directory scanning, and metadata-only file discovery. The next analyzer step is reading selected log files safely and turning raw physical lines into multiline event candidates before later header parsing and classification.

The implementation must stay inside the analyzer module, stream line by line, support normal text and `.gz` logs, tolerate uncertain encodings, preserve raw text, and avoid parsing complex headers in this change.

## Goals / Non-Goals

**Goals:**

- Add streaming text log reading in `diagnose_tool/analyzer/reader.py`.
- Add streaming gzip log reading for `.gz` files.
- Preserve file path, line number, and raw line text for each yielded line.
- Handle encoding uncertainty with `errors="replace"` behavior.
- Add multiline merging in `diagnose_tool/analyzer/multiline.py` for Java stack traces and continuation lines.
- Preserve all raw stack trace content in merged event candidates.
- Add small fixture-based tests for reader and multiline behavior.
- Update `docs/00-project/current-state.md` after implementation.

**Non-Goals:**

- Do not parse complex log headers.
- Do not classify exceptions or categories.
- Do not generate `evidence-pack.md`, reports, timelines, case drafts, or retrieval queries.
- Do not implement casebase, retrieval, AI integration, or database-backed storage.
- Do not add browser upload behavior.

## Decisions

### Streaming Reader Module

`diagnose_tool/analyzer/reader.py` will expose iterator-style functions that yield structured line records. The implementation will use `for line in file` for normal files and gzip text mode for `.gz` files, with UTF-8 plus replacement errors as the default safe behavior.

Alternative considered: reading file contents into a list before processing. This is rejected because large logs must be streamed and full-file reads are forbidden.

### Gzip Support Without Decompression To Disk

`.gz` files will be streamed through `gzip.open(..., mode="rt", encoding="utf-8", errors="replace")` or an equivalent line iterator. This avoids temporary files and keeps memory bounded.

Alternative considered: decompressing the full archive before reading. This is rejected because it can duplicate large logs on disk and encourages non-streaming behavior.

### Structured Raw Line Records

Reader output should include at least `file_path`, `line_no`, and `raw`. This gives later parser work enough context without introducing parse status or parsed fields too early.

Alternative considered: returning plain strings only. This is rejected because line numbers and file paths are required for evidence and diagnostics later.

### Multiline Event Candidate Merger

`diagnose_tool/analyzer/multiline.py` will merge physical lines into event candidates. A new event starts when a line looks like a log start, such as a timestamp at the beginning of the line. Continuation lines, Java stack frames, `Caused by:`, `Suppressed:`, and similar stack trace lines are appended to the current event. If continuation-like or malformed lines appear before any event, they are preserved as raw event candidates rather than discarded.

Alternative considered: waiting until the complex header parser exists before multiline merging. This is rejected because stack trace merging is a separate prerequisite and can use conservative start-line detection.

### No Durable Output Files

This change returns/yields in-memory stream records and event candidates only. It does not write analysis task outputs.

Alternative considered: writing merged event candidates to `data/output`. This is rejected because task state and evidence generation are later changes.

## Data Flow

1. Caller selects a scanned log file path from a validated server directory workflow.
2. Reader opens the file in text or gzip streaming mode.
3. Reader yields line records one at a time with raw text and source location.
4. Multiline merger consumes the line iterator.
5. Merger emits event candidates containing start/end line numbers and raw merged text.
6. Future parser/classifier work consumes event candidates.

## Module Responsibilities

- `diagnose_tool/analyzer/reader.py`: stream normal and gzip logs, preserve raw lines, handle encoding replacement.
- `diagnose_tool/analyzer/multiline.py`: merge physical line records into raw event candidates.
- `tests/test_reader.py`: verify text, gzip, and encoding behavior using small fixtures.
- `tests/test_multiline.py`: verify Java stack trace grouping, continuation preservation, and malformed line handling.
- `tests/fixtures/`: store small fixture logs only.

## File Outputs

This change does not write durable output files. It does not create or modify `task.yaml`, `progress.json`, `evidence-pack.md`, `key-logs.txt`, `case-draft.md`, `case-metadata-draft.yaml`, or `retrieval-query.json`.

## Error Handling

- Invalid file paths should fail with normal file I/O errors unless callers validate earlier.
- Encoding errors should not abort reading; undecodable bytes should be replaced.
- Malformed lines should be preserved in raw event candidates.
- Empty files should produce no line records and no merged events.

## Security Considerations

This analyzer code does not perform path whitelist validation directly; callers must use existing source path validation before selecting files. The reader must not make network calls or access paths beyond the explicit file path it is given.

## Memory Behavior

Reader functions must stream line by line and MUST NOT call full-file `read()` or `readlines()`. The multiline merger may hold only the current event candidate while iterating. It must not accumulate all events before yielding them.

## Tests

- Text reader yields line records with file path, line numbers, and raw text.
- Gzip reader yields line records without decompressing to disk.
- Reader replaces invalid bytes instead of raising decode errors.
- Multiline merger groups Java exception stack frames with the preceding log event.
- Multiline merger preserves `Caused by:` and stack frame lines.
- Multiline merger preserves malformed or continuation lines that appear before a recognized start line.
- Empty input produces no merged events.

## Compatibility

This adds analyzer primitives consumed by later parser and classifier changes. It does not change existing API behavior or persisted storage contracts.

## Risks / Trade-offs

- [Risk] Conservative log-start detection may merge some uncommon formats incorrectly. -> Mitigation: keep raw text preserved and add parser-specific refinements in the later header parser change.
- [Risk] Long stack traces create large current-event buffers. -> Mitigation: only the current event is buffered; later sample limits can bound retained analyzer output.
- [Risk] Gzip decoding may encounter unusual encodings. -> Mitigation: use replacement error handling and preserve raw decoded text as safely as possible.

## Migration Plan

No data migration is required. Rollback is removing `reader.py`, `multiline.py`, associated fixtures/tests, and the current-state update.

## Open Questions

None.
