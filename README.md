# confl

An unofficial command-line interface for Atlassian Confluence Cloud.

## What is this?

`confl` is a CLI tool for reading and editing Confluence pages directly from your terminal. It's designed to be scriptable and agent-friendly—no interactive editors by default, just straightforward commands that can be chained and automated.

## Authentication

- **API Token** — for CI/automation (via environment variables or config file)
- **OAuth** — browser-based login for interactive use

## Configuration

Config lives in `~/.config/confl/`. Environment variables (`CONFL_*`) can override config file settings.

## Installation

```
pipx install git+https://github.com/pocmo/confl.git
```

## Commands

### search

Search for Confluence content using CQL (Confluence Query Language) or simple filters.

**Two modes of operation:**

1. **Simple filters** (for common cases):
```bash
confl search --text "API docs" --space DEV --type page --label draft
```

2. **Raw CQL query** (for power users):
```bash
confl search "space = DEV AND type = page ORDER BY lastmodified DESC"
```

**Examples:**

```bash
# Search for text in a specific space
confl search --text "database migration" --space ENG

# Find all pages with a label
confl search --type page --label architecture

# Combine multiple filters
confl search --text "meeting notes" --space TEAM --type page

# Raw CQL for complex queries
confl search "space = MARKETING AND created >= now('-7d')"

# Get results as JSON
confl search --text "API" --json

# Limit number of results
confl search --text "documentation" --limit 10
```

**Available filters:**
- `--text` — Search for text in content
- `--space` — Filter by space key
- `--type` — Filter by content type (page, blogpost, etc.)
- `--label` — Filter by label
- `--limit` — Maximum number of results (default: 25)
- `--json` — Output as JSON array

**CQL Basics:**

CQL supports powerful queries with operators and functions:
- `space = KEY` — Filter by space
- `type = page` — Filter by content type
- `label = draft` — Filter by label
- `text ~ "keyword"` — Text search
- `created >= now('-7d')` — Date filters
- `AND`, `OR`, `NOT` — Logical operators
- `ORDER BY lastmodified DESC` — Sorting

For complete CQL reference, see [Atlassian's CQL documentation](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/).
