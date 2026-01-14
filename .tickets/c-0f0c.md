---
id: c-0f0c
status: open
deps: []
links: []
created: 2026-01-14T22:06:55Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Implement 'comment' subcommand for collaboration

Implement the 'comment' CLI entity with commands: list, get, add, update, delete. Enables review workflows and feedback automation. Reference: docs/architecture/cli-subcommands.md Phase 2. Commands: confl comment list --page <id>, confl comment get <id>, confl comment add --page <id> --body TEXT, confl comment update <id> --body TEXT, confl comment delete <id>. Support both footer and inline comments, Markdown input for body, show comment thread hierarchy.

