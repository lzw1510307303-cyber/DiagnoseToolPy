# Deployment Guide

## Target Deployment

Linux server with Docker or Python runtime.

Recommended:

```text
Docker Compose
```

## Required Directories

```bash
mkdir -p /data/diagnose/input
mkdir -p /data/diagnose/output
mkdir -p /data/diagnose/cases
mkdir -p /data/diagnose/indexes
mkdir -p /data/diagnose/runtime
```

## Docker Deployment

### Build the Image

```bash
docker build -t diagnose-tool .
```

### Start the Application

```bash
docker compose up -d
```

### Stop the Application

```bash
docker compose down
```

### View Logs

```bash
docker compose logs -f
```

### Rebuild After Updates

```bash
docker compose up -d --build
```

## Access

Default port:

```text
18080
```

Open:

```text
http://SERVER_IP:18080
```

## Main Workflow

Users should place logs under:

```text
/data/diagnose/input/
```

Then select that directory in the Web UI.

## Deployment Verification

### 1. Verify Container is Running

```bash
docker compose ps
```

Expected output shows `diagnose-tool` with status `Up`.

### 2. Verify Health Endpoint

```bash
curl http://localhost:18080/health
```

Expected response: `{"status":"ok"}`

### 3. Verify Volume Mounts

Check that data directories are created:

```bash
ls -la /data/diagnose/
```

Input directory should be empty (read-only mount).
Output, cases, indexes, runtime should exist.

### 4. Verify Web UI

Open `http://SERVER_IP:18080` in a browser.
You should see the DiagnoseToolPy interface.

### 5. Verify Log Directory Access

From the Web UI, select `/data/diagnose/input` as the source directory.
You should be able to browse files in that directory.

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker compose logs
```

Common issues:
- Port 18080 already in use
- Config file missing at `./config/app.yaml`

### Permission Issues

If you see permission denied errors, ensure the host directories have appropriate permissions:

```bash
chmod 755 /data/diagnose/output
chmod 755 /data/diagnose/cases
chmod 755 /data/diagnose/indexes
chmod 755 /data/diagnose/runtime
```

### Health Check Failing

If health check fails but container is running, check if uvicorn started correctly:

```bash
docker compose logs | grep uvicorn
```
