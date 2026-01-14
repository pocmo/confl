---
id: c-2ee0
status: open
deps: []
links: []
created: 2026-01-14T16:03:37Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Implement storage_to_markdown() conversion function

Add storage format to Markdown converter using markdownify.

From docs/architecture/markdown-conversion.md research.

Tasks:
- Add markdownify>=0.11.0 dependency to pyproject.toml
- Add storage_to_markdown(storage: str) -> str to converter.py
- Create custom renderer for Confluence ac: tags
- Handle basic Confluence storage format elements
- Best-effort conversion with graceful degradation
- Add tests for common storage format patterns
- Document conversion limitations

