---
id: c-ded1
status: closed
deps: []
links: []
created: 2026-01-14T15:04:39Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# Setup code coverage with pytest-cov

Add code coverage reporting to the test suite.

## Tasks
- Add pytest-cov to dev dependencies
- Configure coverage settings in pyproject.toml (source paths, branch coverage, etc.)
- Add coverage report to pytest runs (consider pytest.ini or pyproject.toml [tool.pytest.ini_options])
- Optionally set a minimum coverage threshold

## Acceptance Criteria
- `uv run pytest --cov` shows coverage report
- Coverage is measured for src/confl/ package

## Notes
- Keep it simple — just terminal report for now, no HTML or CI integration needed


**2026-01-14T15:54:17Z**

Completed: Added pytest-cov dependency, configured coverage in pyproject.toml with branch coverage, terminal reporting, and 97.14% coverage baseline
