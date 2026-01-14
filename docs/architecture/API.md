# Confluence Cloud REST API v2 Overview

This document provides a comprehensive overview of the Confluence Cloud REST API v2 endpoints, extracted from the official API documentation.

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

## Resource Categories

### Admin Key

Manage admin keys for privileged operations (Premium/Enterprise only):

- `GET /admin-key` - Check if admin key is enabled
- `POST /admin-key` - Enable/renew admin key
- `DELETE /admin-key` - Disable admin key

### Attachments

Manage file attachments on content:

- `GET /attachments` - List all attachments
- `GET /attachments/{id}` - Get attachment by ID
- `DELETE /attachments/{id}` - Delete attachment
- `GET /pages/{id}/attachments` - List attachments on a page
- `GET /blogposts/{id}/attachments` - List attachments on a blog post
- `GET /custom-content/{id}/attachments` - List attachments on custom content
- `GET /labels/{id}/attachments` - List attachments by label

### Blog Posts

Create and manage blog posts:

- `GET /blogposts` - List blog posts
- `POST /blogposts` - Create blog post
- `GET /blogposts/{id}` - Get blog post by ID
- `PUT /blogposts/{id}` - Update blog post
- `DELETE /blogposts/{id}` - Delete blog post
- `GET /spaces/{id}/blogposts` - List blog posts in a space
- `GET /labels/{id}/blogposts` - List blog posts with a label

### Pages

Core page operations:

- `GET /pages` - List pages
- `POST /pages` - Create page
- `GET /pages/{id}` - Get page by ID
- `PUT /pages/{id}` - Update page
- `DELETE /pages/{id}` - Delete page
- `GET /spaces/{id}/pages` - List pages in a space
- `GET /labels/{id}/pages` - List pages with a label
- `GET /pages/{id}/ancestors` - Get page ancestors
- `GET /pages/{id}/children` - Get page children (direct children)
- `GET /pages/{id}/descendants` - Get page descendants (all levels)

### Spaces

Manage Confluence spaces:

- `GET /spaces` - List spaces
- `POST /spaces` - Create space
- `GET /spaces/{id}` - Get space by ID
- `PUT /spaces/{id}` - Update space
- `DELETE /spaces/{id}` - Delete space
- `GET /spaces/{key}` - Get space by key

### Labels

Tag content with labels:

- `GET /labels` - List labels
- `GET /pages/{id}/labels` - Get labels for a page
- `POST /pages/{id}/labels` - Add labels to a page
- `DELETE /pages/{id}/labels/{labelId}` - Remove label from page
- Similar endpoints for blogposts, attachments, custom content

### Comments

Page and blog post comments:

- `GET /pages/{id}/comments` - List comments on a page
- `GET /blogposts/{id}/comments` - List comments on a blog post
- `GET /comments/{id}` - Get comment by ID
- `POST /pages/{id}/comments` - Create comment on page
- `PUT /comments/{id}` - Update comment
- `DELETE /comments/{id}` - Delete comment

### Versions

Content version history:

- `GET /pages/{id}/versions` - List page versions
- `GET /pages/{id}/versions/{versionNumber}` - Get specific version
- `GET /blogposts/{id}/versions` - List blog post versions

### Custom Content

App-defined content types:

- `GET /custom-content` - List custom content
- `POST /custom-content` - Create custom content
- `GET /custom-content/{id}` - Get custom content by ID
- `PUT /custom-content/{id}` - Update custom content
- `DELETE /custom-content/{id}` - Delete custom content

### Whiteboards

Manage whiteboard content:

- `GET /whiteboards` - List whiteboards
- `POST /whiteboards` - Create whiteboard
- `GET /whiteboards/{id}` - Get whiteboard by ID
- `PUT /whiteboards/{id}` - Update whiteboard
- `DELETE /whiteboards/{id}` - Delete whiteboard

### Databases (Confluence Database)

Manage Confluence database content:

- `GET /databases` - List databases
- `POST /databases` - Create database
- `GET /databases/{id}` - Get database by ID
- `PUT /databases/{id}` - Update database
- `DELETE /databases/{id}` - Delete database

### Smart Links (Embeds)

Embedded content and smart links:

- `GET /embeds` - List embedded content
- `GET /embeds/{id}` - Get embed by ID

### Folders

Organize content in folders:

- `GET /folders` - List folders
- `POST /folders` - Create folder
- `GET /folders/{id}` - Get folder by ID
- `PUT /folders/{id}` - Update folder
- `DELETE /folders/{id}` - Delete folder

### App Properties

Store app-specific data (Forge apps):

- `GET /app/properties` - List app properties
- `GET /app/properties/{key}` - Get property by key
- `PUT /app/properties/{key}` - Set property value
- `DELETE /app/properties/{key}` - Delete property

### Content Properties

Custom properties on content:

- `GET /pages/{id}/properties` - List page properties
- `GET /pages/{id}/properties/{key}` - Get property by key
- `POST /pages/{id}/properties` - Create property
- `PUT /pages/{id}/properties/{key}` - Update property
- `DELETE /pages/{id}/properties/{key}` - Delete property
- Similar endpoints for blogposts, custom-content

### Classification

Data classification levels:

- `GET /classification/levels` - List classification levels
- `GET /spaces/{id}/classification` - Get space classification
- `PUT /spaces/{id}/classification` - Set space classification
- `GET /pages/{id}/classification` - Get page classification
- `PUT /pages/{id}/classification` - Set page classification

### Ancestors

Get ancestor hierarchy:

- `GET /pages/{id}/ancestors` - Get page ancestors
- `GET /blogposts/{id}/ancestors` - Get blog post ancestors
- `GET /whiteboards/{id}/ancestors` - Get whiteboard ancestors
- `GET /databases/{id}/ancestors` - Get database ancestors
- `GET /embeds/{id}/ancestors` - Get embed ancestors
- `GET /folders/{id}/ancestors` - Get folder ancestors

### Children

Get direct children:

- `GET /pages/{id}/children` - Get page children
- Similar endpoints for other content types

### Descendants

Get all descendants (recursive):

- `GET /pages/{id}/descendants` - Get all page descendants
- Similar endpoints for other content types

### Footer Comments

Page footer comments:

- `GET /pages/{id}/footer-comments` - Get footer comments
- `POST /pages/{id}/footer-comments` - Create footer comment

### Inline Comments

Inline/highlight comments on content:

- `GET /pages/{id}/inline-comments` - Get inline comments
- `POST /pages/{id}/inline-comments` - Create inline comment

### Operations

Batch operations:

- `GET /operations` - List recent operations
- `GET /operations/{id}` - Get operation status

### Tasks

Task management:

- `GET /tasks` - List tasks
- `GET /tasks/{id}` - Get task by ID
- `PUT /tasks/{id}` - Update task

### User Management

User information:

- `GET /users` - Search users
- `GET /users/{accountId}` - Get user by account ID
- `GET /user/current` - Get current user

### Group Management

User groups:

- `GET /groups` - List groups
- `GET /groups/{groupId}` - Get group by ID
- `GET /groups/{groupId}/members` - List group members

### Permissions

Space and content permissions:

- `GET /spaces/{id}/permissions` - Get space permissions
- `POST /spaces/{id}/permissions` - Add space permission
- `DELETE /spaces/{id}/permissions/{id}` - Remove space permission

### Watchers

Content watchers:

- `GET /pages/{id}/watchers` - Get page watchers
- Similar endpoints for other content types

## Content Body Formats

Confluence supports multiple body formats:

### Storage Format

The canonical format for content storage (XHTML-based):
```xml
<p>Hello <strong>world</strong></p>
```

### View Format

Rendered HTML for display:
```html
<div class="content">Hello <strong>world</strong></div>
```

### Editor Format

Format for the Confluence editor.

### Export View

HTML suitable for export/PDF generation.

### Anonymous Export View

Export view without user-specific content.

## Common Fields

### Content Object

Most content endpoints return objects with these fields:

- `id` - Unique identifier
- `type` - Content type (page, blogpost, etc.)
- `status` - current, archived, trashed, deleted
- `title` - Content title
- `spaceId` - Parent space ID
- `parentId` - Parent content ID (optional)
- `authorId` - Creator account ID
- `ownerId` - Owner account ID
- `createdAt` - Creation timestamp (ISO 8601)
- `version` - Version information
  - `number` - Version number
  - `authorId` - Who made this version
  - `message` - Version message
  - `createdAt` - Version timestamp
- `body` - Content body (storage, view, etc.)
- `_links` - HAL links to related resources

### Space Object

- `id` - Space ID
- `key` - Space key (unique short identifier)
- `name` - Space name
- `type` - global, personal
- `status` - current, archived
- `authorId` - Creator
- `createdAt` - Creation timestamp
- `homepageId` - Homepage page ID
- `description` - Space description

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
