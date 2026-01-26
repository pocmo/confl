---
id: c-ment2
status: closed
deps: []
links: []
created: 2026-01-23T20:44:00Z
type: bug
priority: 1
assignee: Sebastian Kaspari
---
# BUG: User mentions display account ID instead of username

User mentions in page content are being rendered as `@5e9c86c6a747380c188f4d4c` (account ID) instead of the actual username that appears on the Confluence webpage.

## Bug Description
When displaying pages with user mentions:
- **Current output**: `@5e9c86c6a747380c188f4d4c`
- **Expected output**: `@username` (the readable name shown on Confluence web)
- **Example**: If the user is "John Doe" with username "jdoe", should show `@jdoe` or `@John Doe`

## Problem
The mention is now showing the Confluence account ID, which is:
- Not human-readable
- Not the same as what users see in the web UI
- Makes it unclear who is being mentioned
- Poor user experience

## Root Cause Investigation Needed
- How is the converter extracting mention data?
- Is it getting the account-id attribute but not looking up the user?
- Does the storage format include the display name inline?
- Or do we need to look it up via API?
- Related to investigation ticket c-ment1

## Tasks
1. Examine the storage format of mentions in sample page
2. Check what data is available in the mention XML/JSON:
   - Does it include `displayName` or `username`?
   - Or only `accountId`?
3. If display name is in storage format:
   - Update converter to extract and use it
   - Test with various mention formats
4. If display name requires API lookup:
   - Check feasibility per c-ment1 investigation
   - May need to implement user lookup service
   - Consider caching for performance
5. Test fix with real pages containing mentions
6. Handle edge cases (deleted users, missing names)

## Acceptance Criteria
- User mentions display human-readable names, not IDs
- Matches (or is close to) what Confluence web UI shows
- Works for all mention types
- Graceful fallback if name unavailable (show ID with note?)
- No significant performance impact

## References
- c-ment1 — user mention rendering investigation
- src/confl/converter.py — markdown conversion
- docs/architecture/content-rendering.md — rendering approach

## Notes
- This makes mentions completely unreadable
- Account IDs like `5e9c86c6a747380c188f4d4c` are meaningless to users
- Need to either extract name from storage OR look up via API
- Web UI shows readable names, CLI should too
- May be quick fix if name is in storage format already
- If requires API lookup, depends on c-ment1 investigation

**2026-01-26T13:34:55Z**

Starting investigation: converter already tries username first, but bug report says account IDs are showing. Need to check real data samples.

**2026-01-26T13:35:12Z**

Analysis: Code already prefers ri:username. Issue is when storage only has ri:account-id. Two options: (1) API lookup or (2) check for other attrs like display name in link-body. Checking actual data patterns...

**2026-01-26T13:35:44Z**

Solution identified: ac:link-body contains display name. Need to extract it and pass to convert_ri_user as fallback when username not in attributes.

**2026-01-26T13:37:23Z**

Completed: User mentions now show display name from ac:link-body instead of account ID. Added 3 new tests. Priority order: username > userkey > display_name > account_id.
