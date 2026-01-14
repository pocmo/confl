---
id: c-5fd3
status: open
deps: [c-f6f4]
links: []
created: 2026-01-14T15:58:47Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# Implement confl page list command

Implement the 'confl page list' command that lists pages, optionally filtered by space.

## Tasks
- Add 'confl page list' command to page command group
- Require --space flag for space filtering (e.g., --space DEV)
- Display table of pages with: ID, Title, Space, Updated date
- Support --json flag for machine-readable output
- Support --limit flag to control number of results
- Use ConfluenceClient.list_pages() method
- Use Rich tables for nice terminal output (default)

## Acceptance Criteria
- 'confl page list --space KEY' lists pages in that space
- Output is formatted as a table (Rich Table by default)
- '--json' outputs array of page objects
- Error handling for invalid space keys, auth failures

## References
- docs/architecture/page-commands.md — page list spec
- docs/architecture/cli-design.md — command patterns

## Notes
- Start with basic listing, pagination can be enhanced later if needed

