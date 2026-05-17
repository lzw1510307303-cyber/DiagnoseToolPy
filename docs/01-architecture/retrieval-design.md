# Retrieval Design

## Goal

Each AI diagnosis prompt should include a small set of similar historical cases when available.

The retrieval system must work without embedding models.

## Retrieval Channels

Default channels:

1. Rule matching
2. Keyword matching
3. Exception class matching
4. Key phrase matching
5. Tag matching
6. Fault mode matching
7. BM25 search if dependency is available

Optional channel:

1. Vector search with LanceDB or FAISS

## Default Behavior

Embedding is disabled by default.

When embedding is disabled, retrieval still works through:

```text
metadata.yaml + case.md + index.jsonl + optional BM25
```

## Retrieval Query

Generated as:

```text
data/output/{task_id}/retrieval-query.json
```

Example:

```json
{
  "task_id": "task-20260516-100103",
  "summary": "Redis连接池耗尽，伴随Closed by interrupt和任务超时",
  "components": ["Redis", "Jedis", "ThreadPool"],
  "fault_modes": ["connection_pool_exhausted", "timeout", "thread_interrupt"],
  "exception_classes": ["JedisConnectionException", "SocketTimeoutException"],
  "keywords": [
    "Could not get a resource from the pool",
    "Closed by interrupt",
    "RedisInputStream.ensureFill"
  ],
  "stack_symbols": [
    "redis.clients.jedis.util.RedisInputStream.ensureFill"
  ]
}
```

## Ranking

Without embedding:

```text
final_score = keyword_score * 0.35
            + bm25_score * 0.35
            + rule_score * 0.30
```

With embedding enabled:

```text
final_score = keyword_score * 0.25
            + bm25_score * 0.25
            + rule_score * 0.20
            + vector_score * 0.30
```

## Prompt Context Rule

Historical cases are references only.

The prompt must state:

```text
The following cases are similar references only. Do not assume the current issue has the same root cause.
```
