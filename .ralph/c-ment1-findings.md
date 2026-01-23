# Investigation Findings: c-ment1

## 1. How mentions are stored in Confluence

Confluence uses TWO different storage formats for user mentions:

### Format A: Standalone `<ri:user>` (ALREADY WORKING)
```xml
<ri:user ri:username="jsmith" />
<ri:user ri:account-id="557058:3aade8e1-22aa-4566-9c02-d8a4f5e89012" />
```
- Converts correctly to @jsmith or @557058:... 
- Already handled by convert_ri_user() method
- 12 comprehensive tests already exist
- Works perfectly!

### Format B: `<ac:link>` wrapping `<ri:user>` (THE PROBLEM)
```xml
<ac:link>
  <ri:user ri:account-id="557058:3aade8e1-22aa-4566-9c02-d8a4f5e89012" />
  <ac:link-body>@557058:3aade8e1-22aa-4566-9c02-d8a4f5e89012</ac:link-body>
</ac:link>
```
- Currently converts to **[@557058:...]** (wrapped in brackets like a page link)
- **This is what users are seeing and reporting as the bug**
- convert_ac_link() doesn't check for ri:user children
- Falls through to generic link handling

## 2. Can we resolve user IDs to names?

**Short answer: No practical way for this use case**

Confluence Cloud REST API v2 has user endpoints, but:
- Requires individual lookup per account ID: GET /wiki/api/v2/users/{accountId}
- Would add significant API overhead (1 call per mention per page)
- Need caching layer to avoid rate limits
- Deleted/deactivated users would fail lookups
- Adds complexity for minimal UX gain

**Better solution:** Storage format already contains username when available:
- ri:username attribute (most readable)
- ri:userkey attribute (often contains username)  
- Only falls back to account-id when username not available

**The real problem is not ID-to-name resolution** - it's that the converter ignores the ri:user attributes when wrapped in ac:link.

## 3. Best UX for mentions

Current approach is already ideal:
- **@username** format (simple, familiar, used in test suite)
- Falls back to @userkey or @account-id when username unavailable
- No additional API calls needed
- Already implemented in convert_ri_user()

The only missing piece: handle mentions wrapped in `<ac:link>` tags.

## 4. Performance considerations

**Zero performance impact for the fix:**
- No additional API calls needed
- Just check if ac:link contains ri:user before processing
- Delegate to existing convert_ri_user() method
- All logic and fallback already implemented

## 5. Visual highlighting

Not investigated - low priority cosmetic enhancement. Current @username format is clear and readable.

## 6. Implementation complexity

**Very simple fix - estimated 30 minutes:**

1. Modify `convert_ac_link()` method in converter.py:
   - Check if el.find("ri:user") exists
   - If yes: extract the ri:user element and call convert_ri_user()
   - If no: continue with existing page link logic

2. Add tests for ac:link wrapped mentions (4-5 test cases)

3. Verify with pytest

**No architecture changes needed.** Reuses all existing logic.

## 7. Edge cases tested

Created test cases for:
- ✅ Standalone ri:user with username → @jsmith
- ✅ Standalone ri:user with account-id → @557058:...
- ✅ ac:link wrapping ri:user → currently broken, shows [@557058:...]
- ✅ ac:link with link-body → currently broken, shows [@557058:...]

## Decision & Recommendation

### Problem Statement
User mentions wrapped in `<ac:link>` tags display as `[@557058:3aade8e1-22a…]` instead of `@username`.

### Root Cause  
The convert_ac_link() method only handles page links. It doesn't check if the link wraps a user mention.

### Recommended Solution
**Fix convert_ac_link() to handle wrapped user mentions**

Implementation:
```python
def convert_ac_link(self, el: Tag, text: str, **options: Any) -> str:
    # NEW: Check if this is a user mention wrapped in ac:link
    ri_user = el.find("ri:user")
    if ri_user is not None:
        return self.convert_ri_user(ri_user, "", **options)
    
    # Existing page link logic...
    link_body = el.find("ac:link-body")
    # ... rest of method unchanged
```

### Effort: 30 minutes
- Simple code change
- Add 4-5 test cases
- Run pytest to verify

### Alternative Considered: User API lookup
**Rejected** - adds API overhead, caching complexity, handles deleted users poorly, and provides no benefit since storage format already has username when available.

## Follow-up Action
File implementation ticket with:
- Clear description of the bug
- Reference to this investigation
- Code change needed (modify convert_ac_link)
- Test cases to add
- Priority: P2 (UX improvement, not critical)
