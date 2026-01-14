# Agent Guidelines

## Tech Stack

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Typer](https://typer.tiangolo.com/) for CLI
- [Rich](https://rich.readthedocs.io/) for terminal output
- [httpx](https://www.python-httpx.org/) for API requests

## Project Layout

```
confl/
├── src/confl/       # Main package
├── tests/           # Tests
├── docs/            # Documentation
│   └── architecture/  # Architecture decisions
└── pyproject.toml   # Project config
```

## Architecture

- [CLI Design](docs/architecture/cli-design.md)
- [Configuration](docs/architecture/configuration.md)

## API Reference

- [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
