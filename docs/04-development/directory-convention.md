# Directory Convention

## Source Code

```text
diagnose_tool/
├── api/
├── core/
├── analyzer/
├── casebase/
├── retrieval/
├── exporter/
├── templates/
└── static/
```

## Config

```text
config/
├── app.yaml
├── rules/
└── case_templates/
```

## Runtime Data

```text
data/
├── input/
├── output/
├── cases/
├── indexes/
└── runtime/
```

## Tests

```text
tests/
├── fixtures/
├── test_scanner.py
├── test_header_parser.py
└── ...
```

## Naming

- task IDs: `task-YYYYMMDD-HHMMSS`
- case IDs: `CASE-YYYYMMDD-NNN`
- case directories: `{case_id}_{slug}`
- evidence file: `evidence-pack.md`
- metadata file: `metadata.yaml`
