---
id: c-da4c
status: open
deps: []
links: []
created: 2026-01-15T07:44:32Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# DISCOVERY: OAuth browser login flow implementation requirements

Research what's needed to implement 'confl auth login' with OAuth browser flow, similar to gh/gcloud/acli.

## Problem Statement
We want `confl auth login` to open a browser, complete OAuth authorization, and store credentials automatically. This provides better UX than manual token management. Key question: Does Confluence support dynamic client registration, or do we need pre-registered OAuth app credentials?

## Questions to Answer

### 1. OAuth App Registration Requirements
- Does Confluence Cloud support OAuth 2.0 dynamic client registration (RFC 7591)?
- Or must we pre-register an OAuth app and ship client credentials?
- If pre-registration required:
  - Where do we register OAuth apps? (Atlassian Developer Console?)
  - What redirect URIs are needed?
  - Can we use localhost redirect for CLI apps?
  - Are client credentials sensitive (client secret)?

### 2. Client Credentials Distribution
- If pre-registration required, how do gh/gcloud/acli handle this?
- Do they ship embedded client credentials in the tool?
- Do they use different approaches (device flow, PKCE, etc.)?
- What are security implications of shipping client credentials in open source?
- Can users provide their own OAuth app credentials?

### 3. OAuth Flow Type
- Which OAuth flow should we use?
  - Authorization Code with PKCE? (recommended for public clients)
  - Device Authorization Grant? (no localhost redirect needed)
  - Implicit flow? (deprecated, avoid)
- What scopes are needed for Confluence API access?
- How do we handle token refresh?

### 4. Implementation Architecture
- How to implement local callback server for authorization code?
- How to launch browser cross-platform?
- Where to store tokens securely?
- How to handle token expiration and refresh?
- What libraries exist? (authlib, requests-oauthlib, etc.)

### 5. User Experience Considerations
- Fallback if browser can't open?
- Support for headless/SSH environments?
- What if user already has token from Atlassian (keep --token flag)?
- Error handling for declined authorization?

### 6. Comparison with Other Tools
- Study how `gh` (GitHub CLI) implements OAuth
- Study how `gcloud` implements OAuth
- Study how `acli` (Atlassian CLI) implements OAuth
- What can we learn/reuse from their approaches?

## Output
- Document findings in **docs/architecture/oauth-browser-login.md** with:
  - Clear explanation of Confluence OAuth requirements
  - Whether dynamic client registration is supported
  - Recommended OAuth flow type and why
  - Client credential handling strategy (if pre-registration required)
  - Architecture diagram/flow of the implementation
  - Security considerations
  - Alternative approaches (device flow, manual token)
  - Step-by-step implementation breakdown
- Create follow-up tickets based on findings:
  - If straightforward: implementation tickets with clear tasks
  - If complex: additional discovery or proof-of-concept tickets
  - Consider phased approach (MVP vs full-featured)

## IMPORTANT
This is a DISCOVERY ticket. Research, document, file follow-ups, then STOP. Do not implement.

## References
- docs/architecture/configuration.md — current auth design
- c-2b89 — existing OAuth research ticket (may have overlap)
- https://developer.atlassian.com/cloud/confluence/oauth-2-3lo-apps/ — Confluence OAuth docs
- https://datatracker.ietf.org/doc/html/rfc7591 — Dynamic Client Registration
- https://datatracker.ietf.org/doc/html/rfc8252 — OAuth for Native Apps
- https://oauth.net/2/grant-types/device-code/ — Device Authorization Grant

## Notes
- Main concern: Can we ship an open-source tool with OAuth without requiring users to create their own OAuth app?
- If dynamic client registration not supported, need strategy for client credentials
- Compare with existing ticket c-2b89 to avoid duplicate work
- Consider that API token flow (current --token) works fine for many users
- OAuth might be P2 if token flow is sufficient


**2026-01-15T07:44:49Z**

NOTE: This ticket revisits OAuth implementation. Previous discovery ticket c-2b89 concluded OAuth was not recommended due to lack of device flow and complexity. This ticket should specifically focus on the dynamic client registration question and compare with how gh/gcloud/acli actually implement it. If findings differ from c-2b89, document why the recommendation should change.
