---
Status: GUIDE
Date: 2025-12-01
Purpose: Guidelines for creating effective tickets for AI agent workflow
---

# Filing Tickets

Guidelines for creating good tickets that AI agents can work on effectively.

## Ticket Size

**One commit = one ticket.** Each ticket should be:

- A single, focused change
- Completable in one work session
- Small enough to review easily
- Large enough to be meaningful

If a task feels too big, break it down. If it feels trivial, consider combining with related work.

## Ticket Structure

Every implementation ticket should include:

| Section | Purpose |
|---------|---------|
| **Tasks** | Concrete steps to complete |
| **Acceptance Criteria** | How to verify it's done |
| **References** | Links to relevant architecture docs |
| **Notes** | Context, constraints, gotchas |

### Example

```markdown
## Tasks
- Create `src/confl/foo.py` module
- Implement `do_thing()` function
- Add tests

## Acceptance Criteria
- `uv run pytest` passes
- `confl foo` produces expected output

## References
- docs/architecture/cli-design.md — command structure

## Notes
- Keep it simple — no error retry logic yet
```

## Dependencies

Use `tk dep <ticket> <depends-on>` to establish order:

- **Foundational work first** — storage modules before commands that use them
- **Integration last** — wire things together after parts exist
- **Independent tickets can parallelize** — no artificial dependencies

```bash
# Example: login command depends on credentials storage
tk dep c-477a c-41a7
```

## Discovery Tickets

Use discovery tickets when something is **unclear or needs research**:

- Prefix with `DISCOVERY:` in the title
- Output is documentation + follow-up tickets
- Agent should NOT implement in the same ticket
- Good for: architecture decisions, library choices, API research

### Discovery Template

```markdown
## Questions to Answer
- How does X work?
- What library should we use for Y?
- What's the best approach for Z?

## Output
- Document findings in [location]
- File follow-up implementation tickets

## IMPORTANT
This is a DISCOVERY ticket. Research, document, file follow-ups, then STOP.
```

## Priority Guidelines

| Priority | When to use |
|----------|-------------|
| P0 | Foundational — blocks other work |
| P1 | Important — core functionality |
| P2 | Nice to have — not blocking |
| P3-P4 | Future — defer for now |

## Breaking Down Work

Ask these questions:

1. **Can this be split by layer?** (storage → commands → integration)
2. **Can this be split by feature?** (login vs logout vs status)
3. **Are there unknowns?** → File discovery ticket first
4. **What's the dependency chain?** → Foundation before features

### Good Breakdown Pattern

```
1. Storage/data layer (no deps)
2. Individual commands (depend on storage)
3. Integration/wiring (depends on multiple pieces)
4. Polish/extras (lowest priority)
```

## Reference Architecture Docs

Always point agents to relevant docs:

- `docs/architecture/design-principles.md` — CLI philosophy, agent-first design
- `docs/architecture/cli-design.md` — command structure, error handling
- `docs/architecture/configuration.md` — config and auth patterns
- `docs/architecture/content-formats.md` — input/output formats
- `docs/architecture/page-commands.md` — page entity details

## Asking Clarifying Questions

When filing tickets for someone else's ideas:

- **Ask one question at a time** — don't overwhelm
- **Propose breakdowns first** — get buy-in before filing
- **Enrich descriptions** — add detail based on architecture docs
- **Flag unknowns** — suggest discovery tickets for unclear areas

## Anti-Patterns

Avoid these:

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Huge tickets with many tasks | Break into focused pieces |
| Vague acceptance criteria | Specific, testable outcomes |
| Missing dependencies | Use `tk dep` to show order |
| Guessing at unclear requirements | File discovery ticket first |
| Tickets without doc references | Point to relevant architecture docs |
