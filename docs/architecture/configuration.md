---
Status: IMPLEMENTED
Date: 2025-12-01
Purpose: Document configuration and authentication methods
---

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

Credentials stored in `~/.config/confl/credentials.toml` with file permissions set to `0o600` (owner read/write only).

### Security

**Current Approach:**
- Credentials stored in `~/.config/confl/credentials.toml`
- File permissions: `0o600` (owner read/write only)
- Secure for single-user development environments
- Standard practice for CLI developer tools

**Future Enhancement: OS Keychain Integration**

For additional security, confl could integrate with operating system keychains:

- **macOS**: Keychain Access (`security` command)
- **Windows**: Credential Manager (Windows Credential Store)
- **Linux**: Secret Service API (GNOME Keyring, KWallet)

Benefits:
- Encrypted credential storage managed by OS
- Integration with system security policies
- Credentials never written as plain text to disk

Implementation Considerations:
- Python library: [`keyring`](https://pypi.org/project/keyring/) provides cross-platform abstraction
- Effort: High (requires OS-specific testing and fallback handling)
- Trade-off: Added dependency and complexity vs. marginal security benefit
- Current file-based approach is acceptable and secure for developer tool use case

**Priority:** P3 - Future enhancement, not a security concern

**Reference:** [Senior Review Findings](senior-review-findings.md) - Finding 6.1

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
