# confl

An unofficial command-line interface for Atlassian Confluence Cloud.

## What is this?

`confl` is a CLI tool for reading and editing Confluence pages directly from your terminal. It's designed to be scriptable and agent-friendly—no interactive editors by default, just straightforward commands that can be chained and automated.

## Authentication

- **API Token** — for CI/automation (via environment variables or config file)
- **OAuth** — browser-based login for interactive use

## Configuration

Config lives in `~/.config/confl/`. Environment variables (`CONFL_*`) can override config file settings.

## Installation

```
pipx install git+https://github.com/pocmo/confl.git
```
