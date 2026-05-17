## Why

DiagnoseToolPy currently has no containerized deployment option. Users deploying on servers need a simple way to run the application with proper directory isolation and configuration management. Docker Compose provides a clean, reproducible deployment model that matches the project's local-server-friendly philosophy.

## What Changes

- Add `Dockerfile` for building the application image
- Add `docker-compose.yml` with volume mounts and environment configuration
- Input log directories mounted read-only for security
- Output, cases, indexes, and runtime directories mounted read-write
- `DIAGNOSE_CONFIG` environment variable configured via docker-compose
- Startup commands documented for common workflows
- Deployment verification steps added to documentation
- `docs/00-project/current-state.md` updated to mark Docker deployment as implemented

## Capabilities

### New Capabilities

- `docker-deployment`: Containerized deployment using Docker Compose with proper volume mount隔离 and configuration

## Impact

- New files: `Dockerfile`, `docker-compose.yml`
- Updated docs: `docs/06-operations/deployment-guide.md`, `docs/06-operations/docker-compose-guide.md`
- No external database containers introduced
- No authentication layer added
- No Kubernetes manifests (future work)
