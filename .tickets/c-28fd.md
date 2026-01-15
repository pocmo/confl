---
id: c-28fd
status: closed
deps: []
links: []
created: 2026-01-15T11:55:36Z
type: bug
priority: 0
assignee: Sebastian Kaspari
---
# BUG: confl space whoami fails with 400 error on generic-content-type

The 'confl space whoami' command fails with a 400 error about invalid generic-content-type.

## Bug Description
Running `confl space whoami` returns:
```
Error: Client error (400): Provided value {user} for 'generic-content-type' is not the correct type.
Expected type is GenericContentType
GenericContentType is one of [DATABASES, EMBEDS, FOLDERS, WHITEBOARDS].
```

This prevents users from discovering their personal space.

## Root Cause
The implementation is likely using wrong endpoint or wrong parameters. The error suggests it's trying to query generic content with 'user' as a type, but the API expects content types like DATABASES, EMBEDS, FOLDERS, or WHITEBOARDS.

Possible issues:
- Using wrong API endpoint entirely
- Incorrect query parameter for getting user's personal space
- Misunderstanding of how to look up personal spaces in API v2

## Tasks
- Review current implementation of `space whoami` command
- Check what API endpoint is being called
- Investigate correct way to get current user's personal space:
  - Is there a /user/current endpoint?
  - Do we need to use /spaces with user filter?
  - Is personal space key based on user ID (e.g., ~userid)?
- Fix the implementation to use correct endpoint/parameters
- Test that it returns user's personal space info
- Add tests for this command

## Acceptance Criteria
- `confl space whoami` successfully returns user's personal space
- Shows space key, name, and other relevant info
- No 400 errors
- Works for all authenticated users

## References
- src/confl/commands/space.py — whoami command implementation
- Confluence API docs for user/personal space lookup
- docs/architecture/API.md — API reference

## Notes
- Personal spaces typically have keys like ~userid or ~accountid
- This is a basic feature users need to discover their own space
- Related to personal space investigation in c-5171


**2026-01-15T12:02:36Z**

Fixed: get_current_user() now uses v1 API endpoint (/wiki/rest/api/user/current) instead of v2 (which doesn't support user endpoints). Updated all 4 whoami tests to mock the correct v1 endpoint.
