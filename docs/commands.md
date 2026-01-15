# Commands Reference

Complete reference for all `confl` commands.

## Global Options

These options work with all commands:

- `--profile PROFILE` — Use a specific configuration profile
- `--verbose` / `-v` — Show detailed operation information
- `--debug` — Show debug information including HTTP requests/responses

For details on global options, see [Configuration](configuration.md).

---

## search

Search for Confluence content using CQL (Confluence Query Language) or simple filters.

### Usage

**Two modes of operation:**

1. **Simple filters** (for common cases):
```bash
confl search --text "API docs" --space DEV --type page --label draft
```

2. **Raw CQL query** (for power users):
```bash
confl search "space = DEV AND type = page ORDER BY lastmodified DESC"
```

### Examples

```bash
# Search for text in a specific space
confl search --text "database migration" --space ENG

# Find all pages with a label
confl search --type page --label architecture

# Combine multiple filters
confl search --text "meeting notes" --space TEAM --type page

# Raw CQL for complex queries
confl search "space = MARKETING AND created >= now('-7d')"

# Get results as JSON
confl search --text "API" --json

# Limit number of results
confl search --text "documentation" --limit 10
```

### Options

- `--text TEXT` — Search for text in content
- `--space KEY` — Filter by space key
- `--type TYPE` — Filter by content type (page, blogpost, etc.)
- `--label LABEL` — Filter by label
- `--limit N` — Maximum number of results (default: 25)
- `--json` — Output as JSON array

### CQL Basics

CQL supports powerful queries with operators and functions:
- `space = KEY` — Filter by space
- `type = page` — Filter by content type
- `label = draft` — Filter by label
- `text ~ "keyword"` — Text search
- `created >= now('-7d')` — Date filters
- `AND`, `OR`, `NOT` — Logical operators
- `ORDER BY lastmodified DESC` — Sorting

For complete CQL reference, see [Atlassian's CQL documentation](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/).

---

## auth

Manage authentication credentials and profiles.

### Commands

- `confl auth login` — Store credentials in config file
- `confl auth logout` — Remove credentials from config file
- `confl auth status` — Check authentication status
- `confl auth list` — List all configured profiles

### Examples

```bash
# Login with API token
echo "$API_TOKEN" | confl auth login --token \
  --site yoursite.atlassian.net \
  --email you@example.com

# Login with a specific profile
echo "$API_TOKEN" | confl auth login --token \
  --site dev.atlassian.net \
  --email dev@example.com \
  --profile dev

# Check authentication status
confl auth status

# List all profiles
confl auth list

# Logout (delete credentials)
confl auth logout

# Logout specific profile
confl auth logout --profile dev
```

For more details, see [Authentication](authentication.md) and [Configuration](configuration.md).

---

## page

Manage Confluence pages.

### Commands

- `confl page list` — List pages in a space
- `confl page get` — Get page content and metadata
- `confl page create` — Create a new page
- `confl page update` — Update an existing page
- `confl page delete` — Delete a page
- `confl page versions` — List all versions of a page
- `confl page version` — Get a specific version of a page
- `confl page restore` — Restore a page to a specific version

### Examples

```bash
# List pages in a space
confl page list --space DEV

# Get a page by ID
confl page get 123456

# Get page by URL
confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/123456/Page+Title"

# Get page content as markdown
confl page get 123456 --markdown

# Get page as raw storage format
confl page get 123456 --raw

# Create a new page
confl page create --space DEV --title "New Page" --body "# Content"

# Create page from markdown file
confl page create --space DEV --title "Documentation" --body-file doc.md

# Create page from stdin
cat doc.md | confl page create --space DEV --title "Documentation"

# Create page under parent
confl page create --space DEV --title "Sub Page" --parent 123456 --body "# Content"

# Update page content
confl page update 123456 --body "# Updated content"

# Update page title
confl page update 123456 --title "New Title"

# Update both title and content
confl page update 123456 --title "New Title" --body "# Updated content"

# Delete a page
confl page delete 123456

# List all versions of a page
confl page versions 123456

# Get a specific version
confl page version 123456 --version 5

# Restore to a previous version
confl page restore 123456 --version 5

# Get results as JSON
confl page list --space DEV --json
confl page get 123456 --json
```

### Notes

- Page body supports Markdown input which is automatically converted to Confluence storage format
- Use `--raw` flag to provide content in Confluence storage format directly
- Deletion moves pages to trash (soft delete) — they can be restored from the web UI
- Restore creates a new version with the content from the specified version
- **Images and attachments are not displayed in terminal output** — use `--json` to see attachment references

---

## space

Manage Confluence spaces.

### Commands

- `confl space list` — List spaces
- `confl space get` — Get space details

### Examples

```bash
# List all spaces
confl space list

# Get details for a specific space
confl space get DEV

# Get results as JSON
confl space list --json
confl space get DEV --json
```

---

## attachment

Manage attachments on Confluence pages.

### Commands

- `confl attachment list` — List attachments on a page
- `confl attachment get` — Get attachment metadata
- `confl attachment download` — Download an attachment
- `confl attachment upload` — Upload a file as an attachment
- `confl attachment delete` — Delete an attachment

### Examples

```bash
# List attachments on a page
confl attachment list --page 123456

# Download an attachment
confl attachment download ATTACH_ID --output file.pdf

# Upload an attachment
confl attachment upload --page 123456 --file document.pdf

# Upload with custom title/comment
confl attachment upload --page 123456 --file doc.pdf --title "Q4 Report" --comment "Updated version"

# Delete an attachment
confl attachment delete ATTACH_ID

# Get results as JSON
confl attachment list --page 123456 --json
```

---

## label

Manage labels on Confluence content.

### Commands

- `confl label list` — List labels on a page or blogpost
- `confl label add` — Add a label to content
- `confl label remove` — Remove a label from content

### Examples

```bash
# List labels on a page
confl label list --page 123456

# Add a label to a page
confl label add --page 123456 --label "documentation"

# Add multiple labels
confl label add --page 123456 --label "draft" --label "review-needed"

# Remove a label
confl label remove --page 123456 --label "draft"

# Get results as JSON
confl label list --page 123456 --json
```

---

## comment

Manage comments on Confluence pages.

### Commands

- `confl comment list` — List comments on a page or all comments
- `confl comment get` — Get comment details
- `confl comment add` — Add a new comment to a page or reply to another comment
- `confl comment update` — Update an existing comment's body
- `confl comment delete` — Delete a comment

### Examples

```bash
# List all comments on a page
confl comment list --page 123456

# List comments with inline comments included
confl comment list --page 123456 --include-inline

# Get a specific comment
confl comment get 789012

# View comment body as markdown
confl comment get 789012 --markdown

# Add a comment to a page
confl comment add --page 123456 --body "Great work on this page!"

# Add a comment from a markdown file
confl comment add --page 123456 --body-file comment.md

# Reply to another comment
confl comment add --parent 789012 --body "I agree with this point"

# Update a comment
confl comment update 789012 --body "Updated feedback"

# Delete a comment
confl comment delete 789012

# Get results as JSON
confl comment list --page 123456 --json
confl comment get 789012 --json
```

### Notes

- Comment body supports Markdown input which is automatically converted to Confluence storage format
- Use `--page` to comment on a page or `--parent` to reply to an existing comment
- Both footer comments (page-level) and inline comments (location-specific) are supported
- The `--include-inline` flag includes inline comments in list results
- **Images and attachments are not displayed in terminal output** — use `--json` to see attachment references

---

## blogpost

Manage blog posts in Confluence spaces.

### Commands

- `confl blogpost list` — List blog posts in a space
- `confl blogpost get` — Get blog post details and content
- `confl blogpost create` — Create a new blog post
- `confl blogpost update` — Update an existing blog post's content and/or title
- `confl blogpost delete` — Delete a blog post

### Examples

```bash
# List all blog posts in a space
confl blogpost list --space DEV

# Get a specific blog post
confl blogpost get 654321

# Get blog post by URL
confl blogpost get "https://company.atlassian.net/wiki/spaces/DEV/blogposts/654321/Title"

# Get blog post content as markdown
confl blogpost get 654321 --markdown

# Get blog post as raw storage format
confl blogpost get 654321 --raw

# Create a new blog post
confl blogpost create --space DEV --title "Release Notes v1.0" --body "# New Features..."

# Create blog post from a markdown file
confl blogpost create --space DEV --title "Announcement" --body-file post.md

# Create blog post from stdin
cat post.md | confl blogpost create --space DEV --title "Update"

# Update blog post content
confl blogpost update 654321 --body "# Updated content..."

# Update blog post title
confl blogpost update 654321 --title "New Title"

# Update both title and content
confl blogpost update 654321 --title "New Title" --body "# Updated..."

# Delete a blog post
confl blogpost delete 654321

# Get results as JSON
confl blogpost list --space DEV --json
confl blogpost get 654321 --json
```

### Notes

- Blog posts use the same storage format as pages and support Markdown input/output
- Blog posts support attachments, labels, and comments (use corresponding commands with blog post IDs)
- Deletion moves blog posts to trash (soft delete) - they can be restored from the web UI
- Use `--raw` flag with create/update to provide content in Confluence storage format directly
- Blog posts appear in chronological order, making them ideal for release notes, announcements, and updates
- **Images and attachments are not displayed in terminal output** — use `--json` to see attachment references

---

## See Also

- [Getting Started Guide](getting-started.md) — Step-by-step walkthrough
- [Authentication](authentication.md) — Setting up API tokens
- [Configuration](configuration.md) — Config files and profiles
