---
id: c-fe0c
status: open
deps: []
links: []
created: 2026-01-14T22:07:01Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Implement 'blogpost' subcommand for blog management

Implement the 'blogpost' CLI entity with commands: list, get, create, update, delete. Blog posts are time-ordered content similar to pages. Reference: docs/architecture/cli-subcommands.md Phase 2. Commands: confl blogpost list --space <key>, confl blogpost get <id>, confl blogpost create, confl blogpost update <id>, confl blogpost delete <id>. Reuse page rendering logic (same storage format), support attachments/labels/comments like pages.

