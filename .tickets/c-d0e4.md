---
id: c-d0e4
status: open
deps: [c-3dd2]
links: []
created: 2026-01-15T07:47:23Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Audit and identify missing/outdated documentation in docs/

Review docs/ to identify missing, incomplete, or outdated documentation and file follow-up tickets.

## Tasks
- Review all existing documentation in docs/
- Compare documentation against actual implementation:
  - Are commands documented correctly?
  - Are new features/flags documented?
  - Are examples up-to-date?
  - Are architectural docs accurate?
- Identify missing documentation:
  - Commands that exist but aren't documented
  - Features that aren't explained
  - Common use cases/workflows not covered
  - Troubleshooting guides needed
  - API/developer docs for contributors
- Check README links:
  - Do all README links to docs/ work?
  - Are the right docs linked from README?
  - Are any important docs not linked?
- Create a documentation gap analysis:
  - List what exists and its status (✅ good, ⚠️ needs update, ❌ missing)
  - Prioritize gaps (critical vs nice-to-have)
  - Estimate effort for each gap
- File follow-up tickets:
  - For small updates: single ticket per doc file
  - For large missing sections: separate tickets
  - For new documentation areas: discovery or implementation tickets
  - Group related items where appropriate

## Acceptance Criteria
- Complete audit of docs/ directory
- Documentation gap analysis created (can be in ticket notes or temp file)
- Follow-up tickets filed for all significant gaps
- Priorities assigned appropriately
- No ticket for trivial issues (just fix them in this ticket)

## References
- docs/ — all documentation to audit
- README.md — check links and coverage
- c-3dd2 — README restructure (should complete first)
- src/confl/ — actual implementation to verify against

## Notes
- This depends on c-3dd2 completing so README structure is clear
- Focus on user-facing docs first, then contributor docs
- Consider what questions users/contributors would have
- Look at architecture docs too (may be outdated as code evolved)

