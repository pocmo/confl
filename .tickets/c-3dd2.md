---
id: c-3dd2
status: open
deps: []
links: []
created: 2026-01-15T07:46:22Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Restructure README - move detailed content to docs/

Break down README.md into focused overview + separate detailed documentation files in docs/.

## Problem
README should be concise and focused on the essentials. Detailed content should live in docs/ with links from README.

## Tasks
- Review current README.md and identify sections to move
- Create separate documentation files in docs/ for detailed content:
  - docs/authentication.md — detailed auth methods, token setup, OAuth info
  - docs/configuration.md — config file details, environment variables, precedence
  - docs/commands.md — complete command reference with all options
  - docs/installation.md — detailed install methods, troubleshooting
  - (others as needed based on current README)
- Keep in README (should be brief):
  - Project description and purpose (1-2 paragraphs)
  - Quick Start section (already planned in c-2735)
  - Links to detailed docs
  - Link to Getting Started guide
  - Maybe: Basic usage examples (very short)
  - Contributing, License sections
- Update README to link to new doc files
- Ensure docs/ has clear structure and navigation

## Acceptance Criteria
- README.md is concise (ideally under 200 lines)
- All detailed content moved to appropriate docs/ files
- Links from README to detailed docs work
- No information is lost in the restructure
- docs/ files are well-organized and easy to navigate

## References
- README.md — current content to restructure
- c-2735 — Quick Start section ticket
- c-5103 — Getting Started guide ticket

## Notes
- README should be scannable and get users started quickly
- Detailed docs are for deep dives
- Keep README maintenance-friendly (less to update)

