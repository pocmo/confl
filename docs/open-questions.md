# Open Questions

Design questions to resolve in future sessions.

## Search

- Should `confl search` use Confluence's CQL (Confluence Query Language) or simple text search?
- What fields to display in search results?
- How to handle pagination in search results?

## Space Commands

- What actions beyond `list` and `get`? Create/delete spaces?
- Should `space list` show all spaces or filter by permissions?

## Pagination

- How to expose pagination in `list` commands?
- Options: `--limit`, `--cursor`, automatic fetching, or interactive paging?

## Page Lookup

- Support `--title "Page Name" --space KEY` for fuzzy lookup?
- How to handle duplicate titles within a space?

## Attachments

- Upload from local file or URL?
- How to reference which page to attach to?

## Comments

- Inline comments vs page-level comments?
- Threading support?

## Content Conversion

- Build our own Markdown ↔ storage format converter or use existing library?
- How to handle Confluence-specific macros that have no Markdown equivalent?
