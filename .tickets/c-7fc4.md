---
id: c-7fc4
status: open
deps: [c-f20d, c-9877]
links: []
created: 2026-01-14T15:59:29Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement confl page create command

Implement the 'confl page create' command that creates a new page.

## Tasks
- Add 'confl page create' command to page command group
- Require --space flag (space key, e.g., DEV)
- Require --title flag for page title
- Accept content via --body (inline), --body-file (from file), or stdin
- Support --parent flag for parent page ID (optional)
- Support --raw flag to provide storage format directly
- Default: convert Markdown to storage format
- Use ConfluenceClient.create_page() method
- Output created page ID and URL on success

## Acceptance Criteria
- 'confl page create --space DEV --title "My Page" --body "Content"' creates page
- 'cat file.md | confl page create --space DEV --title "My Page"' works
- '--raw' flag accepts storage format without conversion
- Returns new page ID and success message
- Error handling for validation failures

## References
- docs/architecture/page-commands.md — page create spec
- docs/architecture/cli-design.md — command patterns
- docs/architecture/content-formats.md — input formats

## Notes
- Depends on Markdown conversion capability (or start with --raw only)
- Space key needs to be converted to space ID via API

