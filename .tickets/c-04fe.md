---
id: c-04fe
status: open
deps: []
links: []
created: 2026-01-14T20:30:16Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement user-friendly error formatting for API errors

Replace raw JSON error dumps with formatted, human-readable error messages.

## Tasks
- Create error handling module or utilities for formatting API errors
- Parse Confluence API error responses (status, code, title, detail fields)
- Display errors using Rich for nice terminal formatting
- Show: error code, title, and detail message (not raw JSON dump)
- Handle common error types: 400 (bad request), 401 (unauthorized), 404 (not found), etc.
- Preserve --json flag behavior (show raw JSON when requested)
- Apply error formatting across all commands (page get, list, etc.)
- Ensure errors go to stderr (not stdout)

## Acceptance Criteria
- API errors display as formatted messages, not JSON dumps
- Error output is clear and actionable for users
- --json flag still outputs raw error JSON
- Errors go to stderr
- Exit codes follow CLI design (1 for API errors, 2 for usage errors)

## References
- docs/architecture/cli-design.md — error handling and exit codes
- docs/architecture/design-principles.md — human-readable output

## Notes
- Should catch errors at CLI command level or in HTTP client
- Can use Rich Console.print() with [red] styling for errors
- Example: 'Error: Page not found (404)' instead of full JSON response

