---
id: c-ac19
status: closed
deps: []
links: []
created: 2026-01-15T07:52:11Z
type: bug
priority: 0
assignee: Sebastian Kaspari
---
# Fix ruff formatting/linting failures in automation

CI is failing again due to ruff formatting or linting issues. Need to fix and ensure it doesn't regress.

## Bug Description
Ruff is failing in GitHub Actions CI, likely due to unformatted code or linting violations being committed.

## Tasks
- Run `uv run ruff format .` to format all Python files
- Run `uv run ruff check --fix .` to fix auto-fixable linting issues
- Run `uv run ruff format --check .` to verify formatting passes
- Run `uv run ruff check .` to verify no linting errors remain
- Review any remaining issues that can't be auto-fixed
- Commit all formatting and linting fixes
- Verify CI passes

## Acceptance Criteria
- `uv run ruff format --check .` exits with code 0
- `uv run ruff check .` exits with code 0
- CI passes ruff checks
- All Python files are properly formatted and linted

## References
- .ralph/prompt.md — ruff commands
- c-1e01 — previous ruff formatting fix

## Notes
- Must run both format and check commands
- This keeps happening - agents need to run ruff before committing
- CI should catch this but we need to fix it promptly


**2026-01-15T07:58:52Z**

Fixed all ruff linting errors: combined nested if statements (SIM102) and converted if-else to ternary operators (SIM108). All checks now pass.
