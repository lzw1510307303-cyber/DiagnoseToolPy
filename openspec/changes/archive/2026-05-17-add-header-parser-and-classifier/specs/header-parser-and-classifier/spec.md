## ADDED Requirements

### Requirement: Complex Header Parser
The system MUST parse the supported log header format `时间 级别 [[服务内部模块]线程名] [类名信息] message` into structured fields without using naive bracket splitting.

#### Scenario: Full nested bracket header parses
- **WHEN** a log event starts with `2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] [com.demo.OrderService] query failed`
- **THEN** the parser returns timestamp, level, module, thread, logger, message, raw text, source location, and `parse_status` of `FULL`

#### Scenario: Bracket groups are scanned with balance
- **WHEN** the module/thread group contains nested brackets like `[[order-core]worker-1]`
- **THEN** the parser extracts the group using balanced bracket scanning rather than simple bracket splitting

### Requirement: Parse Status And Raw Preservation
The system MUST assign `FULL`, `PARTIAL`, or `RAW` parse status and preserve original raw content for every parsed event.

#### Scenario: Missing logger yields partial parse
- **WHEN** an event includes timestamp, level, and module/thread but no logger bracket group
- **THEN** the parser returns safely extracted fields, preserves raw text, and sets `parse_status` to `PARTIAL`

#### Scenario: Malformed line yields raw parse
- **WHEN** an event does not contain a recognizable timestamp and level
- **THEN** the parser returns a raw parsed record with original text and `parse_status` of `RAW`

#### Scenario: Incomplete bracket group preserves raw
- **WHEN** an event has an incomplete or unbalanced bracket group
- **THEN** the parser does not discard the event and preserves raw content with `PARTIAL` or `RAW` status

### Requirement: YAML Rule Loader
The system MUST load classification rules from local YAML files under `config/rules/` using a schema with category, display name, severity, and keywords.

#### Scenario: Valid rule file loads
- **WHEN** a rule YAML file contains required category, display name, severity, and keyword fields
- **THEN** the rule loader returns a usable classification rule

#### Scenario: Invalid rule file is rejected
- **WHEN** a rule YAML file is malformed or missing required fields
- **THEN** the rule loader raises a clear rule loading error

### Requirement: Rule-Based Classifier
The system MUST classify parsed or raw event text by matching configured rule keywords and MUST return an `unknown` classification when no rule matches.

#### Scenario: Keyword match returns category
- **WHEN** an event message or raw text contains a configured rule keyword
- **THEN** the classifier returns the matching category, display name, severity, and matched keyword

#### Scenario: No keyword match returns unknown
- **WHEN** no configured rule keyword matches the event message or raw text
- **THEN** the classifier returns an `unknown` classification without discarding the event

### Requirement: Analyzer Boundary Preservation
The parser and classifier MUST remain independent from FastAPI, AI providers, casebase, retrieval, and report generation.

#### Scenario: Parser and classifier are analyzer-only
- **WHEN** parser and classifier modules are implemented
- **THEN** they can be tested directly from `diagnose_tool/analyzer/` without importing FastAPI or writing output artifacts

### Requirement: Implementation State Is Documented
The system MUST update the project continuity snapshot after header parsing and rule classification are implemented.

#### Scenario: Current state reflects parser and classifier completion
- **WHEN** implementation tasks for this change are completed
- **THEN** `docs/00-project/current-state.md` marks complex log header parser and rule classifier as implemented while leaving evidence, casebase, retrieval, and deployment work incomplete
