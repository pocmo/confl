# Configuration

## Config Location

- Config path: `~/.config/confl/`
- Environment variables (`CONFL_*`) override config file settings

## Authentication

### For humans (local development)

```bash
confl auth login              # Opens browser for OAuth
confl auth login --token      # Read API token from stdin
confl auth status             # Show current auth state
confl auth logout             # Clear stored credentials
```

Credentials stored in `~/.config/confl/credentials.toml`.

### For automation (CI, agents)

Environment variables are auto-detected — no login required:

```bash
export CONFL_SITE="mycompany.atlassian.net"
export CONFL_TOKEN="your-api-token"

confl page list --space DEV   # Just works
```

Alternatively, pipe token explicitly:

```bash
echo "$CONFLUENCE_TOKEN" | confl auth login --token --site mycompany.atlassian.net
```

## Precedence

1. Command-line flags (highest)
2. Environment variables (`CONFL_*`)
3. Config file (`~/.config/confl/`)

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CONFL_SITE` | Confluence site (e.g., `mycompany.atlassian.net`) |
| `CONFL_TOKEN` | API token for authentication |
| `CONFL_EMAIL` | Email associated with API token |
