---
id: c-6f7c
status: open
deps: []
links: []
created: 2026-01-14T20:47:29Z
type: task
priority: 1
assignee: Sebastian Kaspari
---
# Document Atlassian Document Format (ADF) specification

Research and document the Atlassian Document Format (ADF) used by Confluence in comprehensive detail.

## Tasks
- Research ADF specification from Atlassian documentation
- Fetch all relevant information about ADF structure and schema
- Document in docs/architecture/atlassian-document-format.md with:
  - Overview of ADF (what it is, why Confluence uses it)
  - JSON structure and schema
  - Node types (paragraph, heading, list, table, code block, etc.)
  - Mark types (bold, italic, link, etc.)
  - Attributes and properties
  - Examples of common content types in ADF format
  - Comparison with storage format (XHTML)
  - When ADF is used vs storage format
- Include practical examples for each major node type
- Document any limitations or edge cases

## Acceptance Criteria
- docs/architecture/atlassian-document-format.md exists
- Document is comprehensive and detailed
- Includes structure, node types, marks, and examples
- Helps developers understand how to work with ADF
- Information is accurate and sourced from official docs

## References
- https://developer.atlassian.com/cloud/confluence/apis/document/structure/ — ADF structure docs
- https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/ — ADF spec (shared across products)
- docs/architecture/content-formats.md — format requirements
- docs/architecture/API.md — API response formats

## Notes
- ADF is JSON-based, different from storage format (XHTML)
- Used by modern Confluence editors
- May be easier to work with than storage format for rendering
- This will inform our rendering strategy decisions

