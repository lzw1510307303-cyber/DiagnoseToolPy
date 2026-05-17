# Retrieval Query Template

`retrieval-query.json` is generated from analysis results.

Example:

```json
{
  "task_id": "task-20260516-100103",
  "summary": "Redis连接池耗尽，伴随Closed by interrupt和任务超时",
  "components": ["Redis", "Jedis", "ThreadPool"],
  "fault_modes": ["connection_pool_exhausted", "timeout", "thread_interrupt"],
  "exception_classes": [
    "JedisConnectionException",
    "SocketTimeoutException"
  ],
  "keywords": [
    "Could not get a resource from the pool",
    "Closed by interrupt",
    "RedisInputStream.ensureFill",
    "task timeout"
  ],
  "stack_symbols": [
    "redis.clients.jedis.util.RedisInputStream.ensureFill"
  ],
  "log_templates": [
    "Could not get a resource from the pool",
    "Closed by interrupt"
  ]
}
```

## Extraction Sources

- category classification
- exception classes
- log templates
- key phrases
- stack symbols
- component tags
- fault modes

## Rule

Do not include full raw logs in the retrieval query.
