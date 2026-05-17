# OpenSpec Usage Guide

## When to Use OpenSpec

Use OpenSpec for:

- new features
- architecture changes
- storage contract changes
- retrieval behavior changes
- casebase behavior changes
- deployment changes
- anything affecting multiple modules

## When Not to Use Full OpenSpec

For small bug fixes, a lightweight bugfix note is sufficient.

Still document:

- symptom
- root cause
- fix
- regression test

## Recommended Flow

### Explore

Use when unclear:

```text
/opsx:explore
```

### Propose

Use for planned changes:

```text
/opsx:propose
```

### Apply

Use after proposal is accepted:

```text
/opsx:apply
```

### Verify

Use after implementation if available:

```text
/opsx:verify
```

### Archive

Use after completion:

```text
/opsx:archive
```

## Standard Prompt Prefix

```text
Follow AGENTS.md and docs/README.md.
Use the DiagnoseToolPy harness standard.
Do not introduce mandatory databases.
Preserve file-system-as-source-of-truth.
Keep the change small and testable.
Update docs/00-project/current-state.md.
```
