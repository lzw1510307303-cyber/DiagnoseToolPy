## Context

DiagnoseToolPy is a Python-based diagnostic tool using FastAPI. Currently deployed by installing dependencies and running `uvicorn`. Docker deployment would provide:
- Consistent environment across development and production
- Simple dependency management (no Python environment setup)
- Volume-based data persistence
- Easy cleanup (docker down removes everything)

## Goals / Non-Goals

**Goals:**
- Single Dockerfile building the Python application
- docker-compose.yml with volume mounts matching deployment guide
- Input directories read-only, output/cases/indexes/runtime read-write
- Environment-based configuration via DIAGNOSE_CONFIG
- Deployment verification steps

**Non-Goals:**
- No external database containers (MySQL, PostgreSQL, Redis, etc.)
- No authentication layer
- No Kubernetes deployment
- No multi-service architecture (single container)

## Decisions

### Python base image

**Decision**: Use `python:3.12-slim` as base image.

**Rationale**: Slim image keeps size small (~150MB vs ~900MB for full). Python 3.12 matches project's requires-python. Alpine was considered but can cause compatibility issues with some Python packages.

**Alternatives**:
- `python:3.12` (full): Larger image, not needed
- `python:3.12-alpine`: Potential C extension compatibility issues

### Multi-stage Dockerfile

**Decision**: Use multi-stage build with requirements installation separate from application code.

**Rationale**: Caching layer for dependencies. Only rebuilds requirements when pyproject.toml changes, not on every code change.

**Alternatives**:
- Single-stage: Every code change triggers full dependency reinstall

### Non-root user in container

**Decision**: Create and use a non-root user (diagnose) in the container.

**Rationale**: Running as root in containers is a security risk. The user needs write access to mounted volumes.

**Alternatives**:
- Run as root: Security risk, UID mismatch with host files

### Volume mount strategy

**Decision**:
- `/data/diagnose/input` - read-only (`:ro`)
- `/data/diagnose/output`, `/data/diagnose/cases`, `/data/diagnose/indexes`, `/data/diagnose/runtime` - read-write (`:rw`)
- `./config:/app/config:ro` - config directory read-only

**Rationale**: Input directories should not be modified by the application per security policy. Output and data directories need write access.

**Alternatives**:
- All read-write: Security risk for input logs
- All read-only: Application cannot persist results

### Restart policy

**Decision**: `restart: unless-stopped` in docker-compose.

**Rationale**: Container should restart automatically after server reboot or crash. `unless-stopped` allows manual stopping without auto-restart.

**Alternatives**:
- `always`: Overrides manual stops
- `no`: No auto-restart

## Risks / Trade-offs

[Risk] UID/GID mismatch between container user and host files → [Mitigation] Use numeric UID in Dockerfile USER directive, document required host permissions

[Risk] Large log files on mounted volumes → [Mitigation] No file size limits in container, rely on existing sampling logic

[Risk] Config file changes require container restart → [Mitigation] Config mounted read-only, volume change detection not needed

## Open Questions

- Should we support GPU access for any future ML features? (Not needed now, defer)
- Should we expose health check endpoint? (FastAPI already has /health, docker HEALTHCHECK can use it)
