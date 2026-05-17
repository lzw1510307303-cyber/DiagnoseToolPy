# Server Directory Access

## Principle

Large logs should not be uploaded through the browser.

Users should place logs on the server using:

- SFTP
- SCP
- shared directory
- existing operational file transfer tools

Then select the server directory in the Web UI.

## Allowed Roots

Configure allowed roots:

```yaml
storage:
  input_roots:
    - /data/diagnose/input
    - /mnt/log-share
```

## Security Rule

The backend must reject paths outside configured roots.

Examples:

Allowed:

```text
/data/diagnose/input/DTS-001
/mnt/log-share/case-001
```

Rejected:

```text
/etc
/root
/var/lib/mysql
../../etc/passwd
```
