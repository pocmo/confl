# Page Commands

The `page` entity is the core of `confl`.

## Commands

| Command | Description | Priority |
|---------|-------------|----------|
| `confl page get <ref>` | Fetch and display a single page | P0 |
| `confl page list --space KEY` | List pages in a space | P0 |
| `confl page create` | Create a new page | P0 |
| `confl page update <ref>` | Update page content | P0 |
| `confl page delete <ref>` | Delete a page | P1 |
| `confl page tree --space KEY` | Show page hierarchy as tree | P2 |

## Page Reference

Pages can be referenced by:

- **ID** — `confl page get 12345678` (for automation)
- **URL** — `confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678/Title"` (user-friendly)

Future: lookup by title + space.

## Output

Default output includes metadata header + content:

```
Title: Release Notes v2.0
Space: DEV
Author: jane@company.com
Updated: 2025-01-10
---
# Release Notes

Content as Markdown...
```

Flags:
- `--body-only` — suppress metadata header
- `--json` — full API response
- `--markdown` — raw Markdown without Rich formatting
- `--raw` — Confluence storage format (XHTML)

## Input

For `create` and `update`:

- Content via `--body` flag (inline) or `--body-file` (from file)
- Stdin supported: `cat content.md | confl page update 12345`
- Default format: Markdown (converted to storage format)
- `--raw` flag to provide storage format directly
