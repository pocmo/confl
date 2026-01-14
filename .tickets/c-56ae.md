---
id: c-56ae
status: closed
deps: []
links: []
created: 2026-01-14T22:31:30Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Add API v1 client support to ConfluenceClient

Extend client.py to support both v2 and v1 endpoints. Add create_v1_client() function that uses /wiki/rest/api base URL. Use same Basic auth. Needed for search command which requires v1 API. Reference: c-b5c3 design.


## Notes

**2026-01-14T22:34:32Z**

Completed: Added create_v1_client() and get_v1_client() functions to client.py. Both use /wiki/rest/api base URL with same Basic auth. Added comprehensive tests. All 396 tests pass.
