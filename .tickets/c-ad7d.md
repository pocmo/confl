---
id: c-ad7d
status: open
deps: []
links: []
created: 2026-01-14T21:23:46Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# DISCOVERY: Identify additional CLI subcommands from Confluence API

Analyze the Confluence API to identify what other entity subcommands (beyond 'page') would be valuable to support.

## Questions to Answer
1. **What API endpoints/entities are available?**
   - Review docs/architecture/API.md and OpenAPI spec
   - What top-level entities exist? (spaces, attachments, search, comments, labels, etc.)
   - What operations are available for each entity?

2. **What are the most useful entities for CLI users?**
   - Which entities complement 'page' operations?
   - Which provide essential functionality for common workflows?
   - Which are frequently used together?

3. **What should each subcommand group include?**
   - For each entity (e.g., 'space', 'search', 'attachment', 'comment'):
     - What operations make sense? (list, get, create, update, delete)
     - What are the required parameters?
     - What output formats are needed?
     - What are common use cases?

4. **What's the priority order?**
   - Which subcommands are most critical? (P0/P1)
   - Which are nice-to-have? (P2)
   - Which can wait for future iterations? (P3)

5. **Are there any complex integrations?**
   - Which features require multiple API calls?
   - Which require special handling (e.g., file uploads)?
   - Which need discovery tickets vs. straightforward implementation?

## Output
- Document findings in docs/architecture/cli-subcommands.md
- For each proposed subcommand entity, document:
  - Entity name and purpose
  - Proposed commands (e.g., 'confl space list', 'confl search query')
  - Priority level
  - Implementation complexity estimate
  - Dependencies on other work
- File follow-up tickets:
  - Discovery tickets for complex/unclear entities
  - Implementation tickets for straightforward entities
  - Group related commands appropriately

## IMPORTANT
This is a DISCOVERY ticket. Research, document, file follow-ups, then STOP.

## References
- docs/architecture/API.md — API overview
- docs/architecture/openapi-v2.v3-spec.json — full API spec
- docs/architecture/cli-design.md — command structure patterns
- docs/architecture/page-commands.md — example entity implementation

## Notes
- Follow entity-first pattern: confl <entity> <action>
- Consider what would make the CLI useful for daily workflows
- Look at cli-design.md for already planned entities (space, search, attachment, comment)
- Some entities may not be worth implementing (too niche, too complex)

