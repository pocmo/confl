---
id: c-b3bd
status: open
deps: []
links: []
created: 2026-01-14T15:59:14Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement API client delete_page method

Add delete_page() method to ConfluenceClient that deletes a page.

## Tasks
- Add delete_page(page_id: str) method
- Use DELETE /wiki/api/v2/pages/{id} endpoint
- Handle 404 gracefully (page already deleted or doesn't exist)
- Return success confirmation or None
- Add type hints

## Acceptance Criteria
- Method deletes page successfully
- 404 errors handled appropriately
- Tests use pytest-httpx to mock API responses

## References
- docs/architecture/page-commands.md — page delete command
- https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-delete — API endpoint docs

## Notes
- Deletion in Confluence may be soft delete (moved to trash)

