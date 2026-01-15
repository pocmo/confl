# Space Lookup Discovery

**Date:** 2026-01-15  
**Ticket:** c-89ee  
**Status:** Complete

## Executive Summary

Users can search for Confluence spaces by name using two approaches:

1. **CQL Search (v1 API)** - Full-text search with fuzzy matching via `title~"name"` operator
2. **Client-side Filtering** - Fetch all spaces and filter locally (works for smaller instances)

Both methods are viable. CQL search is recommended for most use cases as it's server-side, supports fuzzy matching, and works well with large Confluence instances.

## API Capabilities

### GET /wiki/api/v2/spaces

The v2 spaces endpoint supports these filters:

- `ids` - Filter by space IDs (comma-separated)
- `keys` - Filter by space keys (comma-separated)
- `type` - Filter by type (global, personal)
- `status` - Filter by status (current, archived)
- `labels` - Filter by labels (comma-separated)
- `favorited-by` - Filter by user account ID
- `not-favorited-by` - Exclude favorited spaces
- `sort` - Sort results

**❌ No "name" or "search" parameter** - Cannot search by space name using v2 API directly.

### CQL Search via v1 API (GET /wiki/rest/api/search)

The v1 search API supports CQL queries including:

```cql
type=space                           # All spaces
type=space AND title~"Engineering"   # Fuzzy match on name
type=space AND title="Engineering"   # Exact match on name
type=space AND space.type=personal   # Personal spaces only
type=space AND space.type=global     # Global spaces only
```

**✅ Works perfectly** - Returns spaces with full metadata including key, name, ID, type, status.

### Pagination

- **v2 /spaces**: Cursor-based pagination, fetch 100 per page, supports up to 1000+ spaces efficiently
- **v1 /search**: Limit-based pagination, typical limits 25-100 results

## Search Methods

### Option A: CQL Search (Recommended)

**Pros:**
- Server-side filtering (efficient for large instances)
- Fuzzy text matching with `title~"query"`
- Exact matching with `title="query"`
- Can combine with other filters (type, labels, etc.)
- Returns rich result metadata

**Cons:**
- Uses v1 API (but stable and widely used)
- Requires understanding of CQL syntax for advanced queries
- Limited to search result format (not direct space objects)

**Example:**
```python
results = confluence.search_content('type=space AND title~"Engineering"', limit=25)
for result in results:
    space = result['space']
    print(f"{space['key']} | {space['name']}")
```

### Option B: Client-side Filtering

**Pros:**
- Uses v2 API
- Simple case-insensitive substring matching
- No CQL knowledge required
- Returns full space objects

**Cons:**
- Must fetch ALL spaces first (inefficient for large instances)
- Higher latency for instances with 1000+ spaces
- No fuzzy matching
- More network overhead

**Example:**
```python
all_spaces = confluence.list_spaces()
matches = [s for s in all_spaces if 'engineering' in s['name'].lower()]
```

### Performance Comparison

| Scenario | CQL Search | Client-side Filter |
|----------|------------|-------------------|
| Small instance (<100 spaces) | ⚡ Fast | ⚡ Fast |
| Medium instance (100-500 spaces) | ⚡ Fast | 🟡 Acceptable |
| Large instance (500-1000+ spaces) | ⚡ Fast | ❌ Slow |

## Personal Spaces

Personal spaces can be discovered via:

1. **List with type filter:**
   ```python
   personal = confluence.list_spaces(type_filter='personal')
   ```

2. **CQL search:**
   ```cql
   type=space AND space.type=personal AND title~"username"
   ```

3. **Find current user's space:**
   - Space key format: `~username` or `~accountId`
   - Can search by user's name in space name
   - Might need to get current user first, then construct key

## UX Recommendations

### Recommended Approach: New `confl space search` Command

Add a dedicated search command for best UX:

```bash
# Fuzzy search by name
confl space search "Engineering"

# Show personal spaces only
confl space search --personal "John"

# Filter by type
confl space search --type global "Product"

# Output options
confl space search "API" --json
```

**Benefits:**
- Clear, intuitive command structure
- Follows Unix tool conventions (grep, find, etc.)
- Matches pattern used by other tools (gh, kubectl, etc.)
- Doesn't complicate existing commands
- Easy to add filters incrementally

### Alternative: Enhance `confl space list` with Search

Add filtering to existing list command:

```bash
# List with name filter
confl space list --name "Engineering"

# List with fuzzy search
confl space list --search "Eng"
```

**Benefits:**
- Fewer commands to learn
- Natural extension of existing functionality
- Consistent with list/filter pattern

**Concerns:**
- List typically implies "show all"
- Mixing listing and searching semantics
- Could get complex with many filters

### Not Recommended: Auto-resolve Space Names

Don't automatically resolve space names in `--space` flags:

```bash
# ❌ BAD: Ambiguous and error-prone
confl page list --space "Engineering"  # Which space? TECH? SOLENG? AIE?
```

**Problems:**
- Multiple spaces can have similar names
- Silent failures or wrong results
- Makes commands non-deterministic
- Hard to debug issues
- Breaks scripts when spaces are renamed

**Better:**
- Keep `--space` expecting keys/IDs only
- Users run `confl space search` first to find key
- Clear, explicit, predictable behavior

## Implementation Plan

### Phase 1: Core Search Command (Recommended MVP)

Create `confl space search` command:

```python
def search_spaces(
    query: str,
    type_filter: str | None = None,  # global, personal
    limit: int = 25,
    json_output: bool = False,
) -> None:
    """Search spaces by name using CQL."""
    # Build CQL query
    cql = f'type=space AND title~"{query}"'
    if type_filter:
        cql += f' AND space.type={type_filter}'
    
    results = confluence.search_content(cql, limit=limit)
    # Display results...
```

**Estimated effort:** 4-6 hours
- Add command (~2h)
- Add tests (~2h)
- Update docs (~1h)
- Manual testing (~1h)

### Phase 2: Enhanced Listing (Optional)

Add filters to `confl space list`:
- `--name` for substring search
- `--search` for fuzzy CQL search
- Leverage existing type/status filters

**Estimated effort:** 2-3 hours

### Phase 3: User Discovery (Future)

Help users find their own space:
- `confl space whoami` - Show current user's personal space
- `confl space list --mine` - List spaces user can access
- Requires getting current user info from API

**Estimated effort:** 3-4 hours

## API Request/Response Examples

### CQL Space Search

**Request:**
```http
GET /wiki/rest/api/search?cql=type%3Dspace%20AND%20title~%22Engineering%22&limit=25
```

**Response:**
```json
{
  "results": [
    {
      "space": {
        "key": "TECH",
        "name": "Engineering",
        "type": "global",
        "status": "current"
      },
      "title": "Engineering",
      "excerpt": "Main engineering team space",
      "url": "/spaces/TECH",
      "entityType": "space",
      "lastModified": "2026-01-15T10:00:00.000Z"
    }
  ],
  "start": 0,
  "limit": 25,
  "size": 1,
  "_links": {}
}
```

### List All Spaces (v2)

**Request:**
```http
GET /wiki/api/v2/spaces?limit=100&type=global
```

**Response:**
```json
{
  "results": [
    {
      "id": "1310723",
      "key": "TECH",
      "name": "Engineering",
      "type": "global",
      "status": "current",
      "description": {
        "plain": {
          "value": "Main engineering team space"
        }
      }
    }
  ],
  "_links": {
    "next": "/wiki/api/v2/spaces?cursor=abc123&limit=100"
  }
}
```

## Common Use Cases

### 1. Find space by partial name
```bash
confl space search "Product"
# Shows: Product Team, Product Marketing, Product Docs, etc.
```

### 2. Find exact space
```bash
confl space search "Engineering" | grep "^TECH"
# Or add --exact flag in future
```

### 3. Find personal space
```bash
confl space search --personal "John Smith"
# Shows: ~jsmith | John Smith
```

### 4. Explore spaces by topic
```bash
confl space search "API"
confl space search "Design"
confl space search "Architecture"
```

### 5. Script usage
```bash
# Get space key programmatically
SPACE_KEY=$(confl space search "Engineering" --json | jq -r '.[0].space.key')
confl page list --space "$SPACE_KEY"
```

## Comparison with Other Tools

### GitHub CLI (gh)
```bash
gh repo list                    # List all
gh repo search "kubernetes"     # Search
```

### Kubernetes (kubectl)
```bash
kubectl get namespaces          # List all
kubectl get namespaces | grep prod  # Filter client-side
```

### Google Cloud (gcloud)
```bash
gcloud projects list            # List all
gcloud projects list --filter="name:prod"  # Server-side filter
```

**Lesson:** Most tools provide dedicated search/filter commands for resources. Users expect `search` for fuzzy finding and `list` for comprehensive views.

## Decision

**✅ Implement `confl space search` command using CQL**

### Rationale

1. **Clear UX** - Dedicated search command matches user mental model
2. **Scalable** - Server-side filtering works for any instance size
3. **Flexible** - CQL supports fuzzy matching and complex queries
4. **Extensible** - Easy to add filters (type, status, labels, etc.)
5. **Consistent** - Similar to how `confl search` works for content

### Next Steps

1. **File implementation ticket** - Create `confl space search` command
2. **Consider future enhancements:**
   - Add `--exact` flag for exact matching
   - Add `--mine` flag for user's accessible spaces
   - Add `--favorite` flag using `favorited-by` filter
   - Support other CQL operators via `--cql` raw query

## References

- [Confluence Cloud REST API v2 - Spaces](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/)
- [Confluence Search API (v1)](https://developer.atlassian.com/cloud/confluence/rest/api-group-search/)
- [CQL (Confluence Query Language)](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/)
- OpenAPI spec: `docs/architecture/openapi-v2.v3-spec.json`
- Existing search implementation: `src/confl/commands/search.py`

## Related Tickets

- c-0bb9 - Feature: Implement confl space search command (implementation)
- c-2369 - Enhancement: Add sorting options to confl space list
- c-7fa7 - Enhancement: Add filtering options to confl space list
