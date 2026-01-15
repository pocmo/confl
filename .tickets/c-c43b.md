---
id: c-c43b
status: open
deps: []
links: []
created: 2026-01-15T08:01:13Z
type: task
priority: 3
assignee: Sebastian Kaspari
---
# Clean up open-questions.md - archive resolved questions

The docs/open-questions.md file contains questions that have been resolved in implementation. Review and either:
1. Remove questions that are clearly answered by existing implementation
2. Convert to a docs/architecture/decisions.md or similar if historical context is valuable

Resolved questions include:
- Search: Uses CQL with simple filter options (implemented in search command)
- Space commands: list and get are implemented
- Pagination: Uses --limit in commands
- Page lookup: URLs are supported, titles via search
- Attachments: Upload from local file is supported
- Comments: Implemented with list/get/add/update/delete
- Content conversion: Using markdown conversion

Consider archiving if this historical context isn't valuable, or moving to architecture docs if it is.

