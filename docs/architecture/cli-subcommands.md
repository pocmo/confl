# CLI Subcommands Analysis

This document analyzes the Confluence Cloud REST API v2 to identify additional CLI subcommands beyond the currently implemented `page` entity.

## Current Implementation Status

### ✅ Implemented

#### P0 - Core Functionality
- **`auth`** - Authentication management (login, configure credentials)
- **`page`** - Page operations (get, list, create, update, delete, versions, restore)

#### P1 - Essential Extensions
- **`space`** - Space management (list, get, create, update, delete)
- **`attachment`** - File attachment management (list, get, upload, download, delete)
- **`label`** - Content labeling (list, add, remove, search)

#### P2 - Collaboration Features
- **`comment`** - Comments management (list, get, add, update, delete)
- **`blogpost`** - Blog post management (list, get, create, update, delete)
- **`search`** - Content search using CQL and simple filters

#### P3 - Advanced Features (Partial)
- ⚠️ **Version history** - Implemented as page subcommands (`page versions`, `page version`, `page restore`)

### ❌ Not Yet Implemented

#### P3 - Task Management
- **`task`** - Task tracking (list, get, update status) - Planned but not implemented

## API Entity Analysis

The Confluence Cloud REST API v2 provides 146 endpoints across 24 top-level entities. Below is the analysis of which entities make sense as CLI subcommands.

### High-Priority Entities (P1)

#### 1. ✅ `space` - Space Management
**Priority:** P1  
**Status:** ✅ **IMPLEMENTED**  
**API Paths:** 13 endpoints  
**Operations:** GET, POST, PUT, DELETE

**Rationale:** Spaces are the primary organizational unit in Confluence. Essential for discovering content and understanding context.

**Proposed Commands:**
- `confl space list` - List all spaces (with filtering by type: global/personal, status: current/archived)
- `confl space get <key|id>` - Get space details (name, key, homepage, description)
- `confl space create` - Create a new space (name, key, description)
- `confl space update <key|id>` - Update space details
- `confl space delete <key|id>` - Delete a space

**Key Use Cases:**
- Discover available spaces before creating/listing pages
- Automate space provisioning
- Retrieve space metadata for scripts
- Navigate space hierarchy

**Implementation Notes:**
- Support both space key (human-friendly: "DEV") and ID
- Default output: table with key, name, type, homepage URL
- `--json` flag for programmatic use

---

#### 2. ✅ `attachment` - File Attachment Management
**Priority:** P1  
**Status:** ✅ **IMPLEMENTED**  
**API Paths:** 9 endpoints  
**Operations:** GET, POST, DELETE (download, upload, delete)

**Rationale:** Attachments are commonly used in Confluence. Critical for documentation workflows (uploading images, PDFs, etc.).

**Proposed Commands:**
- `confl attachment list --page <id>` - List attachments on a page
- `confl attachment get <id>` - Get attachment metadata
- `confl attachment download <id> [--output FILE]` - Download attachment
- `confl attachment upload --page <id> --file PATH [--title TITLE]` - Upload file to page
- `confl attachment delete <id>` - Delete attachment

**Key Use Cases:**
- Upload images/diagrams when creating pages
- Download attachments for backup
- Bulk upload documentation assets
- List all attachments on a page

**Implementation Notes:**
- Use streaming for large file downloads
- Support stdin for upload (useful for piping)
- Show progress for large files
- Detect MIME type from file extension

---

#### 3. ✅ `label` - Content Labeling
**Priority:** P1  
**Status:** ✅ **IMPLEMENTED**  
**API Paths:** 4 endpoints  
**Operations:** GET (list labels and content by label)

**Rationale:** Labels are used for organization, search, and categorization. Useful for discovering related content.

**Proposed Commands:**
- `confl label list --page <id>` - List labels on a page
- `confl label add --page <id> <label>...` - Add one or more labels to a page
- `confl label remove --page <id> <label>` - Remove label from a page
- `confl label search <label>` - Find all pages with a given label

**Key Use Cases:**
- Tag pages during automation
- Find all pages with specific tag (e.g., "release-notes")
- Organize content programmatically
- Bulk labeling operations

**Implementation Notes:**
- Support multiple labels in single command
- `label search` shows pages, blogposts, attachments with that label
- Validate label names (no spaces, special chars)

---

### Medium-Priority Entities (P2)

#### 4. ✅ `comment` - Comments Management
**Priority:** P2  
**Status:** ✅ **IMPLEMENTED**  
**API Paths:** 10 endpoints (footer + inline comments)  
**Operations:** GET, POST, PUT, DELETE

**Rationale:** Comments facilitate collaboration. Useful for review workflows and feedback automation.

**Proposed Commands:**
- `confl comment list --page <id>` - List comments on a page (footer + inline)
- `confl comment get <id>` - Get comment details
- `confl comment add --page <id> --body TEXT` - Add comment to page
- `confl comment update <id> --body TEXT` - Update comment
- `confl comment delete <id>` - Delete comment

**Key Use Cases:**
- Automated review feedback
- Notification systems
- Approval workflows
- Discussion archival

**Implementation Notes:**
- Distinguish between footer comments (page-level) and inline comments (specific location)
- Support Markdown input for comment body
- Show comment thread hierarchy

---

#### 5. ✅ `blogpost` - Blog Post Management
**Priority:** P2  
**Status:** ✅ **IMPLEMENTED**  
**API Paths:** 17 endpoints  
**Operations:** GET, POST, PUT, DELETE

**Rationale:** Blog posts are similar to pages but time-ordered. Useful for teams using Confluence for announcements.

**Proposed Commands:**
- `confl blogpost list --space <key>` - List blog posts in space
- `confl blogpost get <id>` - Get blog post
- `confl blogpost create` - Create blog post
- `confl blogpost update <id>` - Update blog post
- `confl blogpost delete <id>` - Delete blog post

**Key Use Cases:**
- Publish release notes
- Automated announcements
- Newsletter publishing
- Team updates

**Implementation Notes:**
- Reuse page rendering logic (same storage format)
- Blog posts appear in chronological order
- Support all page features (attachments, labels, comments)

---

#### 6. ✅ `search` - Content Search
**Priority:** P2  
**Status:** ✅ **IMPLEMENTED**  
**API:** Use CQL (Confluence Query Language) via search endpoints

**Rationale:** Search is essential for discovering content. Enables advanced queries beyond simple listing.

**Proposed Commands:**
- `confl search <query>` - Search using CQL
- `confl search --text "keyword"` - Simple text search
- `confl search --space <key> --type page --label <label>` - Filtered search

**Key Use Cases:**
- Find pages matching criteria
- Discover content by keywords
- Filter by multiple dimensions (space, type, date, author)
- Export search results

**Implementation Notes:**
- Support CQL for power users
- Provide simple flags for common filters
- Output: table with title, space, type, URL
- Use API's built-in search (not implemented yet in API v2 - may need v1 fallback)

---

### Lower-Priority Entities (P3)

#### 7. ❌ `task` - Task Management
**Priority:** P3  
**Status:** ❌ **NOT IMPLEMENTED**  
**API Paths:** 2 endpoints  
**Operations:** GET, PUT (list tasks, update task status)

**Rationale:** Tasks in Confluence pages. Limited functionality but useful for teams tracking work in Confluence.

**Proposed Commands:**
- `confl task list` - List all tasks assigned to current user
- `confl task get <id>` - Get task details
- `confl task update <id> --status complete` - Mark task as complete/incomplete

**Key Use Cases:**
- Track assigned tasks
- Update task status in automation
- Generate task reports

---

#### 8. ✅ `version` - Version History
**Priority:** P3  
**Status:** ✅ **IMPLEMENTED** (as page subcommands)  
**API Paths:** Available under `/pages/{id}/versions` and similar

**Rationale:** Version history is useful for auditing and rollback. Can be accessed via page commands for now.

**Implemented Commands:**
- `confl page versions <id>` - List page versions
- `confl page version <id> <version-number>` - Get specific version
- `confl page restore <id> <version-number>` - Restore to specific version

**Implementation Notes:**
- Integrated into `page` commands rather than separate entity
- Show diff between versions (future enhancement)

---

### Entities NOT Recommended for CLI

#### `custom-content`
**Rationale:** App-specific content types. Too niche for general CLI. Apps should implement their own tooling.

#### `whiteboards`, `databases`, `embeds`, `folders`
**Rationale:** These are newer Confluence features with specialized UIs. CLI manipulation would be awkward and limited value. Focus on core content types first.

#### `app`, `data-policies`, `classification-levels`
**Rationale:** Admin/enterprise features. Not relevant for typical CLI users.

#### `space-permissions`, `space-roles`, `space-role-mode`
**Rationale:** Permission management is complex and risky in CLI. Web UI is more appropriate. May reconsider for advanced use cases.

#### `admin-key`
**Rationale:** Security-sensitive operation. Should not be exposed via CLI.

#### `users-bulk`, `user`
**Rationale:** User management belongs in Atlassian admin console, not Confluence CLI.

---

## Recommended Implementation Roadmap

### ✅ Phase 1: Core Extensions (P1) - COMPLETE
1. ✅ **`space`** - Essential for context and discovery
2. ✅ **`attachment`** - Critical for complete page workflows
3. ✅ **`label`** - High value for organization and search

### ✅ Phase 2: Collaboration Features (P2) - COMPLETE
4. ✅ **`comment`** - Enhance collaboration workflows
5. ✅ **`blogpost`** - Extend to blog content type
6. ✅ **`search`** - Advanced content discovery

### ⚠️ Phase 3: Advanced Features (P3) - PARTIAL
7. ✅ **Version history** - Integrated into `page` commands (`page versions`, `page version`, `page restore`)
8. ❌ **`task`** - Task tracking integration (not yet implemented - see ticket c-4e70)

---

## Common Workflow Patterns

### Pattern 1: Document Publishing Workflow
```bash
# Create page with image
confl page create --space DEV --title "Architecture Doc" --body-file doc.md
page_id=$(confl page get --space DEV --title "Architecture Doc" --json | jq -r .id)
confl attachment upload --page $page_id --file diagram.png
confl label add --page $page_id architecture design
```

### Pattern 2: Content Discovery
```bash
# Find all architecture documentation
confl label search architecture
confl space list --type global
confl page list --space DEV --label architecture
```

### Pattern 3: Backup and Migration
```bash
# Export space content
for page_id in $(confl page list --space DEV --json | jq -r '.[].id'); do
  confl page get $page_id --markdown > "$page_id.md"
  confl attachment list --page $page_id --json | jq -r '.[].id' | while read att_id; do
    confl attachment download $att_id --output "attachments/$att_id"
  done
done
```

### Pattern 4: Collaborative Review
```bash
# Get page, review, add feedback
confl page get 12345 > review.md
# ... make edits ...
confl page update 12345 --body-file review.md --message "Updated per review"
confl comment add --page 12345 --body "Reviewed and updated, LGTM"
```

---

## Design Consistency Patterns

All entity commands should follow these patterns (from cli-design.md):

1. **Entity-first structure:** `confl <entity> <action>`
2. **Common actions:** list, get, create, update, delete
3. **Output flags:** `--json`, `--markdown`, `--body-only`
4. **Pagination:** `--limit`, `--cursor` for large result sets
5. **Filtering:** Entity-specific filters via flags
6. **Reference types:** Support ID, URL, and human-friendly names where possible

---

## Implementation Status Summary

**All high and medium priority features (P0, P1, P2) have been implemented.** The CLI now provides comprehensive functionality for:
- Authentication management
- Page operations (including version history)
- Space management
- Attachment handling
- Label organization
- Comment workflows
- Blog post management
- Content search (CQL and simple filters)

**Remaining work:**
- P3: Task management subcommand (ticket c-4e70) - the only planned feature not yet implemented

---

## References

- **API.md** - Comprehensive API endpoint documentation
- **cli-design.md** - Command structure and design principles
- **page-commands.md** - Example entity implementation
- **OpenAPI spec** - docs/architecture/openapi-v2.v3-spec.json (146 endpoints analyzed)
