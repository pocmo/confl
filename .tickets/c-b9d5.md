---
id: c-b9d5
status: closed
deps: [c-b143]
links: []
created: 2026-01-14T15:58:38Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# Implement confl page get command

Implement the 'confl page get' command that fetches and displays a single page.

## Tasks
- Create src/confl/commands/page.py (or extend if exists)
- Add 'page' command group to CLI
- Implement 'confl page get <page_id>' command
- Accept page ID or URL as argument
- Display output with metadata header (Title, Space, Author, Updated) + content
- Support --body-only flag to suppress metadata header
- Support --json flag for full API response
- Support --markdown flag for raw markdown (when conversion ready)
- Support --raw flag for storage format output
- Use ConfluenceClient.get_page() method
- Follow CLI design patterns from auth commands

## Acceptance Criteria
- 'confl page get <id>' fetches and displays page
- 'confl page get <url>' extracts ID and works
- '--json' outputs full API response
- '--raw' outputs storage format
- Error handling for invalid IDs, auth failures, not found
- Output uses Rich for nice terminal formatting (default)

## References
- docs/architecture/page-commands.md — page get spec
- docs/architecture/cli-design.md — command patterns
- docs/architecture/content-formats.md — output formats

## Notes
- Markdown conversion not needed yet, can output storage format or basic rendering
- URL parsing should extract page ID from Confluence URLs


**2026-01-14T16:15:34Z**

Completed: Implemented 'confl page get' command with support for ID/URL references, multiple output formats (default/json/raw/markdown), and comprehensive error handling. Added 14 tests, all 86 tests pass with 96.53% coverage.
