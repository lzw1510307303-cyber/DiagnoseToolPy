# Log Format Guide

## Primary Supported Format

```text
时间 级别 [[服务内部模块]线程名] [类名信息] message
```

Example:

```text
2026-05-16 10:01:01.123 ERROR [[order-core]worker-1] [com.demo.OrderService] query failed
```

## Why This Is Hard

The header contains nested brackets:

```text
[[order-core]worker-1]
```

Do not parse bracket fields using simple `split("[")` or `split("]")`.

## Parsing Strategy

1. Parse timestamp and level using regex.
2. Parse bracket groups using balanced bracket scanning.
3. Parse first bracket group as module/thread.
4. Parse second bracket group as logger.
5. Treat remaining content as message.
6. If parsing fails, preserve raw content.

## Expected Fields

- timestamp
- level
- module
- thread
- logger
- message
- raw
- file_path
- line_no
- parse_status

## Parse Status

- `FULL`: full parse succeeded
- `PARTIAL`: timestamp/level or some fields parsed
- `RAW`: preserve raw content only

## Multiline Stack Trace

Lines not matching a log start pattern should be appended to the previous event.

Example:

```text
2026-05-16 10:01:01 ERROR [[task]worker] [com.demo.Task] failed
java.lang.RuntimeException: failed
    at com.demo.A.method(A.java:10)
Caused by: java.io.IOException
    at com.demo.B.method(B.java:20)
```
