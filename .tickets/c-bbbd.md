---
id: c-bbbd
status: open
deps: []
links: []
created: 2026-01-14T22:06:44Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement 'attachment' subcommand for file management

Implement the 'attachment' CLI entity with commands: list, get, download, upload, delete. Critical for documentation workflows (images, PDFs, etc.). Reference: docs/architecture/cli-subcommands.md Phase 1. Commands: confl attachment list --page <id>, confl attachment get <id>, confl attachment download <id> [--output FILE], confl attachment upload --page <id> --file PATH, confl attachment delete <id>. Use streaming for large files, show progress, detect MIME types.

