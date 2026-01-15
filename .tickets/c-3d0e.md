---
id: c-3d0e
status: closed
deps: []
links: []
created: 2026-01-15T12:47:44Z
type: bug
priority: 1
assignee: Sebastian Kaspari
---
# BUG: Empty table renders when space list has no results

When 'confl space list' returns no spaces, it renders an empty table which looks weird.

## Bug Description
Running `confl space list` (or with filters that return no results) displays an empty table with just headers and no rows. This looks awkward and doesn't clearly communicate that there are no results.

## Expected Behavior
When no spaces are found, show a friendly message instead of an empty table:
- "No spaces found."
- Or if filters applied: "No spaces match the specified criteria."

## Tasks
- Check space list command implementation
- Add check for empty results before rendering table
- If results are empty:
  - Skip table rendering
  - Print clear message to user
  - Exit cleanly
- If --json flag is used, still output empty array []
- Apply same pattern to other list commands if they have same issue

## Acceptance Criteria
- Empty results show message instead of empty table
- Message is clear and helpful
- --json flag still outputs []
- Non-zero exit code not needed (empty result is not an error)

## References
- src/confl/commands/space.py — space list command
- Consider checking other list commands (page list, etc.)

## Notes
- Similar issue might exist in other list commands
- Good UX: clear messages when no results
- Examples from other CLIs: 'No repositories found', 'No issues match your query'


**2026-01-15T12:51:15Z**

Fixed: Empty result sets now display clear message instead of empty table. Applied to all list commands: space, page, blogpost, comment, attachment, label, task, and search. Tests pass. JSON output unchanged (still returns empty array).
