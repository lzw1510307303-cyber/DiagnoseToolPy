# Docker Compose Guide

## Quick Start

1. Create required directories on the host:

```bash
mkdir -p /data/diagnose/input
mkdir -p /data/diagnose/output
mkdir -p /data/diagnose/cases
mkdir -p /data/diagnose/indexes
mkdir -p /data/diagnose/runtime
```

2. Place log files in `/data/diagnose/input/` or mount your log directory to `/mnt/log-share`.

3. Start the application:

```bash
docker compose up -d
```

4. Access the web UI at `http://SERVER_IP:18080`

## Configuration

The `docker-compose.yml` provides a complete configuration:

```yaml
version: "3.8"

services:
  diagnose-tool:
    build: .
    container_name: diagnose-tool
    ports:
      - "18080:18080"
    volumes:
      - /data/diagnose/input:/data/diagnose/input:ro
      - /mnt/log-share:/mnt/log-share:ro
      - /data/diagnose/output:/data/diagnose/output:rw
      - /data/diagnose/cases:/data/diagnose/cases:rw
      - /data/diagnose/indexes:/data/diagnose/indexes:rw
      - /data/diagnose/runtime:/data/diagnose/runtime:rw
      - ./config:/app/config:ro
    environment:
      - DIAGNOSE_CONFIG=/app/config/app.yaml
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:18080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

## Mount Rules

### Input Directories (Read-Only)

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `/data/diagnose/input` | `/data/diagnose/input` | `:ro` | Primary log input directory |
| `/mnt/log-share` | `/mnt/log-share` | `:ro` | Optional secondary log source |

### Data Directories (Read-Write)

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `/data/diagnose/output` | `/data/diagnose/output` | `:rw` | Analysis output |
| `/data/diagnose/cases` | `/data/diagnose/cases` | `:rw` | Case knowledge base |
| `/data/diagnose/indexes` | `/data/diagnose/indexes` | `:rw` | Search indexes |
| `/data/diagnose/runtime` | `/data/diagnose/runtime` | `:rw` | Runtime state |

### Configuration (Read-Only)

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `./config` | `/app/config` | `:ro` | Application config |

## Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `DIAGNOSE_CONFIG` | `/app/config/app.yaml` | Path to config inside container |

## Customizing Volume Mounts

To use different host paths, modify the docker-compose.yml:

```yaml
volumes:
  - /your/input/path:/data/diagnose/input:ro
  - /your/output/path:/data/diagnose/output:rw
  # ... other volumes
```

## Health Check

The container includes a health check that verifies the `/health` endpoint is accessible. Docker will report the container as healthy when the check passes.

To manually verify:

```bash
curl http://localhost:18080/health
```

## Restart Policy

The `restart: unless-stopped` policy means:
- Container starts automatically on system boot
- Container restarts after crashes
- Container does NOT restart if you manually stop it (`docker compose down`)
