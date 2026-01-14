---
id: c-f6f4
status: open
deps: []
links: []
created: 2026-01-14T15:58:17Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# Implement API client list_pages method

Add list_pages() method to ConfluenceClient that lists pages, with optional space filtering.

## Tasks
- Add list_pages(space_key: str | None = None, limit: int = 25) method to ConfluenceClient
- Use GET /wiki/api/v2/pages endpoint
- Support space-key query parameter for filtering by space
- Support limit parameter for pagination control
- Return list of pages with basic metadata (id, title, space)
- Handle pagination (return first page of results for now)

## Acceptance Criteria
- Method returns list of page objects
- Space filtering works when space_key provided
- Tests use pytest-httpx to mock API responses
- Error cases handled appropriately

## References
- docs/architecture/page-commands.md — page list command
- https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-get — API endpoint docs

## Notes
- This is foundational for page list command
- Full pagination support can come later if needed

