---
id: c-2eaf
status: closed
deps: []
links: []
created: 2026-01-15T14:27:14Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# INVESTIGATION: Upgrade rich from 13.9.4 to 14.2.0

Investigate upgrading rich library from 13.9.4 to 14.2.0 and assess the effort required.

## Goal
Upgrade rich dependency to latest version (14.2.0) to get bug fixes, improvements, and new features.

## Investigation Tasks

### 1. Review Release Notes
- Check rich changelog/releases between 13.9.4 and 14.2.0
- Identify breaking changes
- Note new features we might benefit from
- Check deprecation warnings

### 2. Dependency Compatibility
- Check if rich 14.2.0 has new dependency requirements
- Verify compatibility with our Python version (3.11+)
- Check for conflicts with other dependencies

### 3. API Changes
- Review our usage of rich in the codebase:
  - Console output
  - Markdown rendering
  - Table formatting
  - Progress indicators (if used)
  - Syntax highlighting (if used)
- Check if any APIs we use have changed
- Search for deprecated usage patterns

### 4. Test Impact
- Update rich in local environment: `uv add 'rich>=14.2.0'`
- Run full test suite: `uv run pytest`
- Note any test failures
- Test CLI commands manually
- Check output formatting still looks good

### 5. Effort Assessment
Categorize the upgrade:
- **Simple**: No breaking changes, drop-in replacement (file single upgrade ticket)
- **Moderate**: Minor API changes, some code updates needed (file ticket with clear subtasks)
- **Complex**: Major refactoring required (break into multiple tickets)

## Output

### Document in ticket notes:
1. Summary of changes between versions
2. Breaking changes that affect us
3. Required code changes (if any)
4. Test results after upgrade
5. Effort estimate

### File follow-up tickets:
- **If simple**: Single "Upgrade rich to 14.2.0" implementation ticket
- **If moderate**: Create sub-tickets for each area that needs updates:
  - Update Console usage
  - Update Markdown rendering
  - Update Table formatting
  - Update tests
  - etc.
- **If complex**: Break down into multiple sub-tickets:
  - Sub-ticket for each breaking change
  - Sub-ticket for deprecated pattern updates
  - Sub-ticket for testing/validation
  - Final sub-ticket for completing the upgrade

**Use sub-tickets to break down work if upgrade requires multiple changes.**

## Acceptance Criteria
- Clear understanding of upgrade impact
- Tested locally with new version
- Effort properly assessed
- Appropriate follow-up tickets filed
- Recommendation on whether to upgrade now or defer

## References
- https://github.com/Textualize/rich/releases — release notes
- https://rich.readthedocs.io/ — documentation
- pyproject.toml — current dependency version
- `grep -r 'from rich' src/` — find our usage

## Notes
- rich is used for all terminal output/formatting
- Breaking changes could affect UX significantly
- Worth upgrading to get improvements and security fixes
- Consider if this is the right time or if we should defer


**2026-01-15T14:31:51Z**

Investigation complete - PROCEED WITH UPGRADE

## Summary
Analyzed upgrade from rich 13.9.4 to 14.2.0. This is a SIMPLE upgrade with minimal risk.

## Breaking Changes Analysis
1. Version 14.0.0: Empty NO_COLOR/FORCE_COLOR env vars now treated as disabled (was enabled)
   - Impact: LOW - More intuitive behavior, edge case only
2. Version 13.9.0: Dropped Python 3.7 support
   - Impact: NONE - We require Python 3.11+

## Our Rich Usage
- Console (basic output)
- Table (list commands)
- Markdown (page/blogpost show)
- Progress bars (upload/clone operations)

No API changes affect these usage patterns.

## Testing Results
✓ All 699 tests pass with rich 14.2.0
✓ Coverage maintained at 82.48%
✓ CLI help text renders correctly
✓ No visual regressions

## Benefits
- Bug fixes and performance improvements (13.8.0-14.2.0)
- Better traceback rendering for Python 3.11+ 
- Better terminal size detection on Windows
- Python 3.14 compatibility
- Removed typing_extensions dependency

## Recommendation
PROCEED - Drop-in replacement, no code changes needed.

## Next Steps
Filed implementation ticket c-6f92 for the actual upgrade.
