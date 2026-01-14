---
id: c-da30
status: closed
deps: []
links: []
created: 2026-01-14T20:30:02Z
type: bug
priority: 0
assignee: Sebastian Kaspari
---
# Fix body-format parameter in get_page API call

The get_page method is sending an invalid body-format parameter value that causes a 400 error.

## Bug Description
Running `confl page get 6647808060` returns:
```
{'errors': [{'status': 400, 'code': 'INVALID_REQUEST_PARAMETER', 
'title': "Provided value {storage,atlas_doc_format} for 'body-format' is not the correct type. 
Expected type is PrimaryBodyRepresentationSingle",
'detail': 'PrimaryBodyRepresentationSingle is one of [STORAGE, ATLAS_DOC_FORMAT, VIEW, EXPORT_VIEW, 
ANONYMOUS_EXPORT_VIEW, STYLED_VIEW, EDITOR].'}]
```

## Root Cause
The API expects a single body-format value, not multiple comma-separated values. The parameter should be one of: STORAGE, ATLAS_DOC_FORMAT, VIEW, EXPORT_VIEW, ANONYMOUS_EXPORT_VIEW, STYLED_VIEW, EDITOR (uppercase, single value).

## Tasks
- Update get_page() method in ConfluenceClient to use correct body-format parameter
- Use single value: body-format=storage (or STORAGE)
- Remove invalid comma-separated format {storage,atlas_doc_format}
- Test that the fix resolves the 400 error
- Verify page content is returned correctly

## Acceptance Criteria
- `confl page get <page-id>` successfully fetches page without 400 error
- body-format parameter is a single valid value
- Tests pass with corrected parameter

## References
- docs/architecture/API.md — API parameter specifications
- https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get

## Notes
- Quick fix, should just change query parameter format


**2026-01-14T20:33:08Z**

Fixed body-format parameter in get_page API call - changed from invalid comma-separated 'storage,atlas_doc_format' to single value 'storage'. Updated all test mocks to match. All client get_page tests pass.
