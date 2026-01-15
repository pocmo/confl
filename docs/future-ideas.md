# Future Ideas

**Note:** This document contains speculative ideas for potential future enhancements. These are **not** planned work items. For concrete feature requests or bugs, create tickets using `tk create`.

Many features originally listed here have been implemented. See the CLI help (`confl --help`) and documentation for current capabilities.

## Potential Commands

- `confl page diff <ref> --version 5` — diff between versions
- `confl page move <ref> --parent <ref>` — move page in hierarchy
- `confl page copy <ref> --space NEW` — copy page to another space
- `confl template list` — list page templates
- `confl template apply <name>` — create page from template
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
- Rate limiting / retry with backoff (basic retry exists but could be enhanced)

## Integrations

- Git hook for updating Confluence on commit
- GitHub Action for CI/CD pipelines
- VS Code extension that shells out to `confl`
