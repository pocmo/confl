---
id: c-e3c6
status: open
deps: []
links: []
created: 2026-01-15T08:08:03Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Update cli-subcommands.md with implementation status

Add status markers to cli-subcommands.md to show what's implemented vs planned.

The document shows Phase 1/2/3 roadmap but Phases 1 & 2 are now complete. Update to reflect reality:

Tasks:
- Add status markers (✅/❌/⚠️) to each entity section
- Update 'Implementation Status' section at top
- Update roadmap section to show completed phases
- Note that task subcommand is only remaining P1-P2 item not implemented

Current state:
- ✅ P0: auth, page
- ✅ P1: space, attachment, label  
- ✅ P2: comment, blogpost, search
- ❌ P3: task (not implemented)
- ⚠️ P3: version (implemented as page subcommands, not separate entity)

Acceptance:
- Document clearly shows implemented vs planned status
- Roadmap reflects current state
- No misleading information about what exists

Reference: arch_audit_findings.md

