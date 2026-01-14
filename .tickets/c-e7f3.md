---
id: c-e7f3
status: closed
deps: [c-60b9, c-b143]
links: []
created: 2026-01-14T15:59:38Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement confl page update command

Implement the 'confl page update' command that updates an existing page.

## Tasks
- Add 'confl page update <page_id>' command to page command group
- Accept page ID or URL as argument
- Accept content via --body (inline), --body-file (from file), or stdin
- Support --title flag to update title (optional, keep existing if not provided)
- Support --raw flag to provide storage format directly
- Default: convert Markdown to storage format
- Fetch current page version automatically
- Use ConfluenceClient.update_page() method
- Handle version conflicts with clear error messages

## Acceptance Criteria
- 'confl page update <id> --body "New content"' updates page
- 'cat file.md | confl page update <id>' works
- '--title' updates page title
- Version conflicts are detected and reported clearly
- Error handling for not found, auth failures

## References
- docs/architecture/page-commands.md — page update spec
- docs/architecture/cli-design.md — command patterns
- docs/architecture/content-formats.md — input formats

## Notes
- Must fetch current version before updating (optimistic locking)
- Depends on Markdown conversion capability (or start with --raw only)


**2026-01-14T16:47:52Z**

Completed: Implemented 'confl page update' command with full markdown conversion support, stdin/file/inline content input, optional title updates, version conflict handling, and comprehensive test coverage (15 tests).
