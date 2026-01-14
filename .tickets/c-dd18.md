---
id: c-dd18
status: closed
deps: [c-542b, c-41a7]
links: []
created: 2026-01-14T15:14:06Z
type: task
priority: 0
assignee: Sebastian Kaspari
---
# Integrate credentials file into config loading

Update config loading to fall back to credentials file when env vars are not set.

## Tasks
- Update `src/confl/config.py` to check credentials file as fallback
- Implement precedence:
  1. Environment variables (CONFL_SITE, CONFL_TOKEN, CONFL_EMAIL) — highest
  2. Credentials file (~/.config/confl/credentials.toml) — fallback
- Partial override: env vars should override individual fields from credentials file
  - Example: CONFL_SITE set + credentials file has token/email → use CONFL_SITE + token/email from file

## Acceptance Criteria
- `get_config()` returns config from env vars if set
- `get_config()` falls back to credentials file if env vars not set
- Partial overrides work correctly
- Clear error if no auth available from any source

## References
- docs/architecture/configuration.md — precedence rules

## Notes
- This makes `confl auth login --token` actually useful — stored creds get picked up by all commands


**2026-01-14T15:35:57Z**

Completed: Implemented partial override support for configuration. Individual env vars (CONFL_SITE, CONFL_EMAIL, CONFL_TOKEN) can now override specific fields from credentials file. Added 4 new tests covering partial override scenarios.
