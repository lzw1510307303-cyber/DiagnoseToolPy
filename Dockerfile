FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -r pyproject.toml

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash diagnose

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY diagnose_tool ./diagnose_tool
COPY config ./config
COPY data ./data
COPY static ./static
COPY templates ./templates

USER diagnose

EXPOSE 18080

CMD ["uvicorn", "diagnose_tool.main:app", "--host", "0.0.0.0", "--port", "18080"]
