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

**New to confl?** Check out the [Getting Started Guide](docs/getting-started.md) for a comprehensive walkthrough.

## Installation

Install with [pipx](https://pipx.pypa.io/) (recommended):

```bash
pipx install git+https://github.com/pocmo/confl.git
```

See [Installation Guide](docs/installation.md) for detailed instructions, troubleshooting, and alternative installation methods.

## Authentication

`confl` uses Confluence API tokens for authentication:

```bash
# Store credentials in config file
echo "$YOUR_API_TOKEN" | confl auth login --token \
  --site yoursite.atlassian.net \
  --email you@example.com

# Check authentication status
confl auth status
```

To create an API token, visit: https://id.atlassian.com/manage-profile/security/api-tokens

See [Authentication Guide](docs/authentication.md) for detailed setup, security best practices, and troubleshooting.

## Configuration

Config lives in `~/.config/confl/credentials.toml`. Environment variables take precedence.

**Multiple profiles:**

```bash
# Save different environments
echo "$PROD_TOKEN" | confl auth login --token --site company.atlassian.net --email you@example.com --profile prod
echo "$DEV_TOKEN" | confl auth login --token --site dev.atlassian.net --email dev@example.com --profile dev

# Use a specific profile
confl --profile dev page list
```

See [Configuration Guide](docs/configuration.md) for details on profiles, environment variables, and global options.

## Commands

`confl` provides commands for managing pages, spaces, attachments, labels, comments, and blog posts.

**Core commands:**

- `confl search` — Search content using CQL or filters
- `confl page` — Manage pages (list, get, create, update, delete, versions)
- `confl space` — Manage spaces (list, get)
- `confl attachment` — Manage attachments (list, upload, download, delete)
- `confl label` — Manage labels (list, add, remove)
- `confl comment` — Manage comments (list, get, add, update, delete)
- `confl blogpost` — Manage blog posts (list, get, create, update, delete)
- `confl auth` — Manage authentication (login, logout, status, list profiles)

**Quick examples:**

```bash
# Search for content
confl search --text "API docs" --space DEV

# Get a page as markdown
confl page get 123456 --markdown

# Create a page from markdown
confl page create --space DEV --title "New Page" --body-file doc.md

# Add a comment
confl comment add --page 123456 --body "Great work!"

# Upload an attachment
confl attachment upload --page 123456 --file report.pdf
```

See [Commands Reference](docs/commands.md) for complete command documentation with all options and examples.

## Documentation

- [Getting Started Guide](docs/getting-started.md) — Step-by-step walkthrough for new users
- [Installation Guide](docs/installation.md) — Installation, upgrading, and troubleshooting
- [Authentication Guide](docs/authentication.md) — API token setup and security best practices
- [Configuration Guide](docs/configuration.md) — Profiles, environment variables, and global options
- [Commands Reference](docs/commands.md) — Complete command documentation
- [Architecture Documentation](docs/architecture/README.md) — Design principles, technical decisions, and implementation details

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
