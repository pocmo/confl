---
Status: GUIDE
Date: 2026-01-15
Purpose: Document architecture documentation standards
---

# Architecture Documentation

This directory contains architecture decision records, design documents, and technical analysis for the confl project.

## Document Status Front Matter

All architecture documents include YAML front matter indicating their status and purpose. This helps readers quickly understand whether a document describes current implementation, future proposals, or historical decisions.

### Status Values

- **IMPLEMENTED** — Document describes currently implemented features/design
- **PARTIALLY IMPLEMENTED** — Some features implemented, others pending (list in front matter)
- **PROPOSAL** — Future feature or design not yet implemented
- **DECISION** — Past design decision that guided implementation
- **ANALYSIS** — Research/analysis document (may include recommendations)
- **PLANNING** — Roadmap or phased implementation plan
- **REFERENCE** — API documentation, format specifications
- **GUIDE** — How-to or best practices document
- **VISION** — High-level goals and project direction
- **REVIEW** — Code review or audit findings

### Front Matter Format

```markdown
---
Status: <STATUS>
Date: <YYYY-MM-DD creation date>
Purpose: <Brief description of document purpose>
[Optional fields based on status]
---

# Document Title
```

### Optional Fields by Status

**PARTIALLY IMPLEMENTED:**
```yaml
Implemented: <List of completed features>
Pending: <List of pending features>
```

**PROPOSAL:**
```yaml
Decision: <Current status (e.g., Approved, Deferred, Rejected)>
```

**PLANNING:**
```yaml
Implemented: <Completed phases/features>
Pending: <Remaining phases/features>
```

## Document Categories

### Core Implementation Docs
Current state of implemented features:
- `design-principles.md` — Core design philosophy
- `cli-design.md` — Command structure and patterns
- `configuration.md` — Auth and config system
- `content-formats.md` — Output format support
- `page-commands.md` — Page entity implementation
- `content-rendering.md` — Content display architecture

### Reference Documentation
API and format specifications:
- `API.md` — Confluence Cloud REST API v2 reference
- `atlassian-document-format.md` — ADF format specification

### Planning & Analysis
Roadmaps and research:
- `cli-subcommands.md` — Entity expansion roadmap (Phases 1-3)
- `storage-format-feature-gaps.md` — Format support analysis
- `testing.md` — Testing strategy and coverage
- `senior-review-findings.md` — Code quality review

### Decisions & Proposals
Past decisions and future proposals:
- `markdown-conversion.md` — Conversion library selection (implemented)
- `oauth-browser-login.md` — OAuth evaluation (deferred)
- `cli-ux-improvements.md` — UX enhancements (partially implemented)

### Guides
Best practices and standards:
- `filing-tickets.md` — Ticket creation guidelines
- `goals.md` — Project vision and audience

## Adding New Documents

When creating new architecture documents:

1. **Add front matter** at the top with appropriate status
2. **Choose accurate status** — be honest about implementation state
3. **Include date** — when the document was created
4. **Write clear purpose** — one-line description of what the doc covers
5. **Update this README** — add to appropriate category section

## Finding Documents

- **Current implementation?** Look for Status: IMPLEMENTED
- **Proposed features?** Look for Status: PROPOSAL
- **Past decisions?** Look for Status: DECISION
- **API reference?** Check API.md or atlassian-document-format.md
- **Not sure what's implemented?** Check Status: PARTIALLY IMPLEMENTED docs

## Questions?

If you're unsure about a document's status or what's implemented:
1. Check the front matter Status field
2. Read the document's summary/executive section
3. Run `uv run confl --help` to see current CLI commands
4. Check test files in `tests/` for implemented features
