# Configuration

Config lives in `~/.config/confl/credentials.toml`. Environment variables (`CONFL_*`) take precedence over the config file.

## Configuration Priority

Settings are resolved in this order (highest priority first):

1. Command-line `--profile` flag
2. `CONFL_PROFILE` environment variable
3. Environment variables (`CONFL_SITE`, `CONFL_EMAIL`, `CONFL_TOKEN`)
4. Credentials file (`~/.config/confl/credentials.toml`)

## Multiple Profiles

You can manage multiple Confluence environments using profiles:

```bash
# Save credentials for different environments
echo "$PROD_TOKEN" | confl auth login --token \
  --site company.atlassian.net \
  --email you@example.com \
  --profile prod

echo "$DEV_TOKEN" | confl auth login --token \
  --site dev.atlassian.net \
  --email you@example.com \
  --profile dev

# List all profiles
confl auth list

# Use a specific profile (three ways)
confl --profile dev page list         # CLI flag
export CONFL_PROFILE=dev               # Environment variable
confl page list

# Check which profile is active
confl auth status --profile dev

# Delete a specific profile
confl auth logout --profile dev
```

## Config File Format

The credentials file uses TOML format:

```toml
default_profile = "default"

[profiles.default]
site = "company.atlassian.net"
email = "you@example.com"
token = "your-token"

[profiles.dev]
site = "dev.atlassian.net"
email = "dev@example.com"
token = "dev-token"
```

## Config File Location

- **macOS/Linux**: `~/.config/confl/credentials.toml`
- **Windows**: `%USERPROFILE%\.config\confl\credentials.toml`

The file is created automatically when you run `confl auth login`.

## Environment Variables

Instead of using the config file, you can set environment variables:

- `CONFL_SITE` — Your Confluence site (e.g., `yoursite.atlassian.net`)
- `CONFL_EMAIL` — Your email address
- `CONFL_TOKEN` — Your API token
- `CONFL_PROFILE` — Profile name to use (alternative to `--profile` flag)

Example:

```bash
export CONFL_SITE="yoursite.atlassian.net"
export CONFL_EMAIL="you@example.com"
export CONFL_TOKEN="your-api-token"

# Now use confl without profile flag
confl page list --space DEV
```

## Global Options

These options work with all commands:

### Verbose and Debug Modes

```bash
# Show detailed operation information
confl --verbose page get 12345678
confl -v page list

# Show debug information including HTTP requests/responses
confl --debug page create "Test Page"

# Combine with other commands
confl --debug auth status
```

**`--verbose` / `-v`**: Shows detailed operation information. Useful for understanding what the CLI is doing.

**`--debug`**: Shows debug-level logging including:
- HTTP request methods and URLs
- Request and response headers (auth tokens masked)
- Request and response bodies (truncated for large responses)
- Full stack traces for errors

These flags work with all commands and are particularly helpful when:
- Troubleshooting API issues
- Debugging authentication problems
- Understanding rate limiting or timeout errors
- Filing bug reports (include `--debug` output)

### Profile Selection

```bash
# Use a specific profile for a single command
confl --profile dev page list

# Set default profile via environment variable
export CONFL_PROFILE=dev
confl page list  # Uses dev profile
```

## Managing Profiles

### List Profiles

```bash
confl auth list
```

Shows all configured profiles and their sites.

### Check Active Profile

```bash
# Check default profile
confl auth status

# Check specific profile
confl auth status --profile dev
```

### Switch Default Profile

Edit `~/.config/confl/credentials.toml` and change the `default_profile` value:

```toml
default_profile = "prod"  # Change this
```

Or use `--profile` flag / `CONFL_PROFILE` environment variable to select profile on a per-command basis.

### Delete a Profile

```bash
# Delete specific profile
confl auth logout --profile dev

# Delete default profile
confl auth logout
```

## Security

The config file contains API tokens and should be kept secure:

- File permissions are set to `0600` (owner read/write only) when created
- Tokens are stored in plain text — protect this file like you would protect passwords
- Consider using environment variables in shared/CI environments
- Don't commit `credentials.toml` to version control

## See Also

- [Authentication](authentication.md) — Setting up API tokens and authentication
- [Getting Started Guide](getting-started.md) — Step-by-step setup walkthrough
