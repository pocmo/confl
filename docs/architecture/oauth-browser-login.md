---
Status: PROPOSAL (Not Implemented)
Date: 2026-01-14
Purpose: Evaluate OAuth browser login feasibility for confl auth
Decision: Deferred - API token auth sufficient for MVP
---

# OAuth Browser Login Implementation

## Summary

OAuth browser login for `confl auth login` is **technically feasible** and would significantly improve UX compared to manual API token management. However, it requires hosting an official OAuth app or requiring users to create their own.

## Key Findings

### 1. Dynamic Client Registration: NOT Supported

**Answer**: Confluence Cloud does **NOT** support OAuth 2.0 Dynamic Client Registration (RFC 7591).

- All OAuth apps must be manually registered via Atlassian Developer Console
- Each app gets a static client_id and client_secret
- No way to programmatically register clients at runtime

**Implication**: We cannot use dynamic client registration. We must either:
1. Ship with pre-registered OAuth credentials (like acli, gcloud)
2. Require users to create their own OAuth app

### 2. PKCE Support: AVAILABLE ✅

**Answer**: Confluence Cloud **DOES** support Authorization Code flow with PKCE (Proof Key for Code Exchange).

- PKCE eliminates the need for client_secret in the token exchange
- Designed specifically for public clients like CLI tools
- Uses code_verifier and code_challenge to prevent interception attacks
- More secure than traditional authorization code flow with embedded secrets

**Implication**: We can use PKCE to avoid shipping a client_secret, only need client_id.

### 3. Device Flow: NOT Supported

**Answer**: Atlassian OAuth does **NOT** support Device Authorization Grant (OAuth Device Flow).

- Only Authorization Code flow is available
- Requires browser and localhost callback server
- No option for headless/SSH environments without browser access

**Implication**: OAuth won't work in headless environments. We must keep `--token` flag as fallback.

### 4. How Other CLI Tools Handle OAuth

#### GitHub CLI (`gh`)

**Flow**: OAuth Device Flow (preferred)
- Displays a user code and URL
- User visits URL on any device and enters code
- CLI polls for authorization
- **No browser required** - works in SSH, containers, headless environments
- Ships with embedded public client_id (no secret with device flow)
- Fallback: `gh auth login --with-token` or `GH_TOKEN` env var

**Client Credentials**: Embedded public client_id managed by GitHub

#### Google Cloud CLI (`gcloud`)

**Flow**: Authorization Code with PKCE
- Opens browser to Google OAuth consent page
- Localhost callback server catches authorization code
- Uses PKCE - no client_secret needed in token exchange
- Ships with embedded Google-managed client_id
- Fallback: Service account keys for automation

**Client Credentials**: Embedded client_id managed by Google

#### Atlassian CLI (`acli`)

**Flow**: Authorization Code with PKCE (likely)
- `acli jira auth login --web`
- Opens browser to Atlassian OAuth consent page
- Ships with embedded Atlassian-managed OAuth app (client_id + client_secret)
- Users do NOT need to create their own OAuth app
- Zero setup for most users

**Client Credentials**: Embedded client_id + client_secret managed by Atlassian

### 5. Client Credentials Distribution Strategy

All three major CLI tools ship with **pre-registered, vendor-managed OAuth credentials**:

| Tool | Flow | Credentials Shipped | Secret? |
|------|------|-------------------|---------|
| `gh` | Device Flow | client_id | No (device flow doesn't use secret) |
| `gcloud` | Authorization Code + PKCE | client_id | No (PKCE eliminates need for secret) |
| `acli` | Authorization Code + PKCE | client_id + client_secret | Yes (but PKCE may be used) |

**Key Pattern**: Vendor-hosted, officially-managed OAuth apps enable zero-setup user experience.

**Security Considerations**:
- Client_id is public and safe to embed
- With PKCE, client_secret is not needed (more secure for public clients)
- Without PKCE, embedded client_secret is a security concern (can be extracted from binary)
- PKCE is the recommended approach for public clients per RFC 8252 (OAuth for Native Apps)

## Recommended Implementation Approach

### Option 1: Host Official OAuth App (Recommended for Best UX)

**Setup**:
1. Register OAuth app in Atlassian Developer Console
2. Configure redirect_uri: `http://localhost:PORT/callback`
3. Request scopes: `read:confluence-content.all`, `write:confluence-content`, `offline_access`
4. Embed client_id in confl CLI (client_secret NOT needed with PKCE)

**Flow**:
```bash
$ confl auth login

Opening browser for authentication...
Waiting for authorization...
✓ Authentication successful!
Credentials saved to ~/.config/confl/credentials.toml
```

**Implementation**:
1. Generate code_verifier and code_challenge (PKCE)
2. Start local HTTP server on random available port (e.g., 8080-8090)
3. Open browser to Atlassian OAuth URL with client_id, code_challenge, redirect_uri, scopes
4. User logs in and authorizes
5. Catch callback at localhost with authorization code
6. Exchange code for access_token + refresh_token using code_verifier
7. Store tokens securely in credentials.toml
8. Shut down local server

**Pros**:
- Zero setup for users (like acli, gcloud)
- Professional, polished UX
- Secure with PKCE (no client_secret needed)
- Automatic token refresh

**Cons**:
- Requires infrastructure: Sebastian (or org) must host OAuth app
- Doesn't work in headless/SSH environments
- OAuth app owner has visibility into usage patterns
- Need fallback for automation (`--token` flag)

### Option 2: User-Provided OAuth App (Fallback)

**Setup**:
Users create their own OAuth app:
```bash
$ confl auth setup-oauth
Visit https://developer.atlassian.com/console to create an OAuth app.

1. Create new app
2. Add OAuth 2.0 (3LO) authorization
3. Set callback URL: http://localhost:8080/callback
4. Copy your Client ID

$ confl auth login --client-id abc123xyz

Opening browser...
...
```

**Pros**:
- No infrastructure needed from confl maintainers
- Users control their own OAuth app
- More transparent for security-conscious users

**Cons**:
- Extra setup friction
- Not zero-config like competitors
- Users may not understand OAuth app registration
- Each user/org needs separate OAuth app

### Option 3: Keep API Token Only (Current State)

**Current Flow**:
```bash
$ confl auth login --token --site mycompany.atlassian.net
Paste your API token: [user pastes token]
✓ Credentials saved
```

**Pros**:
- Simple, already works
- No infrastructure needed
- Works everywhere (including headless)
- User creates token in Atlassian UI (familiar process)
- Good for automation and scripting

**Cons**:
- Less elegant than OAuth browser flow
- User must manually create token in Atlassian
- Token management is manual

## Recommendation: Phased Approach

### Phase 1: Keep Current API Token (Immediate)

- Current `confl configure` or env vars work fine
- No changes needed
- Document clearly in README
- This is sufficient for MVP and early adoption

### Phase 2: Add OAuth Login (When Project Matures)

**When to implement**:
- After confl has proven adoption and stability
- When hosting an OAuth app is feasible (requires stable ownership)
- When community requests it

**What to implement**:
- Host official OAuth app (Option 1)
- Implement Authorization Code + PKCE flow
- Use authlib library (modern, well-maintained)
- Keep `--token` as fallback for automation/headless
- Document both auth methods clearly

**Why wait**:
- OAuth adds complexity: local server, browser launching, token refresh, error handling
- API tokens work fine for CLI use case (most CLI tools use keys/tokens)
- OAuth is nice-to-have, not essential for core functionality
- Hosting OAuth app requires stable project ownership

## Implementation Details (When Ready)

### Required Scopes

For Confluence API access:
- `read:confluence-content.all` - Read all Confluence content
- `write:confluence-content` - Create, update, delete pages/blogs/comments  
- `offline_access` - Get refresh token for long-term access (optional but recommended)

### OAuth Endpoints

```
Authorization: https://auth.atlassian.com/authorize
Token: https://auth.atlassian.com/oauth/token
```

### Python Libraries

**Recommended: authlib**
- Modern, actively maintained
- Native PKCE support
- Clean API for OAuth 2.0 flows
- Good documentation

```python
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc7636 import create_s256_code_challenge
import secrets

# Generate PKCE challenge
code_verifier = secrets.token_urlsafe(64)
code_challenge = create_s256_code_challenge(code_verifier)

# Create session
client = OAuth2Session(
    client_id='your_client_id',
    redirect_uri='http://localhost:8080/callback',
    scope='read:confluence-content.all write:confluence-content offline_access',
    code_challenge=code_challenge,
    code_challenge_method='S256'
)

# Get authorization URL
uri, state = client.create_authorization_url(
    'https://auth.atlassian.com/authorize'
)

# Open browser, start local server, catch callback...

# Exchange code for token
token = client.fetch_token(
    'https://auth.atlassian.com/oauth/token',
    code=authorization_code,
    code_verifier=code_verifier
)
```

**Alternative: requests-oauthlib**
- Older but stable
- Also supports PKCE
- Integrated with requests

### Local Callback Server

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import webbrowser

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if 'code' in query:
            self.server.authorization_code = query['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>Authentication successful!</h1><p>You can close this window.</p>')
        
server = HTTPServer(('localhost', 8080), CallbackHandler)
webbrowser.open(authorization_url)
server.handle_request()  # Wait for callback
code = server.authorization_code
```

### Token Storage

Store in `~/.config/confl/credentials.toml`:
```toml
[auth]
method = "oauth"
site = "mycompany.atlassian.net"
access_token = "eyJ..."
refresh_token = "eyJ..."
expires_at = 1642176000

# Fallback for --token method
[auth.token]
site = "mycompany.atlassian.net"
email = "user@example.com"
token = "ATATT..."
```

### Token Refresh Logic

```python
import time
from authlib.integrations.requests_client import OAuth2Session

def ensure_valid_token(creds):
    if creds['expires_at'] > time.time() + 300:  # 5 min buffer
        return creds['access_token']
    
    # Refresh token
    client = OAuth2Session(
        client_id=CLIENT_ID,
        token=creds
    )
    new_token = client.refresh_token(
        'https://auth.atlassian.com/oauth/token',
        refresh_token=creds['refresh_token']
    )
    save_credentials(new_token)
    return new_token['access_token']
```

## Comparison with Previous Research (c-2b89)

Previous ticket c-2b89 concluded OAuth was not recommended. This revisit changes recommendation based on:

**What changed**:
- Confirmation that **PKCE is supported** (reduces security concerns)
- Understanding that **acli successfully uses OAuth** with embedded credentials
- Recognition that hosting an OAuth app is optional (can require user registration)

**What didn't change**:
- No device flow support (still true)
- OAuth adds complexity (still true)
- API tokens work fine (still true)

**New conclusion**: OAuth is feasible with PKCE, but still optional/nice-to-have. Recommend phased approach:
1. Keep API tokens for now (good enough)
2. Add OAuth later when project matures and hosting app is viable

## Security Considerations

1. **Embedded Client ID**: Safe to ship in open-source project
2. **No Client Secret Needed**: PKCE eliminates this security risk
3. **Token Storage**: Use restrictive file permissions (0600) on credentials.toml
4. **Token Refresh**: Implement automatic refresh before expiry
5. **Localhost Server**: Only listen on localhost, use ephemeral port, shutdown after callback
6. **State Parameter**: Use for CSRF protection in OAuth flow
7. **Scope Minimization**: Only request needed scopes

## Alternative: API Tokens Remain Valid

For context, API tokens are perfectly acceptable for CLI tools:
- **AWS CLI**: Uses access keys (not OAuth)
- **Terraform**: Uses API tokens/keys
- **Docker CLI**: Uses API tokens
- **kubectl**: Uses service account tokens or client certificates
- **heroku CLI**: Uses API keys

OAuth is more common for tools that have official vendor hosting (GitHub CLI, gcloud, Azure CLI).

## Next Steps (If Implementing OAuth)

### Discovery Phase Complete ✅

Create implementation tickets:

1. **Research & Spike** (P2)
   - Test OAuth flow manually with Atlassian
   - Verify PKCE implementation
   - Test callback server approach
   - Confirm scope requirements

2. **Infrastructure** (P1 - blocking)
   - Decide: Host official OAuth app OR require user registration
   - If hosting: Register OAuth app in Atlassian Developer Console
   - Configure redirect URIs, scopes
   - Document OAuth app setup

3. **Implementation** (P1)
   - Add authlib dependency
   - Implement `confl auth login` with OAuth flow
   - Implement token storage in credentials.toml
   - Implement token refresh logic
   - Handle errors (declined auth, network issues, etc.)

4. **Fallback & Docs** (P1)
   - Keep `confl auth login --token` for automation
   - Update docs/architecture/configuration.md
   - Add troubleshooting guide for OAuth issues
   - Document headless environment workarounds

5. **Testing** (P1)
   - Unit tests for PKCE code generation
   - Integration tests for OAuth flow (mocked)
   - Manual testing with real Atlassian instance
   - Test token refresh logic

## Conclusion

OAuth browser login is **technically feasible** with PKCE but not essential for confl's core mission. 

**Recommended**: Keep API token authentication for now (Phase 1). Consider OAuth later when:
- Project has stable ownership for hosting OAuth app
- Community requests better auth UX
- We have bandwidth for the additional complexity

API tokens are simple, secure, and work everywhere - perfectly sufficient for a CLI tool.
