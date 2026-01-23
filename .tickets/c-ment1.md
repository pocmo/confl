---
id: c-ment1
status: closed
deps: []
links: []
created: 2026-01-23T19:07:00Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# INVESTIGATION: Improve rendering of @mentions to show usernames instead of IDs

When fetching pages with user mentions (@...), the markdown console output shows user IDs like `[@557058:3aade8e1-22a…` instead of readable usernames.

## Problem
Currently when a page contains user mentions:
- Display shows: `[@557058:3aade8e1-22a…`
- User expectation: `@username` or `@Full Name`
- Makes content harder to read
- Doesn't look like natural mentions

## Investigation Questions

### 1. How are mentions stored in Confluence?
- What does the storage format look like for mentions?
- Is it `<ac:link><ri:user ri:account-id="..."/></ac:link>`?
- Does it include username/display name in the storage format?
- Or just the account ID?

### 2. Can we resolve user IDs to names?
- Is there a Confluence API endpoint to look up user details by account ID?
- `/wiki/api/v2/users/{accountId}` or similar?
- Can we get display name, username, email?
- Are there rate limits or permissions needed?
- Can we batch lookup multiple users?

### 3. What's the best UX for mentions?
Options to consider:
- **Option A**: `@username` (simple, familiar)
- **Option B**: `@Full Name` (more descriptive)
- **Option C**: `@username (Full Name)` (comprehensive)
- **Option D**: Keep ID but highlight/color it
- Which is most readable in terminal?

### 4. Performance considerations
- How many mentions might a page have?
- Should we cache user lookups?
- Do all mentions on one page in a single API call?
- What if user lookup fails (deleted user, no permission)?

### 5. Visual highlighting
- Can we use Rich styling to highlight mentions?
- Color options: cyan, blue, yellow, bold?
- Should mentions be clickable/special in any way?
- Look at how other tools render mentions

### 6. Implementation complexity
- Can converter handle this during markdown conversion?
- Need to intercept mention nodes during parsing?
- Add user lookup step after conversion?
- What if we're using --raw or --body-only flags?

## Tasks
1. Find a page with user mentions and examine storage format
2. Check if user API endpoints exist for lookup
3. Test user lookup with sample account IDs
4. Prototype different display options
5. Measure performance impact of user lookups
6. Test with pages having multiple mentions
7. Handle edge cases (deleted users, invalid IDs)

## Output
Document findings in ticket notes:
- How mentions are stored
- Whether user lookup is feasible
- Recommended display format
- Performance impact
- Implementation approach

File follow-up tickets:
- If straightforward: Implementation ticket with clear approach
- If complex: Break into sub-tickets (lookup service, converter integration, caching)
- If not worth the effort: Document why and close

## Acceptance Criteria
- Clear understanding of mention storage format
- Know if user lookup is possible via API
- Tested user lookup with sample data
- Recommendation on display format
- Effort estimate for implementation
- Decision on whether to implement

## References
- docs/architecture/content-rendering.md — rendering approach
- docs/architecture/atlassian-document-format.md — ADF mention format
- src/confl/converter.py — markdown conversion
- Confluence API docs for user lookup

## Notes
- This is a UX improvement, not critical functionality
- Nice-to-have for better readability
- Consider if user lookup overhead is worth it
- May need caching to avoid excessive API calls
- Example from issue: `[@557058:3aade8e1-22a…` should be `@username`

**2026-01-23T19:09:22Z**

Investigation complete. Documented findings below.

**2026-01-23T19:10:10Z**

Investigation complete. Full findings documented in .ralph/c-ment1-findings.md

KEY FINDINGS:
- User mentions in <ac:link> tags show as [@557058:...] instead of @username
- Root cause: convert_ac_link() doesn't check for ri:user children
- Fix is simple: Check for ri:user in ac:link and delegate to convert_ri_user()
- No API lookups needed - storage format already has username when available
- Estimated effort: 30 minutes (code + tests)

RECOMMENDATION: File P2 implementation ticket to fix convert_ac_link() method.
