---
id: c-56ee
status: closed
deps: []
links: []
created: 2026-01-14T15:06:15Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# DISCOVERY: Define testing strategy for Confluence API

Research and document how we will test confl without hitting a production Confluence system.

## Goal
Create `docs/architecture/testing.md` that documents our testing strategy.

## Questions to Answer
- How do we mock/stub Confluence API responses?
- What mocking library fits best with httpx? (respx, pytest-httpx, etc.)
- Do we use VCR-style recording/playback or hand-crafted fixtures?
- How do we structure test fixtures (API responses)?
- What's our strategy for unit vs integration tests?

## Output
- Create `docs/architecture/testing.md` with the decided strategy
- File follow-up implementation tickets for any setup work needed (e.g., "Add respx for HTTP mocking")

## Constraints
- Must work offline (no real API calls in CI)
- Should be simple for agents to write tests
- Follow existing patterns in docs/architecture/

## References
- docs/architecture/design-principles.md — agent-first design philosophy
- Existing httpx dependency in pyproject.toml

## IMPORTANT
This is a DISCOVERY ticket. Research, document findings in testing.md, file follow-up tickets, then STOP. Do not implement the testing infrastructure in this ticket.


## Notes

**2026-01-14T15:51:09Z**

Research complete. Created docs/architecture/testing.md documenting strategy:
- pytest-httpx for HTTP mocking (simple, pytest-native)
- Hand-crafted fixtures (no VCR cassettes)
- Mock at HTTP layer, not at API wrapper level
- Unit tests for functions, integration tests for commands
- Fixtures in conftest.py for reusable responses
