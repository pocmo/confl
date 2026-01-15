---
id: c-08ff
status: open
deps: []
links: []
created: 2026-01-15T08:14:32Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Simplify project structure section in CONTRIBUTING.md

Remove detailed file-by-file project structure from CONTRIBUTING.md. Keep only high-level important folders.

## Problem
Documenting individual files in CONTRIBUTING.md is maintenance overhead and quickly becomes outdated. Only important folders should be mentioned.

## Tasks
- Review the project structure section in CONTRIBUTING.md
- Remove detailed file-by-file listings
- Keep only high-level important directories:
  - src/confl/ - Main package
  - tests/ - Test suite
  - docs/ - Documentation
  - .ralph/ - Ralph agent implementation
  - .tickets/ - Ticket system
  - (any other top-level important directories)
- Add brief description of what each directory contains
- Remove individual file listings that will change frequently

## Example format:
```markdown
## Project Structure

```
confl/
├── src/confl/       # Main package - CLI, API client, business logic
├── tests/           # Test suite
├── docs/            # Documentation and architecture docs
├── .ralph/          # Ralph agent loop implementation
├── .tickets/        # Ticket system (tk)
└── pyproject.toml   # Project configuration
```
```

## Acceptance Criteria
- Project structure section is simplified
- Only lists important top-level directories
- Brief descriptions added for each directory
- Detailed file listings removed
- Section is maintainable and won't require frequent updates

## References
- CONTRIBUTING.md — file to update

## Notes
- Focus on orientation, not exhaustive listing
- Contributors can explore the codebase themselves
- Keep it high-level and stable

