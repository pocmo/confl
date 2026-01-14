---
id: c-f20d
status: closed
deps: []
links: []
created: 2026-01-14T15:58:55Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement API client create_page method

Add create_page() method to ConfluenceClient that creates a new Confluence page.

## Tasks
- Add create_page(space_id: str, title: str, body: str, parent_id: str | None = None) method
- Use POST /wiki/api/v2/pages endpoint
- Accept body in storage format
- Support optional parent_id for page hierarchy
- Return created page data (including new page ID)
- Handle validation errors (duplicate title, invalid space, etc.)
- Add type hints

## Acceptance Criteria
- Method creates page and returns page data with new ID
- Parent page support works when parent_id provided
- Tests use pytest-httpx to mock API responses
- Error cases handled with clear exceptions

## References
- docs/architecture/page-commands.md — page create command
- https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post — API endpoint docs

## Notes
- This takes storage format as input, not Markdown
- Markdown conversion happens at CLI layer


**2026-01-14T16:50:24Z**

Completed: Implemented create_page() method in ConfluenceClient with full support for space_id, title, body (storage format), and optional parent_id. Added 7 comprehensive tests covering success cases, parent hierarchy, and error cases (invalid space, duplicate title, unauthorized, forbidden, invalid parent). All 204 tests pass with 96.28% coverage.
