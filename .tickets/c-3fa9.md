---
id: c-3fa9
status: open
deps: []
links: []
created: 2026-01-14T21:58:52Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Improve expand macro title rendering

Enhance expand macro (accordion) rendering to make section titles more prominent.

Current behavior: Expand macro content is rendered inline, title parameter may not be visible.

Desired behavior: Use markdown details/summary tags for collapsible sections:
<details>
<summary>Title from parameter</summary>
Content here
</details>

Benefits:
- Preserves section organization better
- Provides semantic structure
- Supported by many markdown renderers

Found in: tests/fixtures/pages/hub.xml and advanced-formatting.xml (FAQ sections, demo tips)

Implementation:
- Update convert_ac_structured_macro() for 'expand' macro
- Extract title parameter
- Wrap in details/summary tags
- Fall back to heading if no title parameter

