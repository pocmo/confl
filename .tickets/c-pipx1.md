---
id: c-pipx1
status: closed
deps: []
links: []
created: 2026-01-23T18:58:00Z
type: bug
priority: 0
assignee: Sebastian Kaspari
---
# BUG: confl whoami fails when installed via pipx

The 'confl whoami' command fails when confl is installed via pipx.

## Bug Description
User installed confl via pipx and encounters an error when running `confl whoami`.

**Error details needed**: The error message was not fully captured in the initial report. Need to reproduce and document the exact error.

## Environment
- Installation method: pipx
- Command attempted: `confl whoami`

## Tasks
- Reproduce the issue with pipx installation:
  ```bash
  pipx install confl
  confl whoami
  ```
- Document the exact error message
- Investigate root cause:
  - Is it a missing dependency in pipx environment?
  - Is it a configuration issue?
  - Is it related to space whoami bug (c-28fd)?
  - Is there an import error or packaging issue?
  - Check if command exists vs command fails
- Compare with local development install (`uv run confl whoami`)
- Fix the issue for pipx installations
- Test that fix works with pipx
- Update installation docs if special steps needed

## Acceptance Criteria
- `confl whoami` works correctly when installed via pipx
- Error is fixed at root cause
- No pipx-specific workarounds needed
- Installation instructions updated if necessary
- All commands work in pipx environment

## References
- c-28fd — existing space whoami bug (may be related)
- pyproject.toml — packaging configuration and entry points
- Installation documentation

## Notes
- pipx creates isolated virtualenvs per tool
- May be environment/dependency issue specific to pipx
- Could be entry point configuration issue in pyproject.toml
- Need full error message to diagnose properly
- This affects real users installing from PyPI
- User's error output wasn't fully shown - ask for complete error if needed

**2026-01-23T18:59:07Z**

Fixed: Moved markdownify from dev to runtime dependencies. The issue was that converter.py imports from markdownify and bs4 (which is a transitive dep of markdownify), but markdownify was incorrectly in dev dependencies. When installing with pipx (production install), these deps were missing, causing ModuleNotFoundError on any confl command that imports converter.py (all commands via blogpost import). Tested with pipx install - all commands now work.
