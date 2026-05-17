# Spec Rule

Specs must describe observable behavior.

Use requirement words:

- MUST
- MUST NOT
- SHOULD
- MAY

## Required Scenario Format

### Scenario: Name

Given ...
When ...
Then ...

## Required Failure Scenarios

For each feature, include at least one failure scenario.

Examples:

- invalid directory
- unsupported file type
- malformed YAML
- parsing failure
- empty casebase
- embedding disabled
- missing task artifact
- malformed case metadata

## Storage Requirements

If the feature writes files, specify:

- file name
- path
- required fields
- overwrite behavior
- rebuild behavior if applicable
