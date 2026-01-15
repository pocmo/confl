# confl

An unofficial command-line interface for Atlassian Confluence Cloud.

## What is this?

`confl` is a CLI tool for reading and editing Confluence pages directly from your terminal. It's designed to be scriptable and agent-friendly—no interactive editors by default, just straightforward commands that can be chained and automated.

## Quick Start

```bash
# Install
pipx install git+https://github.com/pocmo/confl.git

# Authenticate with API token
echo "$CONFLUENCE_TOKEN" | confl auth login --token --site yoursite.atlassian.net --email you@example.com

# List pages in a space
confl page list --space DEV

# Get a page by ID
confl page get <page-id>
```

See [Authentication](#authentication) and [Configuration](#configuration) for more details.

## Authentication

- **API Token** — for CI/automation (via environment variables or config file)
- **OAuth** — browser-based login for interactive use

## Configuration

Config lives in `~/.config/confl/`. Environment variables (`CONFL_*`) can override config file settings.

## Installation

```
pipx install git+https://github.com/pocmo/confl.git
```

## Commands

### search

Search for Confluence content using CQL (Confluence Query Language) or simple filters.

**Two modes of operation:**

1. **Simple filters** (for common cases):
```bash
confl search --text "API docs" --space DEV --type page --label draft
```

2. **Raw CQL query** (for power users):
```bash
confl search "space = DEV AND type = page ORDER BY lastmodified DESC"
```

**Examples:**

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

**Available filters:**
- `--text` — Search for text in content
- `--space` — Filter by space key
- `--type` — Filter by content type (page, blogpost, etc.)
- `--label` — Filter by label
- `--limit` — Maximum number of results (default: 25)
- `--json` — Output as JSON array

**CQL Basics:**

CQL supports powerful queries with operators and functions:
- `space = KEY` — Filter by space
- `type = page` — Filter by content type
- `label = draft` — Filter by label
- `text ~ "keyword"` — Text search
- `created >= now('-7d')` — Date filters
- `AND`, `OR`, `NOT` — Logical operators
- `ORDER BY lastmodified DESC` — Sorting

For complete CQL reference, see [Atlassian's CQL documentation](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/).

### comment

Manage comments on Confluence pages. Supports listing, viewing, creating, updating, and deleting both footer comments (page-level) and inline comments (specific locations).

**Commands:**

- `confl comment list` — List comments on a page or all comments
- `confl comment get` — Get comment details
- `confl comment add` — Add a new comment to a page or reply to another comment
- `confl comment update` — Update an existing comment's body
- `confl comment delete` — Delete a comment

**Examples:**

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

**Notes:**
- Comment body supports Markdown input which is automatically converted to Confluence storage format
- Use `--page` to comment on a page or `--parent` to reply to an existing comment
- Both footer comments (page-level) and inline comments (location-specific) are supported
- The `--include-inline` flag includes inline comments in list results

### blogpost

Manage blog posts in Confluence spaces. Blog posts are time-ordered content similar to pages but displayed chronologically.

**Commands:**

- `confl blogpost list` — List blog posts in a space
- `confl blogpost get` — Get blog post details and content
- `confl blogpost create` — Create a new blog post
- `confl blogpost update` — Update an existing blog post's content and/or title
- `confl blogpost delete` — Delete a blog post

**Examples:**

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

**Notes:**
- Blog posts use the same storage format as pages and support Markdown input/output
- Blog posts support attachments, labels, and comments (use corresponding commands with blog post IDs)
- Deletion moves blog posts to trash (soft delete) - they can be restored from the web UI
- Use `--raw` flag with create/update to provide content in Confluence storage format directly
- Blog posts appear in chronological order, making them ideal for release notes, announcements, and updates
