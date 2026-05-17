# Log Analysis Rules

## Supported Categories

Initial categories:

- common
- jvm
- redis
- database
- kafka
- thread_pool
- http
- business
- unknown

## Rule File Format

Example:

```yaml
category: redis
display_name: Redis异常
severity: high
keywords:
  - JedisConnectionException
  - Could not get a resource from the pool
  - Read timed out
  - Closed by interrupt
  - Redis command timed out
```

## Classification Behavior

- A log event MAY match multiple rules in future versions.
- V0.1 MAY keep the first matched category for simplicity.
- Unknown events should not be discarded.
- Unknown events may be sampled under `unknown`.

## Sampling Rules

- Limit samples per category.
- Keep first N and optionally last N samples.
- Do not store all matched logs in memory.

## Timeline Rules

Timeline should aggregate by time bucket.

Suggested default:

```text
1 minute
```

## Output

Analyzer should generate:

- category counts
- severity counts
- key phrases
- first seen time
- last seen time
- bounded samples
- timeline
