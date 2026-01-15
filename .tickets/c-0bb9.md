---
id: c-0bb9
status: open
deps: [c-89ee]
links: []
created: 2026-01-15T10:17:10Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Feature: Implement confl space search command

Add 'confl space search' command to find spaces by name or description.

## Use Case
Users want to find a space when they know part of the name but don't know the space key.

## Tasks
- Check if there's existing space search discovery work (e.g., c-89ee)
- Implement `confl space search <query>` command
- Search spaces by name and/or description
- Show matching spaces with key, name, and type
- Support search options:
  - Case-insensitive by default
  - Maybe --exact flag for exact matches
- Return results in useful format (table by default, --json option)

## Acceptance Criteria
- `confl space search "Engineering"` finds spaces with 'Engineering' in name
- Results show space key, name, type
- --json flag works
- Clear message when no matches found

## References
- c-89ee — space search discovery ticket (check if completed)
- src/confl/commands/space.py — add search command
- Confluence API search/filter capabilities

## Notes
- Depends on API capabilities for searching
- May need to use GET /spaces with filtering or broader search endpoint
- Should be case-insensitive and intuitive
- Consider dependency on c-89ee if not completed

