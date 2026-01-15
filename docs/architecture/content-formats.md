---
Status: IMPLEMENTED
Date: 2025-12-01
Purpose: Document supported content output formats
---

# Content Formats

## Output Formats

How page content is displayed when reading.

| Format | Flag | Description | Priority |
|--------|------|-------------|----------|
| Rich terminal | (default) | Markdown rendered with Rich for nice shell output | P0 |
| Markdown | `--markdown` | Raw Markdown text | P0 |
| JSON | `--json` | Full API response for machine parsing | P1 |
| Storage format | `--raw` | Confluence's native XHTML storage format | P2 |
| Plain text | `--plain` | Stripped of all formatting | P2 |

## Input Formats

How page content is provided when creating/updating.

| Format | Flag | Description | Priority |
|--------|------|-------------|----------|
| Markdown | (default) | Write in Markdown, converted to storage format | P0 |
| Storage format | `--raw` | Provide Confluence's native XHTML directly | P1 |

## Notes

- Rich terminal output uses Markdown internally, rendered via Rich's Markdown support
- Markdown ↔ storage format conversion is a core capability we need to build or find a library for
