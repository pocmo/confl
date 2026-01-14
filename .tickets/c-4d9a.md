---
id: c-4d9a
status: closed
deps: []
links: []
created: 2026-01-14T20:44:08Z
type: chore
priority: 2
assignee: Sebastian Kaspari
---
# Remove unrelated markdown section from README

Clean up README.md by removing the markdown section that is not related to the confl project.

## Tasks
- Open README.md
- Identify and remove the markdown section that doesn't belong
- Ensure remaining content is relevant to confl CLI tool
- Keep README focused on project purpose, installation, and usage

## Acceptance Criteria
- Unrelated markdown section is removed from README.md
- README content is clean and focused on the project
- No functional content is accidentally removed

## References
- README.md

## Notes
- Simple cleanup task


**2026-01-14T21:13:58Z**

Cannot identify unrelated section in README. All content appears relevant to confl CLI. Added question to .ralph/questions.md requesting clarification from user on which section should be removed.

**2026-01-14T21:16:56Z**

CLARIFICATION: Remove the 'Markdown support documentation' section (features, usage, troubleshooting, limitations). This is an implementation detail, not user-facing documentation. Keep project description, authentication, configuration, and installation sections.

**2026-01-14T21:23:24Z**

Completed: Removed Markdown support documentation section (lines 24-163) from README. README now focused on project essentials: description, authentication, configuration, and installation.
