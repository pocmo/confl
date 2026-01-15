# Getting Started with confl

Welcome! This guide will walk you through installing, configuring, and using `confl` to manage your Confluence content from the command line.

## What is confl?

`confl` is an unofficial CLI tool for Atlassian Confluence Cloud that lets you read, create, and edit Confluence pages directly from your terminal. It's designed to be:

- **Scriptable** — All commands can be automated and chained together
- **Agent-friendly** — No interactive prompts, just straightforward commands
- **Flexible** — Works equally well for humans and CI/automation

## Installation

### Option 1: Using pipx (Recommended)

The easiest way to install `confl` is using [pipx](https://pipx.pypa.io/), which installs Python applications in isolated environments:

```bash
pipx install git+https://github.com/pocmo/confl.git
```

### Option 2: Using uv

If you use [uv](https://docs.astral.sh/uv/) for Python project management:

```bash
uv tool install git+https://github.com/pocmo/confl.git
```

### Option 3: Using pip

You can also install with pip (though pipx is preferred to avoid dependency conflicts):

```bash
pip install git+https://github.com/pocmo/confl.git
```

### Option 4: From Source

For development or to use the latest unreleased features:

```bash
git clone https://github.com/pocmo/confl.git
cd confl
uv sync
uv run confl --help
```

### Verify Installation

Once installed, verify that `confl` is available:

```bash
confl --help
```

You should see the command help output with available commands.

## Authentication Setup

Before you can use `confl`, you need to authenticate with your Confluence site. There are two methods: **API Token** (recommended for automation) and **OAuth** (for interactive use).

### Method 1: API Token (Recommended)

API tokens are ideal for both personal use and automation. Here's how to set one up:

#### 1. Create an API Token

1. Go to [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a label (e.g., "confl CLI")
4. Copy the token (you won't be able to see it again)

#### 2. Login with the Token

You can authenticate in two ways:

**Interactive (token from stdin):**

```bash
confl auth login --token --site yoursite.atlassian.net --email you@example.com
```

When prompted, paste your API token and press Enter.

**Non-interactive (pipe the token):**

```bash
echo "your-api-token" | confl auth login --token --site yoursite.atlassian.net --email you@example.com
```

#### 3. Verify Authentication

Check that authentication is working:

```bash
confl auth status
```

You should see your site and email information.

### Method 2: OAuth (Browser-based)

For interactive use, you can use OAuth which opens your browser:

```bash
confl auth login
```

This will:
1. Open your browser to Atlassian's login page
2. Ask you to authorize the application
3. Store credentials locally

### For CI/Automation: Environment Variables

In CI environments or automated scripts, you can skip the login step by setting environment variables:

```bash
export CONFL_SITE="yoursite.atlassian.net"
export CONFL_TOKEN="your-api-token"
export CONFL_EMAIL="you@example.com"
```

When these are set, `confl` will automatically use them—no `auth login` needed.

## Basic Commands

Now that you're authenticated, let's explore the core commands.

### Listing Pages in a Space

See all pages in a Confluence space:

```bash
confl page list --space DEV
```

Example output:
```
┌──────────────┬────────────────────────────┬────────────┬─────────────────────┐
│ ID           │ Title                      │ Status     │ Last Modified       │
├──────────────┼────────────────────────────┼────────────┼─────────────────────┤
│ 123456       │ API Documentation          │ current    │ 2024-12-15 10:30:00 │
│ 123457       │ Architecture Overview      │ current    │ 2024-12-14 15:45:00 │
│ 123458       │ Getting Started Guide      │ current    │ 2024-12-13 09:20:00 │
└──────────────┴────────────────────────────┴────────────┴─────────────────────┘
```

### Getting a Page by ID

Retrieve a specific page's content:

```bash
confl page get 123456
```

This displays the page in human-readable markdown format. To get the raw storage format:

```bash
confl page get 123456 --raw
```

For JSON output (useful in scripts):

```bash
confl page get 123456 --json
```

### Getting a Page by URL

You can also fetch pages using their full Confluence URL:

```bash
confl page get "https://yoursite.atlassian.net/wiki/spaces/DEV/pages/123456/API+Documentation"
```

### Searching for Content

Search across all your Confluence content:

```bash
# Simple text search in a space
confl search --text "API documentation" --space DEV

# Search with filters
confl search --text "meeting notes" --type page --label draft

# Raw CQL query for advanced searches
confl search "space = DEV AND created >= now('-7d') ORDER BY lastmodified DESC"
```

## Common Workflows

### Creating a New Page

Create a page from markdown content:

```bash
confl page create --space DEV --title "My New Page" --body "# Hello\n\nThis is my page content."
```

Create from a markdown file:

```bash
confl page create --space DEV --title "API Guide" --body-file api-guide.md
```

Create from stdin (useful in pipelines):

```bash
cat page-content.md | confl page create --space DEV --title "Release Notes"
```

Create a child page under another page:

```bash
confl page create --space DEV --title "Sub Page" --parent 123456 --body "Child page content"
```

### Updating a Page

Update the content of an existing page:

```bash
confl page update 123456 --body "# Updated content\n\nNew information here."
```

Update from a file:

```bash
confl page update 123456 --body-file updated-content.md
```

Update the title:

```bash
confl page update 123456 --title "New Page Title"
```

Update both title and content:

```bash
confl page update 123456 --title "New Title" --body-file content.md
```

### Working with Attachments

Upload a file to a page:

```bash
confl attachment upload 123456 diagram.png
```

Upload and set as page thumbnail:

```bash
confl attachment upload 123456 cover.jpg --thumbnail
```

List attachments on a page:

```bash
confl attachment list --page 123456
```

Download an attachment:

```bash
confl attachment download att-789012 -o downloaded-file.pdf
```

### Managing Comments

List comments on a page:

```bash
confl comment list --page 123456
```

Add a comment to a page:

```bash
confl comment add --page 123456 --body "Great documentation!"
```

Reply to an existing comment:

```bash
confl comment add --parent comment-789 --body "Thanks for the feedback!"
```

### Working with Blog Posts

List blog posts in a space:

```bash
confl blogpost list --space UPDATES
```

Create a blog post (ideal for release notes, announcements):

```bash
confl blogpost create --space UPDATES --title "Release v1.0" --body-file release-notes.md
```

### Managing Labels

Add labels to a page:

```bash
confl label add 123456 documentation api draft
```

List labels on a page:

```bash
confl label list --page 123456
```

Remove a label:

```bash
confl label remove 123456 draft
```

## Configuration Options

### Config File Location

Configuration is stored in `~/.config/confl/`:

- `credentials.toml` — Authentication credentials
- `config.toml` — User preferences (if you create it)

### Environment Variables

You can override any configuration using environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `CONFL_SITE` | Confluence site domain | `yoursite.atlassian.net` |
| `CONFL_TOKEN` | API token | `ATATT3xFfG...` |
| `CONFL_EMAIL` | Email for API token auth | `you@example.com` |

### Configuration Precedence

When multiple sources provide the same setting, `confl` uses this order:

1. **Command-line flags** (highest priority)
2. **Environment variables** (`CONFL_*`)
3. **Config file** (`~/.config/confl/`)

This means you can set defaults in your config file and override them with environment variables or flags as needed.

## Output Formats

Most commands support multiple output formats:

### Human-Readable (Default)

By default, `confl` uses Rich formatting for beautiful terminal output:

```bash
confl page get 123456
```

### JSON (For Scripts)

Add `--json` to get machine-readable JSON:

```bash
confl page get 123456 --json
```

This is perfect for use in scripts, CI/CD pipelines, or with tools like `jq`:

```bash
confl page list --space DEV --json | jq '.[].title'
```

### Raw Storage Format

For page content, use `--raw` to get Confluence's native storage format:

```bash
confl page get 123456 --raw
```

This is useful if you need to work with Confluence-specific formatting.

### Markdown

Most content commands support `--markdown` to convert Confluence storage format to markdown:

```bash
confl page get 123456 --markdown
confl comment get 789 --markdown
```

## Troubleshooting

### "Authentication failed" or "401 Unauthorized"

**Problem:** Your credentials are invalid or expired.

**Solution:**
1. Verify your token is still valid at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Check your site URL is correct (should be `yoursite.atlassian.net`, not the full URL)
3. Re-run `confl auth login --token` with correct credentials

### "Space not found" or "Page not found"

**Problem:** The space key or page ID doesn't exist or you don't have access.

**Solution:**
1. Verify the space key is correct (use `confl space list` to see available spaces)
2. Check the page ID (look in the URL when viewing the page in your browser)
3. Ensure you have permission to access the space/page

### "Connection refused" or network errors

**Problem:** Can't reach the Confluence API.

**Solution:**
1. Check your internet connection
2. Verify the site URL is correct
3. Check if your organization has firewall rules blocking API access

### Commands not working as expected

**Problem:** Unexpected behavior or errors.

**Solution:**
1. Make sure you have the latest version: `pipx upgrade confl`
2. Check command help: `confl <command> --help`
3. Try with `--json` flag to see raw API responses
4. Check the [GitHub issues](https://github.com/pocmo/confl) for known problems

### Shell special characters in IDs or titles

**Problem:** IDs or titles with `$`, spaces, or special characters cause issues.

**Solution:**
- Always quote strings with spaces or special characters:
  ```bash
  confl page create --title "My Page with Spaces" --body "Content"
  ```
- Use single quotes to prevent shell variable expansion:
  ```bash
  confl page get '$page-id-with-dollar'
  ```

## Next Steps

Now that you're familiar with the basics:

1. **Explore all commands** — Run `confl --help` and `confl <command> --help` to discover all available features
2. **Read the architecture docs** — Check out `docs/architecture/` for design principles and advanced topics
3. **Automate workflows** — Use `confl` in your CI/CD pipelines or shell scripts
4. **Build integrations** — Combine `confl` with other tools using `--json` output and pipelines

## Getting Help

- **Command help:** `confl --help` or `confl <command> --help`
- **GitHub Issues:** [https://github.com/pocmo/confl/issues](https://github.com/pocmo/confl/issues)
- **README:** [https://github.com/pocmo/confl](https://github.com/pocmo/confl)

Happy Confluence management from the command line! 🚀
