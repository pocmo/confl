---
Status: IMPLEMENTED
Date: 2025-12-01
Purpose: Document entity-first CLI command structure
---

# CLI Design

## Entities

| Entity | Description |
|--------|-------------|
| `auth` | Manage authentication credentials |
| `page` | Read, create, update Confluence pages |
| `space` | List and inspect spaces |
| `search` | Find content by query |
| `attachment` | Upload and download files on pages |
| `comment` | Read and add comments on pages |

## Command Structure

Entity-first pattern:

```
confl <entity> <action> [options]
```

Examples:

```
confl page get <id>
confl page list --space KEY
confl page create --title "..." --space KEY
confl page update <id> --body-file content.md
```

## Principles

- Non-interactive by default — designed for scripting and agents
- Human-readable output by default (Rich), `--json` flag for machine parsing
- All input via arguments, options, or stdin — no prompts

See [Design Principles](design-principles.md) for detailed guidance.

## Error Handling

Exit codes:
| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (API error, invalid input) |
| `2` | Usage error (bad arguments, missing required options) |

Errors go to stderr. Human-readable by default, JSON when `--json` is used.
