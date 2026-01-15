# Authentication

`confl` uses Confluence API tokens for authentication. You can either:

1. Store credentials in config file using `confl auth login`
2. Set environment variables (`CONFL_SITE`, `CONFL_EMAIL`, `CONFL_TOKEN`)

## Creating an API Token

To create an API token, visit: https://id.atlassian.com/manage-profile/security/api-tokens

Follow these steps:
1. Log in to your Atlassian account
2. Navigate to **Security** → **API tokens**
3. Click **Create API token**
4. Give your token a descriptive name (e.g., "confl CLI")
5. Copy the generated token (you won't be able to see it again)

## Quick Setup

Store credentials in config file:

```bash
# Store credentials in config file
echo "$YOUR_API_TOKEN" | confl auth login --token \
  --site yoursite.atlassian.net \
  --email you@example.com

# Check authentication status
confl auth status

# Logout (delete stored credentials)
confl auth logout
```

## Environment Variables

Instead of storing credentials in the config file, you can use environment variables:

```bash
export CONFL_SITE="yoursite.atlassian.net"
export CONFL_EMAIL="you@example.com"
export CONFL_TOKEN="your-api-token"

# Now use confl without login
confl page list --space DEV
```

Environment variables take precedence over config file credentials.

## Security Best Practices

- **Never commit tokens to version control**: Use environment variables or gitignored config files
- **Use separate tokens per machine/environment**: Create different tokens for different machines or CI/CD pipelines
- **Rotate tokens regularly**: API tokens don't expire but should be rotated periodically
- **Use restrictive permissions**: Create tokens with minimal necessary permissions (though Confluence API tokens have full account access)
- **Revoke unused tokens**: Remove tokens you're no longer using from your Atlassian account

## OAuth Login

OAuth browser-based login is not currently supported. API token authentication is the recommended approach for CLI tools.

For background on this decision, see [OAuth Browser Login Architecture Decision](architecture/oauth-browser-login.md).

## Troubleshooting

### "Authentication failed" errors

1. Check your credentials are correct:
   ```bash
   confl auth status
   ```

2. Verify your API token is valid by visiting: https://id.atlassian.com/manage-profile/security/api-tokens

3. Make sure you're using the correct site URL (e.g., `yoursite.atlassian.net`, not the full URL)

4. Use `--debug` to see detailed error information:
   ```bash
   confl --debug auth status
   ```

### Token has been revoked

If you see errors about invalid credentials, your token may have been revoked. Create a new token and run `confl auth login` again.

### Wrong site or email

If you need to update your site or email:

```bash
# Logout and login again
confl auth logout
echo "$NEW_TOKEN" | confl auth login --token --site newsite.atlassian.net --email new@example.com
```

## See Also

- [Configuration](configuration.md) — Profile management and config file details
- [Getting Started Guide](getting-started.md) — Step-by-step setup walkthrough
