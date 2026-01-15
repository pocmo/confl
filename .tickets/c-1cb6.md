---
id: c-1cb6
status: closed
deps: []
links: []
created: 2026-01-15T10:02:22Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# FIX: Make get_space() accept both space keys and IDs

Fix ConfluenceClient.get_space() to handle both space keys and numeric IDs correctly.

Current bug: get_space() uses /spaces/{id} endpoint which only accepts numeric IDs. When users pass space keys (like 'DEV' or personal space keys like '~61df405068926d0068c87f43'), it fails with 400 error.

Solution: Update get_space() to:
1. Check if space_ref is numeric
2. If numeric: use /spaces/{id} directly
3. If not numeric: use get_space_by_key() to look up by key

This will make commands like 'confl space get', 'space update', 'space delete' work with both keys and IDs as documented.

Related to investigation ticket c-5171.


## Notes

**2026-01-15T10:02:33Z**

Scope: Fix all three methods that incorrectly use /spaces/{id}:
1. get_space() - line 575
2. update_space() - line 624
3. delete_space() - line 657

All three have comments claiming 'API accepts both IDs and keys' but this is FALSE for API v2. They all use PUT/GET/DELETE /spaces/{id} which only accepts numeric IDs.

Solution applies to all three:
- Parse space_ref to check if numeric
- If numeric: use /spaces/{id} 
- If not numeric: first resolve key to ID using /spaces?keys={key}, then use /spaces/{id}

**2026-01-15T10:12:15Z**

Completed: Fixed get_space(), update_space(), and delete_space() to properly handle both space keys and numeric IDs. Methods now check if input is numeric and either use /spaces/{id} directly or resolve key via /spaces?keys={key} first.
