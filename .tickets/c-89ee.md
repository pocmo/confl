---
id: c-89ee
status: open
deps: []
links: []
created: 2026-01-15T10:01:38Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# DISCOVERY: Search/lookup spaces by name instead of key/ID

Research if and how users can search for spaces by name when they don't know the space key or ID.

## Problem Statement
Users may know a space's name (e.g., 'Engineering Team') but not its space key (e.g., 'ENG') or ID. We need to understand if the Confluence API supports searching/looking up spaces by name.

## Questions to Answer

### 1. API Capabilities
- Does Confluence API support searching spaces by name?
- What endpoints are available for space discovery?
- GET /wiki/api/v2/spaces - does it support filtering/searching by name?
- Is there a dedicated search endpoint for spaces?
- What query parameters are available (name, label, type, etc.)?

### 2. Search Methods
- Can we do full-text search on space names?
- Is it exact match only or fuzzy search?
- Can we list all spaces and filter client-side?
- Are there pagination limits we need to handle?
- What about private vs public spaces?

### 3. UX Considerations
- Should we add a 'confl space search' command?
- Should we support '--space-name' flag in addition to '--space' (key)?
- Should we auto-resolve space names to keys/IDs internally?
- What if multiple spaces match the name?
- How do we handle no matches?

### 4. Personal Spaces
- Can personal spaces be searched by user's name?
- How do users discover their own personal space?
- Should we have a 'confl space list --mine' option?

### 5. Implementation Options
- **Option A**: Add 'confl space search <name>' command
- **Option B**: Accept space name in --space flag and auto-resolve
- **Option C**: Add 'confl space list' with filtering options
- **Option D**: Combination of above
- Which provides best UX?

## Output
- Document findings in **docs/architecture/space-lookup-discovery.md**
- Include:
  - API capabilities for space search/lookup
  - Available query methods and parameters
  - Recommended UX approach
  - Example API requests/responses
  - Comparison of implementation options
- File follow-up tickets:
  - Implementation ticket(s) if straightforward
  - Additional discovery if approach unclear
  - Consider user workflows and common use cases

## IMPORTANT
This is a DISCOVERY ticket. Research, document, file follow-ups, then STOP.

## References
- docs/architecture/API.md — API reference
- docs/architecture/openapi-v2.v3-spec.json — full API spec
- https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/ — Space API docs
- c-5171 — related space ID investigation

## Notes
- This is a common user need - not knowing exact space keys
- Good UX means users shouldn't need to memorize keys/IDs
- Consider how other tools handle this (gh, gcloud, etc.)
- May relate to overall search/discovery strategy

