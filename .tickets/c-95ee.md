---
id: c-95ee
status: open
deps: []
links: []
created: 2026-01-14T15:04:25Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# Setup pytest for testing

Add pytest as a dev dependency and create the test infrastructure.

## Tasks
- Add pytest to dev dependencies in pyproject.toml (use [project.optional-dependencies] or [dependency-groups])
- Create tests/ directory structure with __init__.py and conftest.py
- Add a simple smoke test that imports confl and verifies the CLI app exists
- Verify with: uv run pytest

## Acceptance Criteria
- `uv run pytest` runs successfully
- At least one passing test exists

## Reference
- Tech stack uses uv for dependency management (see AGENTS.md)

