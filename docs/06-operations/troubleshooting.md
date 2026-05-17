# Troubleshooting

## Web Page Cannot Open

Check:

```bash
docker ps
docker logs diagnose-tool
```

Verify port:

```text
18080
```

## Directory Is Rejected

Check:

- path exists
- path is readable
- path is under configured input roots
- Docker volume mount includes the path

## Logs Not Found

Check supported extensions:

- `.log`
- `.txt`
- `.out`
- `.err`
- `.gz`

## Analysis Is Slow

Check:

- file size
- disk I/O
- too many files
- deep nested directories
- rule complexity

## Empty Report

Check:

- files are readable
- encoding is supported
- log start pattern matches
- rules are loaded

## Case Not Searchable

Run case index rebuild.

Check:

- case has `metadata.yaml`
- case has `case.md`
- status is not deprecated
