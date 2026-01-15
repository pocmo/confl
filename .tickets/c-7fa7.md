---
id: c-7fa7
status: closed
deps: []
links: []
created: 2026-01-15T10:16:58Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Enhancement: Add filtering options to confl space list

Add ability to filter spaces in 'confl space list' by type, status, or other criteria.

## Use Cases
- Show only personal spaces
- Show only team spaces
- Filter by space status (active/archived)
- Filter spaces I'm watching/favorited

## Tasks
- Research what filtering options Confluence API supports
- Add relevant filter flags:
  - --type (personal, global, etc.)
  - --status (current, archived)
  - --mine (show only my personal space)
  - Others based on API capabilities
- Implement filtering (API-side if supported, client-side otherwise)
- Document in help text

## Acceptance Criteria
- `confl space list --mine` shows user's personal space
- `confl space list --type personal` shows all personal spaces
- Filters can be combined if sensible
- Help text documents filter options

## References
- src/confl/commands/space.py — space list command
- Confluence API docs for spaces endpoint filter parameters

## Notes
- Check what filters API supports vs what needs client-side filtering
- Personal spaces are a common filter need
- Similar to 'gh repo list --visibility' pattern


**2026-01-15T11:43:56Z**

Completed: Added filtering options --mine, --favorited, and --label to confl space list. Implemented get_current_user API method. API-side filtering for favorited and labels, client-side filtering for --mine (by authorId).
