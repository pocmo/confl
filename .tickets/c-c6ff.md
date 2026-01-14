---
id: c-c6ff
status: open
deps: []
links: []
created: 2026-01-14T22:06:50Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement 'label' subcommand for content tagging

Implement the 'label' CLI entity with commands: list, add, remove, search. Labels are used for organization and content discovery. Reference: docs/architecture/cli-subcommands.md Phase 1. Commands: confl label list --page <id>, confl label add --page <id> <label>..., confl label remove --page <id> <label>, confl label search <label>. Support multiple labels in single command. label search shows all content (pages, blogposts, attachments) with that label.

