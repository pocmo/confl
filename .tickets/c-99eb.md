---
id: c-99eb
status: closed
deps: []
links: []
created: 2026-01-15T06:34:06Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Enhance error messages with actionable suggestions

Improve error messages to include explanations and suggestions for common errors: missing config → suggest auth login, invalid page ID → explain format, rate limiting → suggest retry delay, 404 → check permissions. From cli-ux-improvements.md - H3


## Notes

**2026-01-15T06:54:50Z**

Completed: Enhanced error messages with actionable suggestions for:
- Authentication failures (401) - suggest auth login and API token URL
- Permission errors (403) - explain possible causes
- Not found errors (404) - suggest search command
- Version conflicts (409) - provide resolution steps
- Rate limiting (429) - suggest wait time and delays
- Configuration errors - provide examples and fix instructions
- Invalid page/blogpost references - show format examples
- File not found errors - show current directory and checklist

Added 14 comprehensive tests covering all error scenarios.
