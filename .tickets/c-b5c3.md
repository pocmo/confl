---
id: c-b5c3
status: closed
deps: []
links: []
created: 2026-01-14T22:07:08Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# DESIGN: Specify search command implementation approach

Design the 'search' CLI entity for content discovery using CQL (Confluence Query Language). Need to determine: 1) API v2 search endpoint availability (may need v1 fallback), 2) CQL syntax support vs simple flags, 3) Output format and fields. Reference: docs/architecture/cli-subcommands.md Phase 2. Proposed: confl search <query>, confl search --text 'keyword', confl search --space <key> --type page --label <label>. Document decision in ticket notes, file implementation ticket after design.


## Notes

**2026-01-14T22:31:13Z**

Design decision: Use API v1 with dual interface (flags + CQL)

**2026-01-14T22:31:19Z**

API Research:
- API v2 has NO search endpoints (verified via OpenAPI spec)
- API v1 has /wiki/rest/api/search with full CQL support
- v1 is production-ready, no deprecation until v2 parity
- CQL supports: space, type, label, text, dates, operators (AND/OR/NOT/~)

**2026-01-14T22:31:24Z**

Design: Dual Interface Approach

1. Simple flags for common cases:
   confl search --text "keyword" --space KEY --type page --label L
   
2. Raw CQL for power users:
   confl search "space = DEV AND type = page ORDER BY lastmodified DESC"
   
3. Output: Table (default) or JSON (--json flag)

4. Implementation: Extend ConfluenceClient for v1 API, add CQL builder helper

**2026-01-14T22:31:57Z**

Design complete. Filed 5 implementation tickets: c-56ae (v1 API), c-3a57 (CQL builder), c-f581 (search command), c-d072 (tests), c-2a5a (docs). Dependencies configured.
