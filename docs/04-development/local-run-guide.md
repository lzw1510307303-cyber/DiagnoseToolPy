# Local Run Guide

## Install Dependencies

```bash
uv add fastapi uvicorn pydantic pydantic-settings pyyaml jinja2 python-multipart
uv add rank-bm25
uv add --dev pytest pytest-cov ruff
```

## Run Development Server

```bash
uv run uvicorn diagnose_tool.main:app --host 0.0.0.0 --port 18080 --reload
```

Open:

```text
http://127.0.0.1:18080
```

## Run Tests

```bash
uv run pytest
```

## Run Lint

```bash
uv run ruff check .
```

## Local Data Directories

```bash
mkdir -p data/input data/output data/cases data/indexes data/runtime
```

## Example Input Directory

```text
data/input/demo-case/
├── app.log
├── error.log
└── gc.log
```
