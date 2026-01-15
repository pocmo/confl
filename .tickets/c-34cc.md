---
id: c-34cc
status: closed
deps: []
links: []
created: 2026-01-15T08:08:22Z
type: task
priority: 4
assignee: Sebastian Kaspari
---
# Create architecture documentation index

Create docs/architecture/README.md to help readers navigate architecture docs.

Tasks:
- Create docs/architecture/README.md
- Categorize docs by purpose:
  - Core Principles: design-principles.md, goals.md
  - Implemented Features: cli-design.md, page-commands.md, configuration.md, testing.md, content-formats.md
  - Feature Analysis: cli-subcommands.md, storage-format-feature-gaps.md, cli-ux-improvements.md
  - Technical Details: content-rendering.md, markdown-conversion.md, atlassian-document-format.md
  - Proposals: oauth-browser-login.md
  - Reference: API.md, openapi-v2.v3-spec.json
  - Process: filing-tickets.md
- Add one-line description for each doc
- Suggest reading order for new contributors
- Link from main README.md

Example structure:
```markdown
# Architecture Documentation

## Start Here
- design-principles.md - Core CLI philosophy
- cli-design.md - Command structure

## Implemented Features
- page-commands.md - Page entity design
...
```

Acceptance:
- Clear navigation guide for architecture docs
- New contributors know where to start
- Docs categorized by purpose

Reference: arch_audit_findings.md


## Notes

**2026-01-15T09:46:07Z**

Completed: Architecture index README already existed with comprehensive categorization and navigation. Added missing link from main README.md to docs/architecture/README.md.
