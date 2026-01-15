---
id: c-df0c
status: closed
deps: []
links: []
created: 2026-01-15T06:34:11Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Add progress indicators for long operations

Show progress spinners for long-running operations: uploading/downloading large attachments, creating pages with complex content. Only show when stdout is a TTY. From cli-ux-improvements.md - H1


## Notes

**2026-01-15T07:17:57Z**

Completed: Added progress spinners to upload/download attachments and create/update page operations. Uses Rich Progress with SpinnerColumn. Only shows when stdout is TTY and not JSON output. Transient progress ensures clean output. Added 6 tests verifying functionality.
