# Security Policy

## Path Security

All user-provided paths must be validated against configured input roots.

Path traversal must be rejected.

## Input Mounts

Input directories should be mounted as read-only in Docker.

## Sensitive Directories

The system must not scan:

- `/etc`
- `/root`
- `/var/lib`
- user home directories outside allowlist
- database directories
- system directories

## Browser Upload

Browser upload is optional and only for small files.

Large files should use server-side directory scanning.

## AI Data Handling

When sending prompts to external AI services, users must understand that evidence may contain sensitive information.

For internal deployments, prefer local or approved model providers.
