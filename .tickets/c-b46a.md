---
id: c-b46a
status: open
deps: []
links: []
created: 2026-01-15T11:28:46Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Feature: Implement confl space search command

Implement 'confl space search <query>' command to search spaces by name using CQL.

## Requirements

From discovery (c-89ee / space-lookup-discovery.md):

### Basic Command
```bash
confl space search "Engineering"
```
- Search spaces by name using fuzzy CQL matching (title~"query")
- Display results in table: Key | Name | Type | ID
- Support --json output

### Options
- `--type <global|personal>` - Filter by space type
- `--limit <n>` - Limit results (default 25)
- `--json` - Output as JSON array

### Implementation
- Use v1 search API: confluence.search_content('type=space AND title~"query"', limit)
- Extract space info from results[].space object
- Handle HTML entities in names (use html.unescape)
- Follow pattern from existing search.py command

### Testing
- Test basic search
- Test with --type filter
- Test with --json output
- Test HTML entities in names
- Test no results case

### Documentation
- Add to README.md examples
- Update docs/architecture/cli-subcommands.md

