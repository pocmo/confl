---
id: c-b8dc
status: closed
deps: []
links: []
created: 2026-01-15T06:33:57Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Add human-readable sizes and timestamps

Format attachment sizes as human-readable (1.2 MB instead of bytes), use relative timestamps (2 hours ago) in list outputs, and format durations. From cli-ux-improvements.md - H4


## Notes

**2026-01-15T07:12:50Z**

Completed: Added human-readable formatting utilities
- Created formatters.py module with format_file_size(), format_relative_time(), and format_duration()
- Updated attachment commands to use centralized file size formatter (was already human-readable, now consistent)
- Updated page, blogpost, and comment list commands to show relative timestamps (e.g., '2 hours ago' instead of '2024-01-15')
- Updated page and blogpost metadata display to use relative timestamps
- Added 18 comprehensive tests covering all formatting functions
- All 542 tests pass
