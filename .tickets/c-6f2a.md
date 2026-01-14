---
id: c-6f2a
status: closed
deps: [c-b3bd]
links: []
created: 2026-01-14T15:59:44Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement confl page delete command

Implement the 'confl page delete' command that deletes a page.

## Tasks
- Add 'confl page delete <page_id>' command to page command group
- Accept page ID or URL as argument
- Use ConfluenceClient.delete_page() method
- Output success message on deletion
- Handle already-deleted pages gracefully

## Acceptance Criteria
- 'confl page delete <id>' deletes page
- 'confl page delete <url>' extracts ID and works
- Success message displayed
- 404/already deleted handled gracefully
- Error handling for auth failures

## References
- docs/architecture/page-commands.md — page delete spec
- docs/architecture/cli-design.md — command patterns

## Notes
- Simple command, no complex logic needed


**2026-01-14T16:43:38Z**

Completed: Implemented page delete command with ID/URL support, JSON output, graceful 404 handling, and comprehensive tests (7 test cases covering success, errors, and edge cases)
