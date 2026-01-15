---
id: c-4fb1
status: open
deps: []
links: []
created: 2026-01-15T08:15:00Z
type: task
priority: 3
assignee: Sebastian Kaspari
---
# Document keychain integration as future enhancement

Document OS-specific keychain integration for secure credential storage as a future enhancement.

Current:
- Credentials stored in ~/.config/confl/credentials.toml
- File permissions set to 0o600 (secure for single-user system)
- Works well for developer tool

Future Enhancement:
- Integrate with OS keychains for additional security
- macOS: Keychain Access
- Windows: Credential Manager
- Linux: Secret Service (GNOME Keyring, KWallet)

Task:
- Document this as a future enhancement in architecture docs
- Note current approach is acceptable and secure
- Add references to keychain libraries: keyring (Python)
- Estimate effort: High (OS-specific implementations)

Priority: P3 - Not a security issue, current approach is secure

Reference: docs/architecture/senior-review-findings.md Finding 6.1

