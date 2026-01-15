---
id: c-a0ba
status: closed
deps: []
links: []
created: 2026-01-15T08:14:44Z
type: task
priority: 3
assignee: Sebastian Kaspari
---
# Increase test coverage for formatter modules

Add tests for formatting code to improve coverage completeness.

Current coverage gaps:
- formatters.py: 4.76% coverage
- table_formatter.py: 16.07% coverage

These are pure functions and easy to test. Current gaps are mostly:
- Display formatting functions
- Edge cases in table rendering
- Relative time formatting

Tests to add:
- Unit tests for format_relative_time() with various timestamps
- Unit tests for table_formatter functions (create_table, sort_items, add_column_with_ellipsis)
- Edge cases: empty data, very long text, special characters

Priority: P3 (nice to have) - These are display functions with low risk, but completing coverage is good practice.

Reference: docs/architecture/senior-review-findings.md Finding 3.1


## Notes

**2026-01-15T08:43:41Z**

Completed: Added comprehensive tests for formatter modules. All formatter modules now have 100% test coverage.
