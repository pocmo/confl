---
id: c-bbbd
status: closed
deps: []
links: []
created: 2026-01-14T22:06:44Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement 'attachment' subcommand for file management

Implement the 'attachment' CLI entity with commands: list, get, download, upload, delete. Critical for documentation workflows (images, PDFs, etc.). Reference: docs/architecture/cli-subcommands.md Phase 1. Commands: confl attachment list --page <id>, confl attachment get <id>, confl attachment download <id> [--output FILE], confl attachment upload --page <id> --file PATH, confl attachment delete <id>. Use streaming for large files, show progress, detect MIME types.


## Notes

**2026-01-14T22:16:40Z**

Completed: Implemented full attachment subcommand with list, get, download, upload, delete commands. All 19 tests passing. Uses v2 API for list/get/delete, v1 API for upload (as v2 doesn't support it yet). Supports streaming downloads, MIME type detection, and page ID extraction from URLs.
