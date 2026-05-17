# Project Skeleton Specification

## Purpose

Define the initial runnable DiagnoseToolPy project skeleton, including the FastAPI entry point, file-based YAML configuration, and core server directory whitelist validation.

## Requirements

### Requirement: Runnable FastAPI Skeleton
The system MUST provide an initial runnable FastAPI application as the DiagnoseToolPy web entry point without requiring a database or external infrastructure service.

#### Scenario: Health check succeeds
- **WHEN** the FastAPI application is started and the health endpoint is requested
- **THEN** the system returns a successful response indicating the application is healthy

#### Scenario: Index page renders
- **WHEN** the root index page is requested
- **THEN** the system returns a simple HTML page identifying DiagnoseToolPy as the diagnostic assistant

### Requirement: Planned Project Structure
The system MUST include the planned package, configuration, data, and test directories needed for future DiagnoseToolPy capabilities.

#### Scenario: Skeleton directories exist
- **WHEN** the project skeleton change is implemented
- **THEN** the documented `diagnose_tool`, `config`, `data`, and `tests` structure exists with module boundaries preserved

### Requirement: File-Based YAML Configuration
The system MUST load runtime application settings from `config/app.yaml` using a core configuration module.

#### Scenario: Valid config loads
- **WHEN** a valid YAML config file is loaded
- **THEN** the system returns the configured application settings and server directory whitelist roots

#### Scenario: Malformed config is rejected
- **WHEN** the YAML config file is malformed
- **THEN** the system fails with a clear configuration loading error instead of silently using unsafe defaults

### Requirement: Server Directory Whitelist Validation
The system MUST validate server-side directory paths against configured whitelist roots before future directory scanning uses them.

#### Scenario: Allowed directory is accepted
- **WHEN** a requested directory resolves inside a configured whitelist root
- **THEN** the validator accepts the path

#### Scenario: Outside directory is rejected
- **WHEN** a requested directory resolves outside all configured whitelist roots
- **THEN** the validator rejects the path

#### Scenario: Traversal attempt is rejected
- **WHEN** a requested path uses traversal segments to escape a configured whitelist root
- **THEN** the validator rejects the path after resolving it

#### Scenario: Sibling-prefix path is rejected
- **WHEN** a requested path only matches an allowed root by string prefix but is not contained by that root
- **THEN** the validator rejects the path

### Requirement: Implementation State Is Documented
The system MUST update the project continuity snapshot after the skeleton implementation is complete.

#### Scenario: Current state reflects skeleton completion
- **WHEN** the implementation tasks for this change are completed
- **THEN** `docs/00-project/current-state.md` records the created package structure, FastAPI app, config loading, and whitelist validation status
