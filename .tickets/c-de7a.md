---
id: c-de7a
status: closed
deps: []
links: []
created: 2026-01-14T21:59:01Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Document layout flattening behavior

Add documentation explaining that multi-column layouts are flattened to sequential content in markdown conversion.

Content to add to docs/architecture/content-rendering.md or similar:

## Layout Handling

Confluence storage format supports complex multi-column layouts (ac:layout, ac:layout-section, ac:layout-cell):
- fixed-width sections
- two-column layouts (two_left, two_right)
- three-column layouts (three_equal)
- breakout modes (wide, full-width)

Current behavior:
- All layout content is preserved
- Column structure is flattened to sequential (top-to-bottom) content
- Layout metadata (breakoutWidth, breakoutMode) is ignored

Rationale:
- Markdown has no native column support
- Plain text representation must be linear
- Content preservation is prioritized over presentation

Future consideration: Could preserve as HTML or use markdown extensions for advanced viewers.

Found in: tests/fixtures/pages/advanced-formatting.xml


## Notes

**2026-01-15T07:41:06Z**

Completed: Added comprehensive layout handling documentation to content-rendering.md explaining how multi-column layouts are flattened to sequential content during markdown conversion
