---
Status: REFERENCE
Date: 2025-12-01
Purpose: Comprehensive Confluence Cloud REST API v2 reference documentation
---

# Confluence Cloud REST API v2 Reference

This document provides comprehensive API reference documentation for Confluence Cloud REST API v2.

## Base URL

All API requests are made to: `https://<your-domain>.atlassian.net/wiki/api/v2/`

## Authentication

The API supports multiple authentication methods:
- **OAuth 2.0** (recommended for production apps)
- **Basic auth** (username/password or email/API token)
- **Personal Access Tokens**

## Common Patterns

### Pagination

Most list endpoints support cursor-based pagination:
- `limit` - Number of results per page (default varies by endpoint)
- `cursor` - Token for next page (returned in response)
- Response includes `Link: next` header when more results available

### Expansion

Many endpoints support `expand` parameter to include related resources:
- Example: `?expand=body.storage,version,space`

### Filtering

Common filter parameters:
- `status` - Filter by content status (current, archived, trashed, deleted)
- `sort` - Sort order (created-date, modified-date, title, etc.)

### Space Identification

Confluence spaces can be identified by two different values:

- **Space Key**: A human-readable unique identifier (e.g., `DEV`, `TEAM`)
  - For personal spaces: tilde (`~`) followed by account ID (e.g., `~61df405068926d0068c87f43`)
  - Visible in URLs: `/wiki/spaces/~61df405068926d0068c87f43/overview`
  - Can be changed by admins (except personal space keys)
  
- **Space ID**: An immutable numeric identifier (e.g., `3277554038`)
  - Never changes, even if space key is renamed
  - Required by many API v2 endpoints

**API v2 Endpoint Behavior:**
- `GET /spaces?keys={key}` - Accepts space keys (including personal space keys with `~`)
- `GET /spaces/{id}` - Only accepts numeric space IDs
- `PUT /spaces/{id}` - Only accepts numeric space IDs  
- `DELETE /spaces/{id}` - Only accepts numeric space IDs

**To convert space key to ID:**
```
GET /spaces?keys=SPACEKEY
```
The response includes both `id` (numeric) and `key` fields.

**Important:** Unlike API v1, API v2 endpoints with `{id}` in the path only accept numeric IDs. Attempting to use a space key will result in a 400 error: "Provided value {...} for 'id' is not the correct type. Expected type is long."

## Error Responses

The API uses standard HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `204 No Content` - Successful deletion or update with no response body
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or invalid
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., version mismatch)
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

Error response format:
```json
{
  "message": "Error description",
  "statusCode": 400,
  "reason": "VALIDATION_ERROR"
}
```

## Rate Limits

Confluence Cloud enforces rate limits based on your plan:
- Monitor via `X-RateLimit-*` headers in responses
- `X-RateLimit-Limit` - Total requests allowed in window
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - When limit resets (Unix timestamp)

---

## API Endpoints

The following sections document all available endpoints grouped by resource type.


### Page
#### `GET /labels/{id}/pages`
Get pages for label
Returns the pages of specified label. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the label for which pages should be returned. |
| `space-id` | query | array |  | Filter the results based on space ids. Multiple space ids can be specified as a comma-separated list. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested pages for specified label were successfully fetched.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested label or label was not found.

#### `GET /pages`
Get pages
Returns all pages. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only pages that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | query | array |  | Filter the results based on page ids. Multiple page ids can be specified as a comma-separated list. |
| `space-id` | query | array |  | Filter the results based on space ids. Multiple space ids can be specified as a comma-separated list. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `status` | query | array |  | Filter the results to pages based on their status. By default, `current` and `archived` are used. |
| `title` | query | string |  | Filter the results to pages based on their title. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `subtype` | query | enum: live, page |  | Filter the results to pages based on their subtype. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested pages are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `POST /pages`
Create page
Creates a page in the space.

Pages are created as published by default unless specified as a draft in the status field. If creating a published page, the title must be specified.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the corresponding space. Permission to create a page in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `embedded` | query | boolean |  | Tag the content as embedded and content will be created in NCS. |
| `private` | query | boolean |  | The page will be private. Only the user who creates this page will have permission to view and edit one. |
| `root-level` | query | boolean |  | The page will be created at the root level of the space (outside the space homepage tree). If true, then a  value may not be supplied for the `parentId` body parameter. |
**Responses:**

- **200**: Returned if the page was successfully created.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if:
- The space does not exist
- The user does not have permissions to view the space
- The user does not have the needed permissions to create a page in the provided space
- **413**: Returned if the request is too large in size (over 5 MB).

#### `GET /pages/{id}`
Get page by id
Returns a specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page to be returned. If you don't know the page ID, use Get pages and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `get-draft` | query | boolean |  | Retrieve the draft version of this page. |
| `status` | query | array |  | Filter the page being retrieved by its status. |
| `version` | query | integer |  | Allows you to retrieve a previously published version. Specify the previous version's number to retrieve its details. |
| `include-labels` | query | boolean |  | Includes labels associated with this page in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this page in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-operations` | query | boolean |  | Includes operations associated with this page in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-likes` | query | boolean |  | Includes likes associated with this page in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-versions` | query | boolean |  | Includes versions associated with this page in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-version` | query | boolean |  | Includes the current version associated with this page in the response. By default this is included and can be omitted by setting the value to `false`. |
| `include-favorited-by-current-user-status` | query | boolean |  | Includes whether this page has been favorited by the current user. |
| `include-webresources` | query | boolean |  | Includes web resources that can be used to render page content on a client. |
| `include-collaborators` | query | boolean |  | Includes collaborators on the page. |
| `include-direct-children` | query | boolean |  | Includes direct children of the page, as defined in the `ChildrenResponse` object. |
**Responses:**

- **200**: Returned if the requested page is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `PUT /pages/{id}`
Update page
Update a page by id.

When the "current" version is updated, the provided body content is considered as the latest version. This latest body content
will be attempted to be merged into the draft version through a content reconciliation algorithm. If two versions are significantly diverged, 
the latest provided content may entirely override what was previously in the draft. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page and its corresponding space. Permission to update pages in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page to be updated. If you don't know the page ID, use Get Pages and filter the results. |
**Responses:**

- **200**: Returned if the requested page is successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided page does not exist
- The user does not have permissions to view the page
- The user does not have the needed permissions to update a page in the space
- The user provides a parentId for a page that does not exist or they do not have permission to view
- There are no spaces associated with the given spaceId

#### `DELETE /pages/{id}`
Delete page
Delete a page by id.

By default this will delete pages that are non-drafts. To delete a page that is a draft, the endpoint must be called on a 
draft with the following param `draft=true`. Discarded drafts are not sent to the trash and are permanently deleted.

Deleting a page moves the page to the trash, where it can be restored later. To permanently delete a page (or "purge" it),
the endpoint must be called on a **trashed** page with the following param `purge=true`.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page and its corresponding space.
Permission to delete pages in the space.
Permission to administer the space (if attempting to purge).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page to be deleted. |
| `purge` | query | boolean |  | If attempting to purge the page. |
| `draft` | query | boolean |  | If attempting to delete a page that is a draft. |
**Responses:**

- **204**: Returned if the page was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided page does not exist
- The user does not have permissions to view the page
- The user does not have the needed permissions to delete a page in the space

#### `PUT /pages/{id}/title`
Update page title
Updates the title of a specified page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page and its corresponding space. Permission to update pages in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page to be updated. If you don't know the page ID, use Get Pages and filter the results |
**Responses:**

- **200**: Returned if the requested page is successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided page does not exist
- The user does not have permissions to view the page
- The user does not have the needed permissions to update a page in the space
- The user provides a parentId for a page that does not exist or they do not have permission to view
- There are no spaces associated with the given spaceId

#### `GET /spaces/{id}/pages`
Get pages in space
Returns all pages in a space. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and 'View' permission for the space.
Only pages that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which pages should be returned. |
| `depth` | query | enum: all, root |  | Filter the results to pages at the root level of the space or to all pages in the space. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `status` | query | array |  | Filter the results to pages based on their status. By default, `current` and `archived` are used. |
| `title` | query | string |  | Filter the results to pages based on their title. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested pages are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.


### Space
#### `GET /spaces`
Get spaces
Returns all spaces. The results will be sorted by id ascending. The number of results is limited by the `limit` parameter and
additional results (if available) will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only spaces that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `ids` | query | array |  | Filter the results to spaces based on their IDs. Multiple IDs can be specified as a comma-separated list. |
| `keys` | query | array |  | Filter the results to spaces based on their keys. Multiple keys can be specified as a comma-separated list. |
| `type` | query | enum: global, collaboration, knowledge_base... |  | Filter the results to spaces based on their type. |
| `status` | query | enum: current, archived |  | Filter the results to spaces based on their status. |
| `labels` | query | array |  | Filter the results to spaces based on their labels. Multiple labels can be specified as a comma-separated list. |
| `favorited-by` | query | string |  | Filter the results to spaces favorited by the user with the specified account ID. |
| `not-favorited-by` | query | string |  | Filter the results to spaces NOT favorited by the user with the specified account ID. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `description-format` | query | object |  | The content format type to be returned in the `description` field of the response. If available, the representation will be available under a response field of the same name under the `description` field. |
| `include-icon` | query | boolean |  | If the icon for the space should be fetched or not. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of spaces per result to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested spaces are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `POST /spaces`
Create space
Creates a Space as specified in the payload.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to create spaces.
**Responses:**

- **201**: Returned if the requested space is created.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to create spaces.
- **413**: Returned if the request is too large in size (over 5 MB).

#### `GET /spaces/{id}`
Get space by id
Returns a specific space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space to be returned. |
| `description-format` | query | object |  | The content format type to be returned in the `description` field of the response. If available, the representation will be available under a response field of the same name under the `description` field. |
| `include-icon` | query | boolean |  | If the icon for the space should be fetched or not. |
| `include-operations` | query | boolean |  | Includes operations associated with this space in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes space properties associated with this space in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-permissions` | query | boolean |  | Includes space permissions associated with this space in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-role-assignments` | query | boolean |  | Includes role assignments associated with this space in the response. This parameter is only accepted for EAP sites. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-labels` | query | boolean |  | Includes labels associated with this space in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
**Responses:**

- **200**: Returned if the requested space is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested space or the space was not found.


### Blog Post
#### `GET /blogposts`
Get blog posts
Returns all blog posts. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only blog posts that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | query | array |  | Filter the results based on blog post ids. Multiple blog post ids can be specified as a comma-separated list. |
| `space-id` | query | array |  | Filter the results based on space ids. Multiple space ids can be specified as a comma-separated list. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `status` | query | array |  | Filter the results to blog posts based on their status. By default, `current` is used. |
| `title` | query | string |  | Filter the results to blog posts based on their title. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of blog posts per result to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested blog posts are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `POST /blogposts`
Create blog post
Creates a new blog post in the space specified by the spaceId.

By default this will create the blog post as a non-draft, unless the status is specified as draft.
If creating a non-draft, the title must not be empty.

Currently only supports the storage representation specified in the body.representation enums below

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `private` | query | boolean |  | The blog post will be private. Only the user who creates this blog post will have permission to view and edit one. |
**Responses:**

- **200**: Returned if the blog post was created successfully.
- **400**: Returned if invalid values were passed in for any of the enums, a REQUIRED parameter was missing, or if the given title is a duplicate in the space
- **401**: Returned if the authentication credentials are incorrect or missing from the request
- **404**: Returned if:
- The provided space does not exist
- The user does not have permissions to view the space
- The user does not have the needed permissions to create a blog post in the provided space
- **413**: Returned if the request is too large in size (over 5 MB)

#### `GET /blogposts/{id}`
Get blog post by id
Returns a specific blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post to be returned. If you don't know the blog post ID, use Get blog posts and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `get-draft` | query | boolean |  | Retrieve the draft version of this blog post. |
| `status` | query | array |  | Filter the blog post being retrieved by its status. |
| `version` | query | integer |  | Allows you to retrieve a previously published version. Specify the previous version's number to retrieve its details. |
| `include-labels` | query | boolean |  | Includes labels associated with this blog post in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this blog post in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-operations` | query | boolean |  | Includes operations associated with this blog post in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-likes` | query | boolean |  | Includes likes associated with this blog post in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-versions` | query | boolean |  | Includes versions associated with this blog post in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-version` | query | boolean |  | Includes the current version associated with this blog post in the response. By default this is included and can be omitted by setting the value to `false`. |
| `include-favorited-by-current-user-status` | query | boolean |  | Includes whether this blog post has been favorited by the current user. |
| `include-webresources` | query | boolean |  | Includes web resources that can be used to render blog post content on a client. |
| `include-collaborators` | query | boolean |  | Includes collaborators on the blog post. |
**Responses:**

- **200**: Returned if the requested blog post is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `PUT /blogposts/{id}`
Update blog post
Update a blog post by id.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post and its corresponding space. Permission to update blog posts in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post to be updated. If you don't know the blog post ID, use Get Blog Posts and filter the results. |
**Responses:**

- **200**: Returned if the requested blog post is successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided blog post does not exist
- The user does not have permissions to view the blog post
- The user does not have the needed permissions to update a blog post in the space

#### `DELETE /blogposts/{id}`
Delete blog post
Delete a blog post by id.

By default this will delete blog posts that are non-drafts. To delete a blog post that is a draft, the endpoint must be called on a 
draft with the following param `draft=true`. Discarded drafts are not sent to the trash and are permanently deleted.

Deleting a blog post that is not a draft moves the blog post to the trash, where it can be restored later.
To permanently delete a blog post (or "purge" it), the endpoint must be called on a **trashed** blog post with the following param `purge=true`.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post and its corresponding space.
Permission to delete blog posts in the space.
Permission to administer the space (if attempting to purge).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post to be deleted. |
| `purge` | query | boolean |  | If attempting to purge the blog post. |
| `draft` | query | boolean |  | If attempting to delete a blog post that is a draft. |
**Responses:**

- **204**: Returned if the blog post was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided blog post does not exist
- The user does not have permissions to view the blog post
- The user does not have the needed permissions to delete a blog post in the space

#### `GET /labels/{id}/blogposts`
Get blog posts for label
Returns the blogposts of specified label. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the label for which blog posts should be returned. |
| `space-id` | query | array |  | Filter the results based on space ids. Multiple space ids can be specified as a comma-separated list. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of blog posts per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested blog posts for specified label were successfully fetched.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested label or label was not found.

#### `GET /spaces/{id}/blogposts`
Get blog posts in space
Returns all blog posts in a space. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and view the space.
Only blog posts that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which blog posts should be returned. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `status` | query | array |  | Filter the results to blog posts based on their status. By default, `current` is used. |
| `title` | query | string |  | Filter the results to blog posts based on their title. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of blog posts per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested blog posts are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.


### Label
#### `GET /attachments/{id}/labels`
Get labels for attachment
Returns the labels of specific attachment. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the attachment and its corresponding space.
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the attachment for which labels should be returned. |
| `prefix` | query | enum: my, team, global... |  | Filter the results to labels based on their prefix. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested attachment or the attachment was not found.

#### `GET /blogposts/{id}/labels`
Get labels for blog post
Returns the labels of specific blog post. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the blog post and its corresponding space.
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which labels should be returned. |
| `prefix` | query | enum: my, team, global... |  | Filter the results to labels based on their prefix. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `GET /custom-content/{id}/labels`
Get labels for custom content
Returns the labels for a specific piece of custom content. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content and its corresponding space.
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content for which labels should be returned. |
| `prefix` | query | enum: my, team, global... |  | Filter the results to labels based on their prefix. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /labels`
Get labels
Returns all labels. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `label-id` | query | array |  | Filters on label ID. Multiple IDs can be specified as a comma-separated list. |
| `prefix` | query | array |  | Filters on label prefix. Multiple IDs can be specified as a comma-separated list. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `GET /pages/{id}/labels`
Get labels for page
Returns the labels of specific page. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which labels should be returned. |
| `prefix` | query | enum: my, team, global... |  | Filter the results to labels based on their prefix. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /spaces/{id}/labels`
Get labels for space
Returns the labels of specific space. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the space.
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which labels should be returned. |
| `prefix` | query | enum: my, team |  | Filter the results to labels based on their prefix. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested space or the space was not found.

#### `GET /spaces/{id}/content/labels`
Get labels for space content
Returns the labels of space content (pages, blogposts etc). The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the space.
Only labels that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which labels should be returned. |
| `prefix` | query | enum: my, team |  | Filter the results to labels based on their prefix. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of labels per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested labels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested space or the space was not found.


### Attachment
#### `GET /attachments`
Get attachments
Returns all attachments. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the container of the attachment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `status` | query | array |  | Filter the results to attachments based on their status. By default, `current` and `archived` are used. |
| `mediaType` | query | string |  | Filters on the mediaType of attachments. Only one may be specified. |
| `filename` | query | string |  | Filters on the file-name of attachments. Only one may be specified. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested attachments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `GET /attachments/{id}`
Get attachment by id
Returns a specific attachment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment's container.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | string | ✓ | The ID of the attachment to be returned. If you don't know the attachment's ID, use Get attachments for page/blogpost/custom content. |
| `version` | query | integer |  | Allows you to retrieve a previously published version. Specify the previous version's number to retrieve its details. |
| `include-labels` | query | boolean |  | Includes labels associated with this attachment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this attachment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-operations` | query | boolean |  | Includes operations associated with this attachment in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-versions` | query | boolean |  | Includes versions associated with this attachment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-version` | query | boolean |  | Includes the current version associated with this attachment in the response. By default this is included and can be omitted by setting the value to `false`. |
| `include-collaborators` | query | boolean |  | Includes collaborators on the attachment. |
**Responses:**

- **200**: Returned if the requested attachment is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested attachment or the attachment was not found.

#### `DELETE /attachments/{id}`
Delete attachment
Delete an attachment by id.

Deleting an attachment moves the attachment to the trash, where it can be restored later. To permanently delete an attachment (or "purge" it),
the endpoint must be called on a **trashed** attachment with the following param `purge=true`.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the container of the attachment.
Permission to delete attachments in the space.
Permission to administer the space (if attempting to purge).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the attachment to be deleted. |
| `purge` | query | boolean |  | If attempting to purge the attachment. |
**Responses:**

- **204**: Returned if the attachment was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided attachment does not exist
- The user does not have permissions to view the container of the attachment
- The user does not have the needed permissions to delete an attachment in the space

#### `GET /blogposts/{id}/attachments`
Get attachments for blog post
Returns the attachments of specific blog post. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which attachments should be returned. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `status` | query | array |  | Filter the results to attachments based on their status. By default, `current` and `archived` are used. |
| `mediaType` | query | string |  | Filters on the mediaType of attachments. Only one may be specified. |
| `filename` | query | string |  | Filters on the file-name of attachments. Only one may be specified. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested attachments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `GET /custom-content/{id}/attachments`
Get attachments for custom content
Returns the attachments of specific custom content. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the custom content and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content for which attachments should be returned. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `status` | query | array |  | Filter the results to attachments based on their status. By default, `current` and `archived` are used. |
| `mediaType` | query | string |  | Filters on the mediaType of attachments. Only one may be specified. |
| `filename` | query | string |  | Filters on the file-name of attachments. Only one may be specified. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested attachments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested custom content or the custom content was not found.

#### `GET /labels/{id}/attachments`
Get attachments for label
Returns the attachments of specified label. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the label for which attachments should be returned. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested attachments for specified label were successfully fetched.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested label or label was not found.

#### `GET /pages/{id}/attachments`
Get attachments for page
Returns the attachments of specific page. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which attachments should be returned. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `status` | query | array |  | Filter the results to attachments based on their status. By default, `current` and `archived` are used. |
| `mediaType` | query | string |  | Filters on the mediaType of attachments. Only one may be specified. |
| `filename` | query | string |  | Filters on the file-name of attachments. Only one may be specified. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested attachments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.


### Comment
#### `GET /attachments/{id}/footer-comments`
Get attachment comments
Returns the comments of the specific attachment.
The number of results is limited by the `limit` parameter and additional results (if available) will be available through
the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment and its corresponding containers.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | string | ✓ | The ID of the attachment for which comments should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `version` | query | integer |  | Version number of the attachment to retrieve comments for. If no version provided, retrieves comments for the latest version. |
**Responses:**

- **200**: Returned if the attachment comments were successfully retrieved
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
attachment or associated containers.

#### `GET /custom-content/{id}/footer-comments`
Get custom content comments
Returns the comments of the specific custom content.
The number of results is limited by the `limit` parameter and additional results (if available) will be available through
the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content and its corresponding containers.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content for which comments should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the custom content comments were successfully retrieved
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
custom content or associated containers.

#### `GET /pages/{id}/footer-comments`
Get footer comments for page
Returns the root footer comments of specific page. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which footer comments should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `status` | query | array |  | Filter the footer comment being retrieved by its status. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of footer comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested footer comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /pages/{id}/inline-comments`
Get inline comments for page
Returns the root inline comments of specific page. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which inline comments should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `status` | query | array |  | Filter the inline comment being retrieved by its status. |
| `resolution-status` | query | array |  | Filter the inline comment being retrieved by its resolution status. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of inline comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested inline comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /blogposts/{id}/footer-comments`
Get footer comments for blog post
Returns the root footer comments of specific blog post. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which footer comments should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `status` | query | array |  | Filter the footer comment being retrieved by its status. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of footer comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested footer comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `GET /blogposts/{id}/inline-comments`
Get inline comments for blog post
Returns the root inline comments of specific blog post. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which inline comments should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `status` | query | array |  | Filter the inline comment being retrieved by its status. |
| `resolution-status` | query | array |  | Filter the inline comment being retrieved by its resolution status. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of inline comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested inline comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `GET /footer-comments`
Get footer comments
Returns all footer comments. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the container and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of footer comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested footer comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `POST /footer-comments`
Create footer comment
Create a footer comment.

The footer comment can be made against several locations: 
- at the top level (specifying pageId or blogPostId in the request body)
- as a reply (specifying parentCommentId in the request body)
- against an attachment (note: this is different than the comments added via the attachment properties page on the UI, which are referred to as version comments)
- against a custom content

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to create comments in the space.

**Request Body:**

Schema: `CreateFooterCommentModel`

**Responses:**

- **201**: Returned if the footer comment is created.
- **400**: Returned if an invalid request is provided
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The page, blog post, parent comment, or attachment was not found
- The calling user does not have permission to view the parent page/blog post
- The user is forbidden from creating a comment tied to a resource they are allowed to view

#### `GET /footer-comments/{comment-id}`
Get footer comment by id
Retrieves a footer comment by id

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the container and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to be retrieved. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `version` | query | integer |  | Allows you to retrieve a previously published version. Specify the previous version's number to retrieve its details. |
| `include-properties` | query | boolean |  | Includes content properties associated with this footer comment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-operations` | query | boolean |  | Includes operations associated with this footer comment in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-likes` | query | boolean |  | Includes likes associated with this footer comment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-versions` | query | boolean |  | Includes versions associated with this footer comment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-version` | query | boolean |  | Includes the current version associated with this footer comment in the response. By default this is included and can be omitted by setting the value to `false`. |
**Responses:**

- **200**: Returned if the footer comment is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
comment or the comment was not found.

#### `PUT /footer-comments/{comment-id}`
Update footer comment
Update a footer comment. This can be used to update the body text of a comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to create comments in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to be retrieved. |

**Request Body:**

Type: `object`

**Responses:**

- **200**: Returned if the footer comment is updated successfully
- **400**: Returned if an invalid request is provided
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The comment was not found
- The calling user does not have permission to view the comment
- The user is forbidden from updating a comment tied to a resource they are allowed to view

#### `DELETE /footer-comments/{comment-id}`
Delete footer comment
Deletes a footer comment. This is a permanent deletion and cannot be reverted.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to delete comments in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to be retrieved. |
**Responses:**

- **204**: Returned if the footer comment is deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The comment was not found
- The calling user does not have permission to view the comment
- The user is forbidden from deleting a comment tied to a resource they are allowed to view

#### `GET /footer-comments/{id}/children`
Get children footer comments
Returns the children footer comments of specific comment. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent comment for which footer comment children should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of footer comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested footer comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent page/blog post or the page/blog post was not found.

#### `GET /inline-comments`
Get inline comments
Returns all inline comments. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of footer comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested inline comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `POST /inline-comments`
Create inline comment
Create an inline comment. This can be at the top level (specifying pageId or blogPostId in the request body)
or as a reply (specifying parentCommentId in the request body). Note the inlineCommentProperties object in the
request body is used to select the text the inline comment should be tied to. This is what determines the text 
highlighting when viewing a page in Confluence.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to create comments in the space.

**Request Body:**

Schema: `CreateInlineCommentModel`

**Responses:**

- **201**: Returned if the inline comment is created.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The page/blog post was not found
- The calling user does not have permission to view the parent page/blog post
- The user is forbidden from creating a comment tied to a resource they are allowed to view

#### `GET /inline-comments/{comment-id}`
Get inline comment by id
Retrieves an inline comment by id

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to be retrieved. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `version` | query | integer |  | Allows you to retrieve a previously published version. Specify the previous version's number to retrieve its details. |
| `include-properties` | query | boolean |  | Includes content properties associated with this inline comment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-operations` | query | boolean |  | Includes operations associated with this inline comment in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-likes` | query | boolean |  | Includes likes associated with this inline comment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-versions` | query | boolean |  | Includes versions associated with this inline comment in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-version` | query | boolean |  | Includes the current version associated with this inline comment in the response. By default this is included and can be omitted by setting the value to `false`. |
**Responses:**

- **200**: Returned if the inline comment is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
comment or the comment was not found.

#### `PUT /inline-comments/{comment-id}`
Update inline comment
Update an inline comment. This can be used to update the body text of a comment and/or to resolve the comment

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to create comments in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to be retrieved. |

**Request Body:**

Schema: `UpdateInlineCommentModel`

**Responses:**

- **200**: Returned if the inline comment is updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The comment was not found
- The calling user does not have permission to view the comment
- The user is forbidden from updating a comment tied to a resource they are allowed to view

#### `DELETE /inline-comments/{comment-id}`
Delete inline comment
Deletes an inline comment. This is a permanent deletion and cannot be reverted.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to delete comments in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to be deleted. |
**Responses:**

- **204**: Returned if the inline comment is deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The comment was not found
- The calling user does not have permission to view the comment
- The user is forbidden from deleting a comment tied to a resource they are allowed to view

#### `GET /inline-comments/{id}/children`
Get children inline comments
Returns the children inline comments of specific comment. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent comment for which inline comment children should be returned. |
| `body-format` | query | object |  | The content format type to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of footer comments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested footer comments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent page/blog post or the page/blog post was not found.


### Version
#### `GET /attachments/{id}/versions`
Get attachment versions
Returns the versions of specific attachment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | string | ✓ | The ID of the attachment to be queried for its versions. If you don't know the attachment ID, use Get attachments and filter the results. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of versions per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested attachment versions are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /attachments/{attachment-id}/versions/{version-number}`
Get version details for attachment version
Retrieves version details for the specified attachment and version number.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `attachment-id` | path | string | ✓ | The ID of the attachment for which version details should be returned. |
| `version-number` | path | integer | ✓ | The version number of the attachment to be returned. |
**Responses:**

- **200**: Returned if the requested version details are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified attachment, the attachment was not found, or the version number does not exist.

#### `GET /blogposts/{id}/versions`
Get blog post versions
Returns the versions of specific blog post. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post to be queried for its versions. If you don't know the blog post ID, use Get blog posts and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of versions per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested blog post versions are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /blogposts/{blogpost-id}/versions/{version-number}`
Get version details for blog post version
Retrieves version details for the specified blog post and version number.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `blogpost-id` | path | integer | ✓ | The ID of the blog post for which version details should be returned. |
| `version-number` | path | integer | ✓ | The version number of the blog post to be returned. |
**Responses:**

- **200**: Returned if the requested version details are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified blog post, the blog post was not found, or the version number does not exist.

#### `GET /pages/{id}/versions`
Get page versions
Returns the versions of specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page to be queried for its versions. If you don't know the page ID, use Get pages and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of versions per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested page versions are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /pages/{page-id}/versions/{version-number}`
Get version details for page version
Retrieves version details for the specified page and version number.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `page-id` | path | integer | ✓ | The ID of the page for which version details should be returned. |
| `version-number` | path | integer | ✓ | The version number of the page to be returned. |
**Responses:**

- **200**: Returned if the requested version details are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page, the page was not found, or the version number does not exist.

#### `GET /custom-content/{custom-content-id}/versions`
Get custom content versions
Returns the versions of specific custom content.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content and its corresponding page and space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content to be queried for its versions. If you don't know the custom content ID, use Get custom-content by type and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field.  Note: If the custom content body type is `storage`, the `storage` and `atlas_doc_format` body formats are able to be returned. If the custom content body type is `raw`, only the `raw` body format is able to be returned. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of versions per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested custom content versions are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested custom content or the custom content was not found.

#### `GET /custom-content/{custom-content-id}/versions/{version-number}`
Get version details for custom content version
Retrieves version details for the specified custom content and version number.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content for which version details should be returned. |
| `version-number` | path | integer | ✓ | The version number of the custom content to be returned. |
**Responses:**

- **200**: Returned if the requested version details are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified custom content, the custom content was not found, or the version number does not exist.

#### `GET /footer-comments/{id}/versions`
Get footer comment versions
Retrieves the versions of the specified footer comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the footer comment for which versions should be returned |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of versions per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested footer comment versions are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the specified page
or blog post, the footer comment was not found, or the version number does not exist.

#### `GET /footer-comments/{id}/versions/{version-number}`
Get version details for footer comment version
Retrieves version details for the specified footer comment version.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the footer comment for which version details should be returned. |
| `version-number` | path | integer | ✓ | The version number of the footer comment to be returned. |
**Responses:**

- **200**: Returned if the requested version details are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the specified page
or blog post, the footer comment was not found, or the version number does not exist.

#### `GET /inline-comments/{id}/versions`
Get inline comment versions
Retrieves the versions of the specified inline comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the inline comment for which versions should be returned |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of versions per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested inline comment versions are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the specified page
or blog post, the inline comment was not found, or the version number does not exist.

#### `GET /inline-comments/{id}/versions/{version-number}`
Get version details for inline comment version
Retrieves version details for the specified inline comment version.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the inline comment for which version details should be returned. |
| `version-number` | path | integer | ✓ | The version number of the inline comment to be returned. |
**Responses:**

- **200**: Returned if the requested version details are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the specified page
or blog post, the inline comment was not found, or the version number does not exist.


### Ancestors
#### `GET /whiteboards/{id}/ancestors`
Get all ancestors of whiteboard
Returns all ancestors for a given whiteboard by ID in top-to-bottom order (that is, the highest ancestor is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the ID of first ancestor in the response payload.

This endpoint returns minimal information about each ancestor. To fetch more details, use a related endpoint, such
as [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the whiteboard and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the highest ancestor's ID to fetch the next set of results. |
**Responses:**

- **200**: Returned if the requested ancestors are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard or the whiteboard was not found.

#### `GET /databases/{id}/ancestors`
Get all ancestors of database
Returns all ancestors for a given database by ID in top-to-bottom order (that is, the highest ancestor is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the ID of first ancestor in the response payload.

This endpoint returns minimal information about each ancestor. To fetch more details, use a related endpoint, such
as [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the database and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the highest ancestor's ID to fetch the next set of results. |
**Responses:**

- **200**: Returned if the requested ancestors are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `GET /embeds/{id}/ancestors`
Get all ancestors of Smart Link in content tree
Returns all ancestors for a given Smart Link in the content tree by ID in top-to-bottom order (that is, the highest ancestor is
the first item in the response payload). The number of results is limited by the `limit` parameter and additional results 
(if available) will be available by calling this endpoint with the ID of first ancestor in the response payload.

This endpoint returns minimal information about each ancestor. To fetch more details, use a related endpoint, such
as [Get Smart Link in the content tree by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the Smart Link in the content tree and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the Smart Link in the content tree. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the highest ancestor's ID to fetch the next set of results. |
**Responses:**

- **200**: Returned if the requested ancestors are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified Smart Link in the content tree or the Smart Link was not found.

#### `GET /folders/{id}/ancestors`
Get all ancestors of folder
Returns all ancestors for a given folder by ID in top-to-bottom order (that is, the highest ancestor is
the first item in the response payload). The number of results is limited by the `limit` parameter and additional results 
(if available) will be available by calling this endpoint with the ID of first ancestor in the response payload.

This endpoint returns minimal information about each ancestor. To fetch more details, use a related endpoint, such
as [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-folders-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the folder and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the highest ancestor's ID to fetch the next set of results. |
**Responses:**

- **200**: Returned if the requested ancestors are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `GET /pages/{id}/ancestors`
Get all ancestors of page
Returns all ancestors for a given page by ID in top-to-bottom order (that is, the highest ancestor is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the ID of first ancestor in the response payload.

This endpoint returns minimal information about each ancestor. To fetch more details, use a related endpoint, such
as [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, call this endpoint with the highest ancestor's ID to fetch the next set of results. |
**Responses:**

- **200**: Returned if the requested ancestors are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.


### Children
#### `GET /whiteboards/{id}/direct-children`
Get direct children of a whiteboard
Returns all children for given whiteboard id in the content tree. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each child. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only content that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent whiteboard. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested children are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `GET /databases/{id}/direct-children`
Get direct children of a database
Returns all children for given database id in the content tree. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each child. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only content that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent database. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested children are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `GET /embeds/{id}/direct-children`
Get direct children of a Smart Link
Returns all children for given smart link id in the content tree. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each child. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only content that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent smart link. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested children are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified smart link or the smart link was not found.

#### `GET /folders/{id}/direct-children`
Get direct children of a folder
Returns all children for given folder id in the content tree. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each child. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only content that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent folder. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested children are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `GET /pages/{id}/children`
Get child pages
Returns all child pages for given page id. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only pages that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent page. If you don't know the page ID, use Get pages and filter the results. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested child pages are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `GET /custom-content/{id}/children`
Get child custom content
Returns all child custom content for given custom content id. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only custom content that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent custom content. If you don't know the custom content ID, use Get custom-content and filter the results. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested child custom content are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `GET /pages/{id}/direct-children`
Get direct children of a page
Returns all children for given page id in the content tree. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each child. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only content that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the parent page. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `sort` | query | string |  | Used to sort the result by a particular field. |
**Responses:**

- **200**: Returned if the requested children are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.


### Descendants
#### `GET /whiteboards/{id}/descendants`
Get descendants of a whiteboard
Returns descendants in the content tree for a given whiteboard by ID in top-to-bottom order (that is, the highest descendant is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the cursor in the response payload. There is also a `depth` parameter specifying depth
of descendants to be fetched.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each descendant. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the whiteboard and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the cursor to fetch the next set of results. |
| `depth` | query | integer |  | Maximum depth of descendants to return. If more results are required, use the endpoint corresponding to the content type of the deepest descendant to fetch more descendants. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
**Responses:**

- **200**: Returned if the requested descendants are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard or the whiteboard was not found.
content: { }

#### `GET /databases/{id}/descendants`
Get descendants of a database
Returns descendants in the content tree for a given database by ID in top-to-bottom order (that is, the highest descendant is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the cursor in the response payload. There is also a `depth` parameter specifying depth
of descendants to be fetched.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each descendant. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the database and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the cursor to fetch the next set of results. |
| `depth` | query | integer |  | Maximum depth of descendants to return. If more results are required, use the endpoint corresponding to the content type of the deepest descendant to fetch more descendants. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
**Responses:**

- **200**: Returned if the requested descendants are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `GET /embeds/{id}/descendants`
Get descendants of a smart link
Returns descendants in the content tree for a given smart link by ID in top-to-bottom order (that is, the highest descendant is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the cursor in the response payload. There is also a `depth` parameter specifying depth
of descendants to be fetched.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard


This endpoint returns minimal information about each descendant. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the smart link and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the smart link. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the cursor to fetch the next set of results. |
| `depth` | query | integer |  | Maximum depth of descendants to return. If more results are required, use the endpoint corresponding to the content type of the deepest descendant to fetch more descendants. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
**Responses:**

- **200**: Returned if the requested descendants are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified smart link or the smart link was not found.

#### `GET /folders/{id}/descendants`
Get descendants of folder
Returns descendants in the content tree for a given folder by ID in top-to-bottom order (that is, the highest descendant is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the cursor in the response payload. There is also a `depth` parameter specifying depth
of descendants to be fetched.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each descendant. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the  and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the cursor to fetch the next set of results. |
| `depth` | query | integer |  | Maximum depth of descendants to return. If more results are required, use the endpoint corresponding to the content type of the deepest descendant to fetch more descendants. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
**Responses:**

- **200**: Returned if the requested descendants are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `GET /pages/{id}/descendants`
Get descendants of page
Returns descendants in the content tree for a given page by ID in top-to-bottom order (that is, the highest descendant is the first
item in the response payload). The number of results is limited by the `limit` parameter and additional results (if available)
will be available by calling this endpoint with the cursor in the response payload. There is also a `depth` parameter specifying depth
of descendants to be fetched.

The following types of content will be returned:
- Database
- Embed
- Folder
- Page
- Whiteboard

This endpoint returns minimal information about each descendant. To fetch more details, use a related endpoint based on the content type, such
as:

- [Get database by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-database/#api-databases-id-get)
- [Get embed by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-smart-link/#api-embeds-id-get)
- [Get folder by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-folder/#api-folders-id-get)
- [Get page by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-id-get)
- [Get whiteboard by id](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-whiteboard/#api-whiteboards-id-get).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Permission to view the page and its corresponding space

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page. |
| `limit` | query | integer |  | Maximum number of items per result to return. If more results exist, call the endpoint with the cursor to fetch the next set of results. |
| `depth` | query | integer |  | Maximum depth of descendants to return. If more results are required, use the endpoint corresponding to the content type of the deepest descendant to fetch more descendants. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
**Responses:**

- **200**: Returned if the requested descendants are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.


## Additional Endpoints

### Admin Key
#### `GET /admin-key`
Get Admin Key
Returns information about the admin key if one is currently enabled for the calling user within the site.

**[Permissions](https://support.atlassian.com/user-management/docs/give-users-admin-permissions/#Centralized-user-management-content) required**:
User must be an organization or site admin.
**Responses:**

- **200**: Returned if an admin key is currently enabled for the calling user.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not currently have an admin key, if the calling user does not have permission to use admin keys, or if the site is not a Confluence Cloud Premium or Enterprise instance.

#### `POST /admin-key`
Enable Admin Key
Enables admin key access for the calling user within the site. If an admin key already exists for the user, a new one will be issued with an updated expiration time.

**Note:** The `durationInMinutes` field within the request body is optional. If the request body is empty or if the `durationInMinutes` is set to 0 minutes, a new admin key will be issued to the calling user with a default duration of 10 minutes.

**[Permissions](https://support.atlassian.com/user-management/docs/give-users-admin-permissions/#Centralized-user-management-content) required**:
User must be an organization or site admin.
**Responses:**

- **200**: Returned if a new admin key is successfully issued for the calling user.
- **400**: Returned if the request body contains an invalid `durationInMinutes`.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not have permission to use admin keys or if the site is not a Confluence Cloud Premium or Enterprise instance.

#### `DELETE /admin-key`
Disable Admin Key
Disables admin key access for the calling user within the site.

**[Permissions](https://support.atlassian.com/user-management/docs/give-users-admin-permissions/#Centralized-user-management-content) required**:
User must be an organization or site admin.
**Responses:**

- **204**: Returned if admin key access was successfully disabled for the calling user or if the user did not have an admin key in the first place.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not have permission to use admin keys or if the site is not a Confluence Cloud Premium or Enterprise instance.


### App Properties
#### `GET /app/properties`
Get Forge app properties.
Gets Forge app properties. This API can only be accessed using **[asApp()](https://developer.atlassian.com/platform/forge/apis-reference/fetch-api-product.requestconfluence/#method-signature)** requests from Forge.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `cursor` | query | string |  | Used for pagination, this opaque cursor represents the last returned property key. It will be included in the response body as the next link. Use this key to request the next set of results. |
| `limit` | query | integer |  | Maximum number of app properties per result to return. If more results exist, use the last returned property key from the Link field in the response body as a cursor to retrieve the next set of results. |
**Responses:**

- **200**: Forge app properties returned on success.
- **401**: The request did not originate from the Forge app.
- **403**: Returned when the request is forbidden due to one of the following:
- The request attempts impersonation. Only requests made using `asApp()` are allowed.
- The Forge app is not installed.

#### `GET /app/properties/{propertyKey}`
Get a Forge app property by key.
Gets a Forge app property by property key. This API can only be accessed using **[asApp()](https://developer.atlassian.com/platform/forge/apis-reference/fetch-api-product.requestconfluence/#method-signature)** requests from Forge.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `propertyKey` | path | string | ✓ | The key of the property |
**Responses:**

- **200**: App property returned on success.
- **400**: Property key longer than 127 characters.
- **401**: The request did not originate from the Forge app.
- **403**: Returned when the request is forbidden due to one of the following:
- The request attempts impersonation. Only requests made using `asApp()` are allowed.
- The Forge app is not installed.
- **404**: App property not found.

#### `PUT /app/properties/{propertyKey}`
Create or update a Forge app property.
Creates or updates a Forge app property. This API can only be accessed using **[asApp()](https://developer.atlassian.com/platform/forge/apis-reference/fetch-api-product.requestconfluence/#method-signature)** requests from Forge.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `propertyKey` | path | string | ✓ | The key of the property |

**Request Body:**

Type: `object`

**Responses:**

- **200**: Property updated.
- **201**: Property created.
- **400**: Property key longer than 127 characters, or request made with invalid JSON.
- **401**: The request did not originate from the Forge app.
- **403**: Returned when the request is forbidden due to one of the following:
- The request attempts impersonation. Only requests made using `asApp()` are allowed.
- The Forge app is not installed.

#### `DELETE /app/properties/{propertyKey}`
Deletes a Forge app property.
Deletes a Forge app property. This API can only be accessed using **[asApp()](https://developer.atlassian.com/platform/forge/apis-reference/fetch-api-product.requestconfluence/#method-signature)** requests from Forge.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `propertyKey` | path | string | ✓ | The key of the property |
**Responses:**

- **204**: Property deleted.
- **400**: Property key longer than 127 characters
- **401**: The request did not originate from the Forge app.
- **403**: Returned when the request is forbidden due to one of the following:
- The request attempts impersonation. Only requests made using `asApp()` are allowed.
- The Forge app is not installed.


### Classification Level
#### `GET /classification-levels`
Get list of classification levels
Returns a list of [classification levels](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level) 
available.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission).
**Responses:**

- **200**: Returned if classifications levels are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Classification levels do not exist
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permissions to access the Confluence site


#### `GET /spaces/{id}/classification-level/default`
Get space default classification level
Returns the [default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/) 
for a specific space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which default classification level should be returned. |
**Responses:**

- **200**: Returned if the requested default classification level for a space is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Default classification level is not applied to the space
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified space or the space was not found

#### `PUT /spaces/{id}/classification-level/default`
Update space default classification level
Update the [default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/) 
for a specific space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and 'Admin' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which default classification level should be updated. |
**Responses:**

- **204**: Returned if the default classification level was successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified space or the space was not found

#### `DELETE /spaces/{id}/classification-level/default`
Delete space default classification level
Returns the [default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/) 
for a specific space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and 'Admin' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which default classification level should be deleted. |
**Responses:**

- **204**: Returned if the default classification level was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified space or the space was not found

#### `GET /pages/{id}/classification-level`
Get page classification level
Returns the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the page.
'Permission to edit the page is required if trying to view classification level for a draft.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which classification level should be returned. |
| `status` | query | enum: current, draft, archived |  | Status of page from which classification level will fetched. |
**Responses:**

- **200**: Returned if the requested classification level for a page is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Page does not have a classification level applied
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified page or the page was not found
- The calling user does not have permission to edit the specified page when trying to fetch classification level for a draft

#### `PUT /pages/{id}/classification-level`
Update page classification level
Updates the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to edit the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified page or the page was not found

#### `POST /pages/{id}/classification-level/reset`
Reset page classification level
Resets the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific page for the space 
[default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully reset.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified page or the page was not found

#### `GET /blogposts/{id}/classification-level`
Get blog post classification level
Returns the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the blog post.
'Permission to edit the blog post is required if trying to view classification level for a draft.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which classification level should be returned. |
| `status` | query | enum: current, draft, archived |  | Status of blog post from which classification level will fetched. |
**Responses:**

- **200**: Returned if the requested classification level for a blog post is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Blog post does not have a classification level applied
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified blog post or the blog post was not found
- The calling user does not have permission to edit the specified blog post when trying to fetch classification level for a draft

#### `PUT /blogposts/{id}/classification-level`
Update blog post classification level
Updates the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to edit the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified blog post or the blog post was not found

#### `POST /blogposts/{id}/classification-level/reset`
Reset blog post classification level
Resets the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific blog post for the space  
[default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully reset.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified blog post or the blog post was not found

#### `GET /whiteboards/{id}/classification-level`
Get whiteboard classification level
Returns the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard for which classification level should be returned. |
**Responses:**

- **200**: Returned if the requested classification level for a whiteboard is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Whiteboard does not have a classification level applied
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified whiteboard, or the whiteboard was not found

#### `PUT /whiteboards/{id}/classification-level`
Update whiteboard classification level
Updates the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to edit the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified whiteboard
- The whiteboard or classification level was not found

#### `POST /whiteboards/{id}/classification-level/reset`
Reset whiteboard classification level
Resets the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific whiteboard for the space 
[default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully reset.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified whiteboard, or the whiteboard was not found

#### `GET /databases/{id}/classification-level`
Get database classification level
Returns the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database for which classification level should be returned. |
**Responses:**

- **200**: Returned if the requested classification level for a database is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Database does not have a classification level applied
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to view the specified database, or the database was not found

#### `PUT /databases/{id}/classification-level`
Update database classification level
Updates the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to edit the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified database
- The database or the classification level was not found

#### `POST /databases/{id}/classification-level/reset`
Reset database classification level
Resets the [classification level](https://developer.atlassian.com/cloud/admin/dlp/rest/intro/#Classification%20level)
for a specific database for the space 
[default classification level](https://support.atlassian.com/security-and-access-policies/docs/what-is-a-default-classification-level/).

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
'Permission to access the Confluence site ('Can use' global permission) and permission to view the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database for which classification level should be updated. |
**Responses:**

- **204**: Returned if the classification level was successfully reset.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- Site's edition does not have entitlement(s) for [data classification](https://support.atlassian.com/security-and-access-policies/docs/what-is-data-classification/)
- The calling user does not have permission to edit the specified database, or the database was not found


### Content
#### `POST /content/convert-ids-to-types`
Convert content ids to content types
Converts a list of content ids into their associated content types. This is useful for users migrating from v1 to v2
who may have stored just content ids without their associated type. This will return types as they should be used in v2.
Notably, this will return `inline-comment` for inline comments and `footer-comment` for footer comments, which is distinct from them
both being represented by `comment` in v1.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the requested content. Any content that the user does not have permission to view or does not exist will map to `null` in the response.
**Responses:**

- **200**: Returned if the requested content ids are successfully converted to their content types
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.


### Content Properties
#### `GET /attachments/{attachment-id}/properties`
Get content properties for attachment
Retrieves all Content Properties tied to a specified attachment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `attachment-id` | path | string | ✓ | The ID of the attachment for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified attachment or the attachment was not found.

#### `POST /attachments/{attachment-id}/properties`
Create content property for attachment
Creates a new content property for an attachment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the attachment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `attachment-id` | path | string | ✓ | The ID of the attachment to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified attachment or the attachment was not found.

#### `GET /attachments/{attachment-id}/properties/{property-id}`
Get content property for attachment by id
Retrieves a specific Content Property by ID that is attached to a specified attachment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the attachment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `attachment-id` | path | string | ✓ | The ID of the attachment for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property to be returned |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified attachment,the attachment was not found, or the property was not found.

#### `PUT /attachments/{attachment-id}/properties/{property-id}`
Update content property for attachment by id
Update a content property for attachment by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the attachment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `attachment-id` | path | string | ✓ | The ID of the attachment the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified attachment or the attachment was not found.

#### `DELETE /attachments/{attachment-id}/properties/{property-id}`
Delete content property for attachment by id
Deletes a content property for an attachment by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to attachment the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `attachment-id` | path | string | ✓ | The ID of the attachment the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified attachment or the attachment was not found.

#### `GET /blogposts/{blogpost-id}/properties`
Get content properties for blog post
Retrieves all Content Properties tied to a specified blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `blogpost-id` | path | integer | ✓ | The ID of the blog post for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified blog post or the blog post was not found.

#### `POST /blogposts/{blogpost-id}/properties`
Create content property for blog post
Creates a new property for a blogpost.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `blogpost-id` | path | integer | ✓ | The ID of the blog post to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified blog post or the blog post was not found.

#### `GET /blogposts/{blogpost-id}/properties/{property-id}`
Get content property for blog post by id
Retrieves a specific Content Property by ID that is attached to a specified blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `blogpost-id` | path | integer | ✓ | The ID of the blog post for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the property being requested |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified blog post,the blog post was not found, or the property was not found.

#### `PUT /blogposts/{blogpost-id}/properties/{property-id}`
Update content property for blog post by id
Update a content property for blog post by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `blogpost-id` | path | integer | ✓ | The ID of the blog post the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified blog post or the blog post was not found.

#### `DELETE /blogposts/{blogpost-id}/properties/{property-id}`
Delete content property for blogpost by id
Deletes a content property for a blogpost by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the blog post.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `blogpost-id` | path | integer | ✓ | The ID of the blog post the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified blog post or the blog post was not found.

#### `GET /custom-content/{custom-content-id}/properties`
Get content properties for custom content
Retrieves Content Properties tied to a specified custom content.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified custom content or the custom content was not found.

#### `POST /custom-content/{custom-content-id}/properties`
Create content property for custom content
Creates a new content property for a piece of custom content.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the custom content.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified custom content or the custom content was not found.

#### `GET /custom-content/{custom-content-id}/properties/{property-id}`
Get content property for custom content by id
Retrieves a specific Content Property by ID that is attached to a specified custom content.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified custom content, the custom content was not found, or the property was not found.

#### `PUT /custom-content/{custom-content-id}/properties/{property-id}`
Update content property for custom content by id
Update a content property for a piece of custom content by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the custom content.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified custom content or the custom content was not found.

#### `DELETE /custom-content/{custom-content-id}/properties/{property-id}`
Delete content property for custom content by id
Deletes a content property for a piece of custom content by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the custom content.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `custom-content-id` | path | integer | ✓ | The ID of the custom content the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified custom content or the custom content was not found.

#### `GET /pages/{page-id}/properties`
Get content properties for page
Retrieves Content Properties tied to a specified page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `page-id` | path | integer | ✓ | The ID of the page for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.

#### `POST /pages/{page-id}/properties`
Create content property for page
Creates a new content property for a page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `page-id` | path | integer | ✓ | The ID of the page to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.

#### `GET /pages/{page-id}/properties/{property-id}`
Get content property for page by id
Retrieves a specific Content Property by ID that is attached to a specified page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `page-id` | path | integer | ✓ | The ID of the page for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page, the page was not found, or the property was not found.

#### `PUT /pages/{page-id}/properties/{property-id}`
Update content property for page by id
Update a content property for a page by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `page-id` | path | integer | ✓ | The ID of the page the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.

#### `DELETE /pages/{page-id}/properties/{property-id}`
Delete content property for page by id
Deletes a content property for a page by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the page.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `page-id` | path | integer | ✓ | The ID of the page the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.

#### `GET /whiteboards/{id}/properties`
Get content properties for whiteboard
Retrieves Content Properties tied to a specified whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard or the whiteboard was not found.

#### `POST /whiteboards/{id}/properties`
Create content property for whiteboard
Creates a new content property for a whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard or the whiteboard was not found.

#### `GET /whiteboards/{whiteboard-id}/properties/{property-id}`
Get content property for whiteboard by id
Retrieves a specific Content Property by ID that is attached to a specified whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `whiteboard-id` | path | integer | ✓ | The ID of the whiteboard for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard, the whiteboard was not found, or the property was not found.

#### `PUT /whiteboards/{whiteboard-id}/properties/{property-id}`
Update content property for whiteboard by id
Update a content property for a whiteboard by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `whiteboard-id` | path | integer | ✓ | The ID of the whiteboard the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard or the whiteboard was not found.

#### `DELETE /whiteboards/{whiteboard-id}/properties/{property-id}`
Delete content property for whiteboard by id
Deletes a content property for a whiteboard by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the whiteboard.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `whiteboard-id` | path | integer | ✓ | The ID of the whiteboard the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified whiteboard or the whiteboard was not found.

#### `GET /databases/{id}/properties`
Get content properties for database
Retrieves Content Properties tied to a specified database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `POST /databases/{id}/properties`
Create content property for database
Creates a new content property for a database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `GET /databases/{database-id}/properties/{property-id}`
Get content property for database by id
Retrieves a specific Content Property by ID that is attached to a specified database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `database-id` | path | integer | ✓ | The ID of the database for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database, the database was not found, or the property was not found.

#### `PUT /databases/{database-id}/properties/{property-id}`
Update content property for database by id
Update a content property for a database by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `database-id` | path | integer | ✓ | The ID of the database the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `DELETE /databases/{database-id}/properties/{property-id}`
Delete content property for database by id
Deletes a content property for a database by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the database.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `database-id` | path | integer | ✓ | The ID of the database the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified database or the database was not found.

#### `GET /embeds/{id}/properties`
Get content properties for Smart Link in the content tree
Retrieves Content Properties tied to a specified Smart Link in the content tree.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the Smart Link in the content tree.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the Smart Link in the content tree for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of Smart Links per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified Smart Link in the content tree or the Smart Link was not found.

#### `POST /embeds/{id}/properties`
Create content property for Smart Link in the content tree
Creates a new content property for a Smart Link in the content tree.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the Smart Link in the content tree.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the Smart Link in the content tree to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified Smart Link in the content tree or the Smart Link was not found.

#### `GET /embeds/{embed-id}/properties/{property-id}`
Get content property for Smart Link in the content tree by id
Retrieves a specific Content Property by ID that is attached to a specified Smart Link in the content tree.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the Smart Link in the content tree.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `embed-id` | path | integer | ✓ | The ID of the Smart Link in the content tree for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified Smart Link in the content tree, the Smart Link was not found, or the property was not found.

#### `PUT /embeds/{embed-id}/properties/{property-id}`
Update content property for Smart Link in the content tree by id
Update a content property for a Smart Link in the content tree by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the Smart Link in the content tree.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `embed-id` | path | integer | ✓ | The ID of the Smart Link in the content tree the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified Smart Link in the content tree or the Smart Link was not found.

#### `DELETE /embeds/{embed-id}/properties/{property-id}`
Delete content property for Smart Link in the content tree by id
Deletes a content property for a Smart Link in the content tree by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the Smart Link in the content tree.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `embed-id` | path | integer | ✓ | The ID of the Smart Link in the content tree the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified Smart Link in the content tree or the Smart Link was not found.

#### `GET /folders/{id}/properties`
Get content properties for folder
Retrieves Content Properties tied to a specified folder.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the folder.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `POST /folders/{id}/properties`
Create content property for folder
Creates a new content property for a folder.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the folder.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `GET /folders/{folder-id}/properties/{property-id}`
Get content property for folder by id
Retrieves a specific Content Property by ID that is attached to a specified folder.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the folder.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `folder-id` | path | integer | ✓ | The ID of the folder for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder, the folder was not found, or the property was not found.

#### `PUT /folders/{folder-id}/properties/{property-id}`
Update content property for folder by id
Update a content property for a folder by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the folder.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `folder-id` | path | integer | ✓ | The ID of the folder the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `DELETE /folders/{folder-id}/properties/{property-id}`
Delete content property for folder by id
Deletes a content property for a folder by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the folder.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `folder-id` | path | integer | ✓ | The ID of the folder the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified folder or the folder was not found.

#### `GET /comments/{comment-id}/properties`
Get content properties for comment
Retrieves Content Properties attached to a specified comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the comment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment for which content properties should be returned. |
| `key` | query | string |  | Filters the response to return a specific content property with matching key (case sensitive). |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of attachments per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested content properties are successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified comment or the comment was not found.

#### `POST /comments/{comment-id}/properties`
Create content property for comment
Creates a new content property for a comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to update the comment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment to create a property for. |

**Request Body:**

Schema: `ContentPropertyCreateRequest`

**Responses:**

- **200**: Returned if the content property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified page or the page was not found.

#### `GET /comments/{comment-id}/properties/{property-id}`
Get content property for comment by id
Retrieves a specific Content Property by ID that is attached to a specified comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the comment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment for which content properties should be returned. |
| `property-id` | path | integer | ✓ | The ID of the content property being requested. |
**Responses:**

- **200**: Returned if the requested content property is successfully retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified comment, the comment was not found, or the property was not found.

#### `PUT /comments/{comment-id}/properties/{property-id}`
Update content property for comment by id
Update a content property for a comment by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the comment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `ContentPropertyUpdateRequest`

**Responses:**

- **200**: Returned if the content property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified comment or the comment was not found.

#### `DELETE /comments/{comment-id}/properties/{property-id}`
Delete content property for comment by id
Deletes a content property for a comment by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the comment.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `comment-id` | path | integer | ✓ | The ID of the comment the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the content property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified comment or the comment was not found.


### Custom Content
#### `GET /blogposts/{id}/custom-content`
Get custom content by type in blog post
Returns all custom content for a given type within a given blogpost. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content, the container of the custom content (blog post), and the corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which custom content should be returned. |
| `type` | query | string | ✓ | The type of custom content being requested. See: https://developer.atlassian.com/cloud/confluence/custom-content/ for additional details on custom content. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field.  Note: If the custom content body type is `storage`, the `storage` and `atlas_doc_format` body formats are able to be returned. If the custom content body type is `raw`, only the `raw` body format is able to be returned. |
**Responses:**

- **200**: Returned if the requested custom content is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the given blog post is not found. Returned if the type of custom content is not found. Note, this is distinct from the type being present, but no instances of the type, which would be a 200 with empty results.

#### `GET /custom-content`
Get custom content by type
Returns all custom content for a given type. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content, the container of the custom content, and the corresponding space (if different from the container).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `type` | query | string | ✓ | The type of custom content being requested. See: https://developer.atlassian.com/cloud/confluence/custom-content/ for additional details on custom content. |
| `id` | query | array |  | Filter the results based on custom content ids. Multiple custom content ids can be specified as a comma-separated list. |
| `space-id` | query | array |  | Filter the results based on space ids. Multiple space ids can be specified as a comma-separated list. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field.  Note: If the custom content body type is `storage`, the `storage` and `atlas_doc_format` body formats are able to be returned. If the custom content body type is `raw`, only the `raw` body format is able to be returned. |
**Responses:**

- **200**: Returned if the requested custom content is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the type of custom content is not found. Note, this is distinct from the type being present, but no instances of the type, which would be a 200 with empty results.

#### `POST /custom-content`
Create custom content
Creates a new custom content in the given space, page, blogpost or other custom content.

Only one of `spaceId`, `pageId`, `blogPostId`, or `customContentId` is required in the request body.
**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to create custom content in the space.
**Responses:**

- **201**: Returned if the requested custom content is created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the type of custom content is not found.

#### `GET /custom-content/{id}`
Get custom content by id
Returns a specific piece of custom content. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content, the container of the custom content, and the corresponding space (if different from the container).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content to be returned. If you don't know the custom content ID, use Get Custom Content by Type and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field.  Note: If the custom content body type is `storage`, the `storage` and `atlas_doc_format` body formats are able to be returned. If the custom content body type is `raw`, only the `raw` body format is able to be returned. |
| `version` | query | integer |  | Allows you to retrieve a previously published version. Specify the previous version's number to retrieve its details. |
| `include-labels` | query | boolean |  | Includes labels associated with this custom content in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this custom content in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-operations` | query | boolean |  | Includes operations associated with this custom content in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-versions` | query | boolean |  | Includes versions associated with this custom content in the response. The number of results will be limited to 50 and sorted in the default sort order.  A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-version` | query | boolean |  | Includes the current version associated with this custom content in the response. By default this is included and can be omitted by setting the value to `false`. |
| `include-collaborators` | query | boolean |  | Includes collaborators on the custom content. |
**Responses:**

- **200**: Returned if the requested custom content is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested custom content or the custom content was not found.

#### `PUT /custom-content/{id}`
Update custom content
Update a custom content by id.
At most one of `spaceId`, `pageId`, `blogPostId`, or `customContentId` is allowed in the request body.
Note that if `spaceId` is specified, it must be the same as the `spaceId` used for creating the custom content
as moving custom content to a different space is not supported.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space. Permission to update custom content in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content to be updated. If you don't know the custom content ID, use Get Custom Content by Type and filter the results. |
**Responses:**

- **200**: Returned if the requested custom content is updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the type of custom content is not found.

#### `DELETE /custom-content/{id}`
Delete custom content
Delete a custom content by id.

Deleting a custom content will either move it to the trash or permanently delete it (purge it), depending on the apiSupport.
To permanently delete a **trashed** custom content, the endpoint must be called with the following param `purge=true`.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page or blogpost and its corresponding space.
Permission to delete custom content in the space.
Permission to administer the space (if attempting to purge).

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content to be deleted. |
| `purge` | query | boolean |  | If attempting to purge the custom content. |
**Responses:**

- **204**: Returned if the custom content was deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the custom content is not found.

#### `GET /pages/{id}/custom-content`
Get custom content by type in page
Returns all custom content for a given type within a given page. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content, the container of the custom content (page), and the corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which custom content should be returned. |
| `type` | query | string | ✓ | The type of custom content being requested. See: https://developer.atlassian.com/cloud/confluence/custom-content/ for additional details on custom content. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field.  Note: If the custom content body type is `storage`, the `storage` and `atlas_doc_format` body formats are able to be returned. If the custom content body type is `raw`, only the `raw` body format is able to be returned. |
**Responses:**

- **200**: Returned if the requested custom content is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the given page is not found. Returned if the type of custom content is not found. Note, this is distinct from the type being present, but no instances of the type, which would be a 200 with empty results.

#### `GET /spaces/{id}/custom-content`
Get custom content by type in space
Returns all custom content for a given type within a given space. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the custom content and the corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which custom content should be returned. |
| `type` | query | string | ✓ | The type of custom content being requested. See: https://developer.atlassian.com/cloud/confluence/custom-content/ for additional details on custom content. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field.  Note: If the custom content body type is `storage`, the `storage` and `atlas_doc_format` body formats are able to be returned. If the custom content body type is `raw`, only the `raw` body format is able to be returned. |
**Responses:**

- **200**: Returned if the requested custom content is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the space is not found. Returned if the type of custom content is not found. Note, this is distinct from the type being present, but no instances of the type, which would be a 200 with empty results.


### Data Policies
#### `GET /data-policies/metadata`
Get data policy metadata for the workspace
Returns data policy metadata for the workspace.

**[Permissions](#permissions) required:**
Only apps can make this request.
Permission to access the Confluence site ('Can use' global permission).
**Responses:**

- **200**: Returned if the request is successful.
- **400**: Returned if the request is not valid.
- **401**: Returned if the authentication credentials are incorrect or missing.

#### `GET /data-policies/spaces`
Get spaces with data policies
Returns all spaces. The results will be sorted by id ascending. The number of results is limited by the `limit` parameter and
additional results (if available) will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Only apps can make this request.
Permission to access the Confluence site ('Can use' global permission).
Only spaces that the app has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `ids` | query | array |  | Filter the results to spaces based on their IDs. Multiple IDs can be specified as a comma-separated list. |
| `keys` | query | array |  | Filter the results to spaces based on their keys. Multiple keys can be specified as a comma-separated list. |
| `sort` | query | object |  | Used to sort the result by a particular field. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of spaces per result to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested spaces are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.


### Database
#### `POST /databases`
Create database
Creates a database in the space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the corresponding space. Permission to create a database in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `private` | query | boolean |  | The database will be private. Only the user who creates this database will have permission to view and edit one. |
**Responses:**

- **200**: Returned if the database was successfully created.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if:
- The space does not exist
- The user does not have permissions to view the space
- The user does not have the needed permissions to create a database in the provided space
- **413**: Returned if the request is too large in size (over 5 MB).

#### `GET /databases/{id}`
Get database by id
Returns a specific database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the database and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database to be returned |
| `include-collaborators` | query | boolean |  | Includes collaborators on the database. |
| `include-direct-children` | query | boolean |  | Includes direct children of the database, as defined in the `ChildrenResponse` object. |
| `include-operations` | query | boolean |  | Includes operations associated with this database in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this database in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
**Responses:**

- **200**: Returned if the requested database is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested database or the database was not found.

#### `DELETE /databases/{id}`
Delete database
Delete a database by id.

Deleting a database moves the database to the trash, where it can be restored later

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the database and its corresponding space.
Permission to delete databases in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database to be deleted. |
**Responses:**

- **204**: Returned if the database was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided database does not exist
- The user does not have permissions to view the database
- The user does not have the needed permissions to delete a database in the space


### Folder
#### `POST /folders`
Create folder
Creates a folder in the space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the corresponding space. Permission to create a folder in the space.
**Responses:**

- **200**: Returned if the folder was successfully created in the content tree.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if:
- The space does not exist
- The user does not have permissions to view the space
- The user does not have the needed permissions to create a folder in the provided space
- **413**: Returned if the request is too large in size (over 5 MB).

#### `GET /folders/{id}`
Get folder by id
Returns a specific folder.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the folder and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder to be returned. |
| `include-collaborators` | query | boolean |  | Includes collaborators on the folder. |
| `include-direct-children` | query | boolean |  | Includes direct children of the folder, as defined in the `ChildrenResponse` object. |
| `include-operations` | query | boolean |  | Includes operations associated with this folder in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this folder in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
**Responses:**

- **200**: Returned if the requested folder is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested folder or the folder was not found.

#### `DELETE /folders/{id}`
Delete folder
Delete a folder by id.

Deleting a folder moves the folder to the trash, where it can be restored later

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the folder and its corresponding space.
Permission to delete folders in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder to be deleted. |
**Responses:**

- **204**: Returned if the folder was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided folder does not exist
- The user does not have permissions to view the folder
- The user does not have the needed permissions to delete folder in the space


### Like
#### `GET /blogposts/{id}/likes/count`
Get like count for blog post
Returns the count of likes of specific blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which like count should be returned. |
**Responses:**

- **200**: Returned if the requested count is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `GET /blogposts/{id}/likes/users`
Get account IDs of likes for blog post
Returns the account IDs of likes of specific blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which account IDs should be returned. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of account IDs per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested account IDs are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested blog post or the blog post was not found.

#### `GET /pages/{id}/likes/count`
Get like count for page
Returns the count of likes of specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which like count should be returned. |
**Responses:**

- **200**: Returned if the requested count is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /pages/{id}/likes/users`
Get account IDs of likes for page
Returns the account IDs of likes of specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which like count should be returned. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of account IDs per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested account IDs are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested page or the page was not found.

#### `GET /footer-comments/{id}/likes/count`
Get like count for footer comment
Returns the count of likes of specific footer comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page/blogpost and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the footer comment for which like count should be returned. |
**Responses:**

- **200**: Returned if the requested count is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the comment or the comment was not found.

#### `GET /footer-comments/{id}/likes/users`
Get account IDs of likes for footer comment
Returns the account IDs of likes of specific footer comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page/blogpost and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the footer comment for which like count should be returned. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of account IDs per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested account IDs are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the comment or the comment was not found.

#### `GET /inline-comments/{id}/likes/count`
Get like count for inline comment
Returns the count of likes of specific inline comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page/blogpost and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the inline comment for which like count should be returned. |
**Responses:**

- **200**: Returned if the requested count is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the comment or the comment was not found.

#### `GET /inline-comments/{id}/likes/users`
Get account IDs of likes for inline comment
Returns the account IDs of likes of specific inline comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the content of the page/blogpost and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the inline comment for which like count should be returned. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of account IDs per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested account IDs are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the comment or the comment was not found.


### Operation
#### `GET /attachments/{id}/operations`
Get permitted operations for attachment
Returns the permitted operations on specific attachment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the attachment and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | string | ✓ | The ID of the attachment for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested attachment or the attachment was not found.

#### `GET /blogposts/{id}/operations`
Get permitted operations for blog post
Returns the permitted operations on specific blog post.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested blog post or the blog post was not found.

#### `GET /custom-content/{id}/operations`
Get permitted operations for custom content
Returns the permitted operations on specific custom content.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the custom content and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the custom content for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested custom content or the custom content was not found.

#### `GET /pages/{id}/operations`
Get permitted operations for page
Returns the permitted operations on specific page.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the page and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested page or the page was not found.

#### `GET /whiteboards/{id}/operations`
Get permitted operations for a whiteboard
Returns the permitted operations on specific whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the whiteboard and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested whiteboard or the whiteboard was not found.

#### `GET /databases/{id}/operations`
Get permitted operations for a database
Returns the permitted operations on specific database.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the database and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the database for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested database or the database was not found.

#### `GET /embeds/{id}/operations`
Get permitted operations for a Smart Link in the content tree
Returns the permitted operations on specific Smart Link in the content tree.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the Smart Link in the content tree and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the Smart Link in the content tree for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested Smart Link in the content tree or the Smart Link was not found.

#### `GET /folders/{id}/operations`
Get permitted operations for a folder
Returns the permitted operations on specific folder.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the folder and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the folder for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested folder or the folder was not found.

#### `GET /spaces/{id}/operations`
Get permitted operations for space
Returns the permitted operations on specific space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
space or the space was not found.

#### `GET /footer-comments/{id}/operations`
Get permitted operations for footer comment
Returns the permitted operations on specific footer comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the footer comment and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the footer comment for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested footer comment or the footer comment was not found.

#### `GET /inline-comments/{id}/operations`
Get permitted operations for inline comment
Returns the permitted operations on specific inline comment.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the parent content of the inline comment and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the inline comment for which operations should be returned. |
**Responses:**

- **200**: Returned if the requested operations are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
parent content of the requested inline comment or the inline comment was not found.


### Redactions
#### `POST /pages/{id}/redact`
Redact Content in a Confluence Page
Redacts sensitive content in a Confluence page by replacing specified text ranges with redaction markers. 
Each redaction in the response includes a unique UUID for restoration (except code block redactions). 
The response metadata items maintain the same order as the input redaction pointers, and completely 
overlapping redactions are merged into a single redaction with one UUID.

**Note**: This endpoint requires **Atlassian Guard Premium**.


**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the page to redact content from. |
**Responses:**

- **202**: Redaction Accepted. The response contains details about the redactions that were applied.
- **400**: Invalid request. This can be thrown if 
- createdAt field is out of date
- JSON pointers are invalid

#### `POST /blogposts/{id}/redact`
Redact Content in a Confluence Blog Post
Redacts sensitive content in a Confluence blog post by replacing specified text ranges with redaction markers. 
Each redaction in the response includes a unique UUID for restoration (except code block redactions). 
The response metadata items maintain the same order as the input redaction pointers, and completely 
overlapping redactions are merged into a single redaction with one UUID.

**Note**: This endpoint requires **Atlassian Guard Premium**.


**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the blog post to redact content from. |
**Responses:**

- **202**: Redaction Accepted. The response contains details about the redactions that were applied.
- **400**: Invalid request. This can be thrown if 
- createdAt field is out of date
- JSON pointers are invalid


### Smart Link
#### `POST /embeds`
Create Smart Link in the content tree
Creates a Smart Link in the content tree in the space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the corresponding space. Permission to create a Smart Link in the content tree in the space.
**Responses:**

- **200**: Returned if the Smart Link was successfully created in the content tree.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if:
- The space does not exist
- The user does not have permissions to view the space
- The user does not have the needed permissions to create a Smart Link in the content tree in the provided space
- **413**: Returned if the request is too large in size (over 5 MB).

#### `GET /embeds/{id}`
Get Smart Link in the content tree by id
Returns a specific Smart Link in the content tree.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the Smart Link in the content tree and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the Smart Link in the content tree to be returned. |
| `include-collaborators` | query | boolean |  | Includes collaborators on the Smart Link. |
| `include-direct-children` | query | boolean |  | Includes direct children of the Smart Link, as defined in the `ChildrenResponse` object. |
| `include-operations` | query | boolean |  | Includes operations associated with this Smart Link in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this Smart Link in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
**Responses:**

- **200**: Returned if the requested Smart Link in the content tree is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested Smart Link in the content tree or the Smart Link was not found.

#### `DELETE /embeds/{id}`
Delete Smart Link in the content tree
Delete a Smart Link in the content tree by id.

Deleting a Smart Link in the content tree moves the Smart Link to the trash, where it can be restored later

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the Smart Link in the content tree and its corresponding space.
Permission to delete Smart Links in the content tree in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the Smart Link in the content tree to be deleted. |
**Responses:**

- **204**: Returned if the Smart Link in the content tree was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided Smart Link in the content tree does not exist
- The user does not have permissions to view the Smart Link in the content tree
- The user does not have the needed permissions to delete a Smart Link in the content tree in the space


### Space Permissions
#### `GET /spaces/{id}/permissions`
Get space permissions assignments
Returns space permission assignments for a specific space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space to be returned. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of assignments to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested assignments are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested space permission assignments or the space was not found.

#### `GET /space-permissions`
Get available space permissions
Retrieves the available space permissions.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of space permissions to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested space permissions are retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
available space permissions.


### Space Properties
#### `GET /spaces/{space-id}/properties`
Get space properties in space
Returns all properties for the given space. Space properties are a key-value storage associated with a space.
The limit parameter specifies the maximum number of results returned in a single response. Use the `link` response header
to paginate through additional results.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and 'View' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `space-id` | path | integer | ✓ | The ID of the space for which space properties should be returned. |
| `key` | query | string |  | The key of the space property to retrieve. This should be used when a user knows the key of their property, but needs to retrieve the id for use in other methods. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of pages per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested space properties are returned. `results` may be empty if no results were found.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.

#### `POST /spaces/{space-id}/properties`
Create space property in space
Creates a new space property.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and 'Admin' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `space-id` | path | integer | ✓ | The ID of the space for which space properties should be returned. |

**Request Body:**

Schema: `SpacePropertyCreateRequest`

**Responses:**

- **201**: Returned if the space property was created successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.

#### `GET /spaces/{space-id}/properties/{property-id}`
Get space property by id
Retrieve a space property by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and 'View' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `space-id` | path | integer | ✓ | The ID of the space the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be retrieved. |
**Responses:**

- **200**: Returned if the space property was retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.

#### `PUT /spaces/{space-id}/properties/{property-id}`
Update space property by id
Update a space property by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and 'Admin' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `space-id` | path | integer | ✓ | The ID of the space the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be updated. |

**Request Body:**

Schema: `SpacePropertyUpdateRequest`

**Responses:**

- **200**: Returned if the space property was updated successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.

#### `DELETE /spaces/{space-id}/properties/{property-id}`
Delete space property by id
Deletes a space property by its id. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission) and 'Admin' permission for the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `space-id` | path | integer | ✓ | The ID of the space the property belongs to. |
| `property-id` | path | integer | ✓ | The ID of the property to be deleted. |
**Responses:**

- **204**: Returned if the space property was deleted successfully.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
specified space or the space was not found.


### Space Roles
#### `GET /space-roles`
Get available space roles
Retrieves the available space roles.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site; if requesting a certain space's roles, permission to view the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `space-id` | query | string |  | The space ID for which to filter available space roles; if empty, return all available space roles for the tenant. |
| `role-type` | query | string |  | The space role type to filter results by. |
| `principal-id` | query | string |  | The principal ID to filter results by. If specified, a principal-type must also be specified. Paired with a `principal-type` of `ACCESS_CLASS`, valid values include [`anonymous-users`, `jsm-project-admins`, `authenticated-users`, `all-licensed-users`, `all-product-admins`] |
| `principal-type` | query | object |  | The principal type to filter results by. If specified, a principal-id must also be specified. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of space roles to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested space roles are retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
available space roles.

#### `POST /space-roles`
Create a space role
Create a space role.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
User must be an organization or site admin. Connect and Forge app users are not authorized to access this resource.

**Request Body:**

Type: `object`


Key fields:
- `name`*: string - Name of the space role
- `description`*: string - Description for the space role
- `spacePermissions`*: array - The ids of the space permissions associated with the space role. Sample value "r
**Responses:**

- **201**: Returned if the requested space role is created.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not have permission to create space roles.

#### `GET /space-roles/{id}`
Get space role by ID
Retrieves the space role by ID.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space role to retrieve. |
**Responses:**

- **200**: Returned if the requested space role is retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
space role.

#### `PUT /space-roles/{id}`
Update a space role
Update a space role.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
User must be an organization or site admin. Connect and Forge app users are not authorized to access this resource.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | string | ✓ | Id of the space role |

**Request Body:**

Type: `object`


Key fields:
- `name`*: string - Name of the space role
- `description`*: string - Description for the space role
- `spacePermissions`*: array - The ids of the space permissions associated with the space role. Sample value "r
- `anonymousReassignmentRoleId`: string - If space anonymous access is assigned to the role being modified, the Id of a ro
- `guestReassignmentRoleId`: string - If guests are assigned to the role being modified, the Id of a role to migrate t
**Responses:**

- **202**: Returned if the update of the space role was accepted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not have permission to update space roles.

#### `DELETE /space-roles/{id}`
Delete a space role
Delete a space role

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
User must be an organization or site admin. Connect and Forge app users are not authorized to access this resource.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | string | ✓ | Id of the space role |
**Responses:**

- **202**: Returned if the deletion of the space role was accepted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not have permission to delete space roles.

#### `GET /space-role-mode`
Get space role mode
Retrieves the space role mode.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
**Responses:**

- **200**: Returned if the requested space role mode is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if the calling user does not have permission to view the space role mode.

#### `GET /spaces/{id}/role-assignments`
Get space role assignments
Retrieves the space role assignments.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which to retrieve assignments. |
| `role-id` | query | string |  | Filters the returned role assignments to the provided role ID. |
| `role-type` | query | string |  | Filters the returned role assignments to the provided role type. |
| `principal-id` | query | string |  | Filters the returned role assignments to the provided principal id. If specified, a principal-type must also be specified. Paired with a `principal-type` of `ACCESS_CLASS`, valid values include [`anonymous-users`, `jsm-project-admins`, `authenticated-users`, `all-licensed-users`, `all-product-admins`] |
| `principal-type` | query | object |  | Filters the returned role assignments to the provided principal type. If specified, a principal-id must also be specified. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of space roles to return. If more results exist, use the `Link` response header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested space role assignments are retrieved.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
space or the space was not found.

#### `POST /spaces/{id}/role-assignments`
Set space role assignments
Sets space role assignments as specified in the payload.

Available as part of the [Role-Based Access Controls Beta](https://community.atlassian.com/forums/Confluence-articles/Beta-Simplify-space-access-in-Confluence-with-roles/ba-p/3044550). 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to manage roles in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the space for which to retrieve assignments. |
**Responses:**

- **200**: Returned if the requested update to space role assignments succeeds in its entirety.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to set roles in the space, or the space was not found.
- **413**: Returned if the request is too large in size (over 5 MB).


### Task
#### `GET /tasks`
Get tasks
Returns all tasks. The number of results is limited by the `limit` parameter and additional results (if available)
will be available through the `next` URL present in the `Link` response header.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
Only tasks that the user has permission to view will be returned.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
| `include-blank-tasks` | query | boolean |  | Specifies whether to include blank tasks in the response. Defaults to `true`. |
| `status` | query | enum: complete, incomplete |  | Filters on the status of the task. |
| `task-id` | query | array |  | Filters on task ID. Multiple IDs can be specified. |
| `space-id` | query | array |  | Filters on the space ID of the task. Multiple IDs can be specified. |
| `page-id` | query | array |  | Filters on the page ID of the task. Multiple IDs can be specified. Note - page and blog post filters can be used in conjunction. |
| `blogpost-id` | query | array |  | Filters on the blog post ID of the task. Multiple IDs can be specified. Note - page and blog post filters can be used in conjunction. |
| `created-by` | query | array |  | Filters on the Account ID of the user who created this task. Multiple IDs can be specified. |
| `assigned-to` | query | array |  | Filters on the Account ID of the user to whom this task is assigned. Multiple IDs can be specified. |
| `completed-by` | query | array |  | Filters on the Account ID of the user who completed this task. Multiple IDs can be specified. |
| `created-at-from` | query | integer |  | Filters on start of date-time range of task based on creation date (inclusive). Input is epoch time in milliseconds. |
| `created-at-to` | query | integer |  | Filters on end of date-time range of task based on creation date (inclusive). Input is epoch time in milliseconds. |
| `due-at-from` | query | integer |  | Filters on start of date-time range of task based on due date (inclusive). Input is epoch time in milliseconds. |
| `due-at-to` | query | integer |  | Filters on end of date-time range of task based on due date (inclusive). Input is epoch time in milliseconds. |
| `completed-at-from` | query | integer |  | Filters on start of date-time range of task based on completion date (inclusive). Input is epoch time in milliseconds. |
| `completed-at-to` | query | integer |  | Filters on end of date-time range of task based on completion date (inclusive). Input is epoch time in milliseconds. |
| `cursor` | query | string |  | Used for pagination, this opaque cursor will be returned in the `next` URL in the `Link` response header. Use the relative URL in the `Link` header to retrieve the `next` set of results. |
| `limit` | query | integer |  | Maximum number of tasks per result to return. If more results exist, use the `Link` header to retrieve a relative URL that will return the next set of results. |
**Responses:**

- **200**: Returned if the requested tasks are returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.

#### `GET /tasks/{id}`
Get task by id
Returns a specific task. 

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the containing page or blog post and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the task to be returned. If you don't know the task ID, use Get tasks and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
**Responses:**

- **200**: Returned if the requested task is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested task or the task was not found.

#### `PUT /tasks/{id}`
Update task
Update a task by id. This endpoint currently only supports updating task status.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to edit the containing page or blog post and view its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the task to be updated. If you don't know the task ID, use Get tasks and filter the results. |
| `body-format` | query | object |  | The content format types to be returned in the `body` field of the response. If available, the representation will be available under a response field of the same name under the `body` field. |
**Responses:**

- **200**: Returned if the requested task is updated.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if:
- The provided task does not exist
- The user does not have permissions to view the task
- The user does not have the needed permissions to update the containing page or blog post in the corresponding space


### User
#### `POST /users-bulk`
Create bulk user lookup using ids
Returns user details for the ids provided in the request body.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
The user must be able to view user profiles in the Confluence site.
**Responses:**

- **200**: Returned if the user info is returned for the account IDs. `results` may be empty if no account IDs were found.
- **400**: Returned if an invalid request is provided.
- **404**: Returned if the calling user does not have permission to use Confluence or view user profiles.

#### `POST /user/access/check-access-by-email`
Check site access for a list of emails
Returns the list of emails from the input list that do not have access to site.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
**Responses:**

- **200**: Returns object with list of emails without access to site.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to check access for emails on site.
- **503**: Returned if API is disabled on site

#### `POST /user/access/invite-by-email`
Invite a list of emails to the site
Invite a list of emails to the site.

Ignores all invalid emails and no action is taken for the emails that already have access to the site.

<b>NOTE:</b> This API is asynchronous and may take some time to complete.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to access the Confluence site ('Can use' global permission).
**Responses:**

- **200**: Returns object with list of emails without access to site.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to check access for emails on site.
- **503**: Returned if API is disabled on site


### Whiteboard
#### `POST /whiteboards`
Create whiteboard
Creates a whiteboard in the space.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the corresponding space. Permission to create a whiteboard in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `private` | query | boolean |  | The whiteboard will be private. Only the user who creates this whiteboard will have permission to view and edit one. |
**Responses:**

- **200**: Returned if the whiteboard was successfully created.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing from the request.
- **404**: Returned if:
- The space does not exist
- The user does not have permissions to view the space
- The user does not have the needed permissions to create a whiteboard in the provided space
- **413**: Returned if the request is too large in size (over 5 MB).

#### `GET /whiteboards/{id}`
Get whiteboard by id
Returns a specific whiteboard.

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the whiteboard and its corresponding space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard to be returned |
| `include-collaborators` | query | boolean |  | Includes collaborators on the whiteboard. |
| `include-direct-children` | query | boolean |  | Includes direct children of the whiteboard, as defined in the `ChildrenResponse` object. |
| `include-operations` | query | boolean |  | Includes operations associated with this whiteboard in the response, as defined in the `Operation` object. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
| `include-properties` | query | boolean |  | Includes content properties associated with this whiteboard in the response. The number of results will be limited to 50 and sorted in the default sort order. A `meta` and `_links` property will be present to indicate if more results are available and a link to retrieve the rest of the results. |
**Responses:**

- **200**: Returned if the requested whiteboard is returned.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if the calling user does not have permission to view the
requested whiteboard or the whiteboard was not found.

#### `DELETE /whiteboards/{id}`
Delete whiteboard
Delete a whiteboard by id.

Deleting a whiteboard moves the whiteboard to the trash, where it can be restored later

**[Permissions](https://confluence.atlassian.com/x/_AozKw) required**:
Permission to view the whiteboard and its corresponding space.
Permission to delete whiteboards in the space.

**Parameters:**
| Name | In | Type | Required | Description |
|------|-----|------|----------|-------------|
| `id` | path | integer | ✓ | The ID of the whiteboard to be deleted. |
**Responses:**

- **204**: Returned if the whiteboard was successfully deleted.
- **400**: Returned if an invalid request is provided.
- **401**: Returned if the authentication credentials are incorrect or missing
from the request.
- **404**: Returned if:
- The provided whiteboard does not exist
- The user does not have permissions to view the whiteboard
- The user does not have the needed permissions to delete a whiteboard in the space


## Best Practices

1. **Use cursor pagination** for large result sets instead of offset-based
2. **Request only needed fields** using `expand` parameter selectively
3. **Handle rate limits** with exponential backoff
4. **Cache responses** when appropriate
5. **Use version numbers** when updating content to prevent conflicts
6. **Check permissions** before operations to avoid 403 errors
7. **Use space keys** for human-readable space references
8. **Follow HAL links** in `_links` for related resources

## References

- [Official API Documentation](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
- [Authentication Guide](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/#authentication)
- [API Change Log](https://developer.atlassian.com/cloud/confluence/changelog/)
