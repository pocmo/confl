# Open Questions

_Note: This file previously contained design questions that have all been resolved in implementation. See the sections below for current status._

## Resolved Questions

All questions from the initial design phase have been addressed:

### Search ✅
- **Decision**: Uses CQL with simple filter options
- **Implementation**: `confl search` supports both raw CQL queries and simple filters (--text, --space, --type, --label)
- **Pagination**: Uses --limit flag (default 25)

### Space Commands ✅
- **Decision**: Full CRUD operations
- **Implementation**: list, get, create, update, delete commands
- **Permissions**: API returns spaces based on user permissions

### Pagination ✅
- **Decision**: Uses --limit flag
- **Implementation**: All list commands support --limit (default 25)

### Page Lookup ✅
- **Decision**: Supports page ID or full URL
- **Implementation**: `confl page get <id|url>`
- **Note**: Title-based lookup not implemented (use `confl search --text "title" --space KEY` instead)

### Attachments ✅
- **Decision**: Upload from local file system
- **Implementation**: `confl attachment upload --page <id> --file <path>`

### Comments ✅
- **Decision**: Page-level comments with threading via replies
- **Implementation**: Full CRUD operations: list, get, add (with --reply-to for threading), update, delete

### Content Conversion ✅
- **Decision**: Custom converter handling most common storage format elements
- **Implementation**: Markdown conversion with HTML fallback for complex/unsupported elements
- **See**: docs/architecture/markdown-conversion.md and storage-format-feature-gaps.md

## Current Questions

_Add new design questions here as they arise._
