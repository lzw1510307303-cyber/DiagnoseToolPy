# Log Reader And Multiline Specification

## Purpose

Define streaming text/gzip log reading and multiline Java stack trace event candidate merging for DiagnoseToolPy analyzer workflows.

## Requirements

### Requirement: Streaming Text Log Reader
The system MUST provide a text log reader that streams normal log files line by line and preserves source metadata for every yielded line.

#### Scenario: Text log lines are streamed
- **WHEN** a caller reads a normal text log file
- **THEN** the reader yields line records one at a time with file path, line number, and raw text

#### Scenario: Empty text log produces no records
- **WHEN** a caller reads an empty normal text log file
- **THEN** the reader yields no line records

### Requirement: Streaming Gzip Log Reader
The system MUST provide a gzip log reader that streams `.gz` log files line by line without decompressing the full file to memory or disk.

#### Scenario: Gzip log lines are streamed
- **WHEN** a caller reads a `.gz` log file
- **THEN** the reader yields line records one at a time with file path, line number, and raw text

### Requirement: Encoding-Safe Reading
The system MUST handle uncertain log encodings safely by replacing undecodable bytes instead of failing or discarding log lines.

#### Scenario: Invalid bytes are preserved with replacement
- **WHEN** a log file contains bytes that are invalid for the configured encoding
- **THEN** the reader yields raw text containing replacement characters and continues reading subsequent lines

### Requirement: Multiline Event Candidate Merging
The system MUST merge Java stack trace and continuation lines into a single raw log event candidate while preserving source line boundaries.

#### Scenario: Java stack trace merges into previous event
- **WHEN** a log start line is followed by exception, stack frame, and `Caused by:` continuation lines
- **THEN** the merger emits one event candidate containing all raw stack trace text

#### Scenario: New log start flushes previous event
- **WHEN** a new log start line appears after a multiline event
- **THEN** the merger emits the previous event and starts a new event candidate

### Requirement: Malformed Lines Are Preserved
The system MUST NOT discard malformed or continuation-like lines that appear before a recognized log start line.

#### Scenario: Leading malformed line is emitted
- **WHEN** the input starts with a line that does not match the log start pattern
- **THEN** the merger preserves it in a raw event candidate instead of discarding it

### Requirement: Streaming-Safe Multiline Behavior
The system MUST merge multiline events while buffering only the current event candidate and MUST NOT require all input lines in memory.

#### Scenario: Events are yielded during iteration
- **WHEN** the merger consumes a stream of line records containing multiple events
- **THEN** it yields completed event candidates as it advances through the iterator

### Requirement: Implementation State Is Documented
The system MUST update the project continuity snapshot after streaming reader and multiline merging are implemented.

#### Scenario: Current state reflects reader and multiline completion
- **WHEN** implementation tasks for this change are completed
- **THEN** `docs/00-project/current-state.md` marks streaming log reader and multiline stack trace merger as implemented while leaving parser, classifier, evidence, casebase, retrieval, and deployment work incomplete
