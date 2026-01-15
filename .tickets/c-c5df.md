---
id: c-c5df
status: closed
deps: []
links: []
created: 2026-01-15T12:48:38Z
type: task
priority: 2
assignee: Sebastian Kaspari
---
# Update CONTRIBUTING.md to link to tk ticket system

CONTRIBUTING.md mentions 'ticket' system but doesn't link to the implementation repository.

## Problem
The contribution document references the ticket/tk system but doesn't provide a link for people who want to learn more or get the tool.

## Tasks
- Find where CONTRIBUTING.md mentions 'ticket' or 'tk'
- Add link to: https://github.com/wedow/ticket
- Explain briefly what tk is (minimal ticket system)
- Make it clear tk is used for task management in this project

## Example text:
"This project uses [tk](https://github.com/wedow/ticket), a minimal ticket system for managing tasks and issues."

## Acceptance Criteria
- CONTRIBUTING.md links to https://github.com/wedow/ticket
- Context explains what tk is
- Link is properly formatted in Markdown

## References
- CONTRIBUTING.md — add link
- https://github.com/wedow/ticket — tk repository

## Notes
- Quick documentation improvement
- Helps contributors understand the tooling


**2026-01-15T12:53:20Z**

Completed: Added tk (https://github.com/wedow/ticket) links and explanations in three places: Ralph introduction section, project structure diagram, and codebase organization list.
