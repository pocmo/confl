# Future Ideas

Potential enhancements for future discovery and implementation.

## Commands

- `confl page history <ref>` — view version history
- `confl page diff <ref> --version 5` — diff between versions
- `confl page restore <ref> --version 3` — restore previous version
- `confl page move <ref> --parent <ref>` — move page in hierarchy
- `confl page copy <ref> --space NEW` — copy page to another space
- `confl template list` — list page templates
- `confl template apply <name>` — create page from template
- `confl label add/remove/list` — manage page labels
- `confl watch <ref>` — watch a page for changes
- `confl export --space KEY` — bulk export to Markdown files

## Output Formats

- `--yaml` output format
- `--html` rendered HTML output
- `--pdf` export (if API supports)

## Features

- Offline cache for frequently accessed pages
- `confl diff local.md remote` — diff local file against page
- `confl sync` — bidirectional sync between local files and Confluence
- Tab completion for space keys and page titles
- `--dry-run` flag for destructive operations
- `--verbose` / `--debug` flags for troubleshooting
- Config profiles for multiple Confluence sites
- Rate limiting / retry with backoff

## Integrations

- Git hook for updating Confluence on commit
- GitHub Action for CI/CD pipelines
- VS Code extension that shells out to `confl`
