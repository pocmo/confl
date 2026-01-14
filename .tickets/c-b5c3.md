---
id: c-b5c3
status: open
deps: []
links: []
created: 2026-01-14T22:07:08Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# DESIGN: Specify search command implementation approach

Design the 'search' CLI entity for content discovery using CQL (Confluence Query Language). Need to determine: 1) API v2 search endpoint availability (may need v1 fallback), 2) CQL syntax support vs simple flags, 3) Output format and fields. Reference: docs/architecture/cli-subcommands.md Phase 2. Proposed: confl search <query>, confl search --text 'keyword', confl search --space <key> --type page --label <label>. Document decision in ticket notes, file implementation ticket after design.

