# Contributing to confl

## 🤖 Developed by Ralph

This project is **completely vibe coded by Ralph**, an autonomous loop agent. Ralph works in iterations: it reads tickets from our issue tracker ([`tk`](.tickets/)), implements one feature at a time, runs tests, commits changes, and moves to the next ticket. The entire codebase you see here was written autonomously by AI agents following architecture docs and best practices—no human wrote a single line of the implementation code.

Want to understand how this works? Check out the [`.ralph/`](.ralph/) directory for the agent implementation and handoff logs, or read [**The Year of the Ralph Loop Agent**](https://dev.to/alexandergekov/2026-the-year-of-the-ralph-loop-agent-1gkj) for a deep dive into this development approach.

**Human contributions are welcome!** While Ralph does the day-to-day development, we're happy to accept PRs, bug reports, and feature requests. Ralph will review and integrate them in future iterations.

---

Thank you for your interest in contributing to `confl`! This guide will help you get started with development.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/confl.git
cd confl

# Install dependencies with uv
uv sync

# Verify installation
uv run confl --help

# Run tests
uv run pytest
```

## Development Setup

### Prerequisites

- **Python 3.11+** — required for type hints and modern syntax
- **uv** — fast Python package installer and resolver ([installation guide](https://docs.astral.sh/uv/))

### Initial Setup

1. **Clone and install dependencies:**
   ```bash
   git clone https://github.com/your-org/confl.git
   cd confl
   uv sync
   ```

2. **Configure authentication:**
   ```bash
   uv run confl auth login
   ```
   Follow the prompts to set up your Confluence credentials.

3. **Verify everything works:**
   ```bash
   uv run confl --help
   uv run pytest
   ```

## Project Structure

```
confl/
├── src/confl/       # Main package - CLI, API client, commands, formatters
├── tests/           # Test suite (mirrors src/ structure)
├── docs/            # User documentation and architecture decisions
│   └── architecture/  # Architecture decision records and design docs
├── .ralph/          # Ralph agent loop implementation and handoff logs
├── .tickets/        # Ticket system (tk) - task tracking
└── pyproject.toml   # Project configuration and dependencies
```

The codebase is organized for clarity:
- **src/confl/** contains all application code: CLI entry point, API client, command modules, and output formatters
- **tests/** mirrors the src/ structure for easy navigation
- **docs/** includes both user-facing guides and architecture documentation
- **.ralph/** and **.tickets/** support autonomous development workflows

## Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_page.py

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/test_page.py::test_create_page
```

Tests use `pytest` with `pytest-httpx` for mocking HTTP requests. Coverage reports are generated automatically.

## Code Style and Quality

We use automated tools to maintain code quality. **All checks must pass before committing.**

### Required Checks

```bash
# 1. Format code (auto-fix)
uv run ruff format .

# 2. Lint code (auto-fix)
uv run ruff check --fix .

# 3. Verify formatting and linting
uv run ruff format --check .
uv run ruff check .

# 4. Type check
uv run mypy src/

# 5. Run tests
uv run pytest
```

### Pre-commit Workflow

Before committing, run this sequence:

```bash
uv run ruff format . && \
uv run ruff check --fix . && \
uv run ruff format --check . && \
uv run ruff check . && \
uv run mypy src/ && \
uv run pytest
```

If all checks pass, you're ready to commit!

### Code Style Guidelines

- **Line length:** 100 characters (configured in `pyproject.toml`)
- **Type hints:** Required for all function signatures (`mypy` enforces this)
- **Imports:** Sorted automatically by `ruff` (isort)
- **Docstrings:** Use for public functions, keep them concise
- **Comments:** Only when needed for clarity; code should be self-documenting

## Adding a New Command

Commands are organized by entity type (page, space, attachment, etc.). Follow these steps:

### 1. Choose Command Structure

**Option A: Command Group** (multiple related commands)
- Best for entities with multiple operations (list, get, create, update, delete)
- Example: `page`, `space`, `label`

**Option B: Single Command** (one operation)
- Best for standalone operations
- Example: `search`

### 2. Create Command Module

For a command group, create `src/confl/commands/myentity.py`:

```python
"""My entity commands."""

import json
import sys

import typer
from rich.console import Console

from confl.client import ApiError, ConfluenceClient, get_client
from confl.formatters import format_json

app = typer.Typer(help="Manage my entity")
console = Console()
err_console = Console(stderr=True)


@app.command("list")
def list_entities(
    limit: int = typer.Option(25, "--limit", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List entities.
    
    Examples:
        confl myentity list
        confl myentity list --limit 50 --json
    """
    try:
        client = get_client()
        results = client.get("/myentity", params={"limit": limit})
        
        if json_output:
            format_json(results)
        else:
            # Rich formatted output
            for item in results.get("results", []):
                console.print(f"[bold]{item['name']}[/bold] - {item['id']}")
    except ApiError as e:
        err_console.print(f"[red]Error:[/red] {e}", style="bold")
        sys.exit(1)


@app.command("get")
def get_entity(
    entity_id: str = typer.Argument(..., help="Entity ID"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Get an entity by ID."""
    # Implementation...
    pass
```

### 3. Register Command in CLI

Edit `src/confl/cli.py`:

```python
from confl.commands import myentity

# For command group:
app.add_typer(myentity.app, name="myentity")

# For single command:
app.command(name="mycommand")(myentity.my_command)
```

### 4. Add Tests

Create `tests/test_myentity.py`:

```python
"""Tests for myentity commands."""

import pytest
from typer.testing import CliRunner

from confl.cli import app

runner = CliRunner()


def test_list_entities(httpx_mock):
    """Test listing entities."""
    httpx_mock.add_response(
        url="https://test.atlassian.net/wiki/api/v2/myentity?limit=25",
        json={
            "results": [
                {"id": "123", "name": "Test Entity"}
            ]
        }
    )
    
    result = runner.invoke(app, ["myentity", "list"])
    assert result.exit_code == 0
    assert "Test Entity" in result.stdout
```

### 5. Update Documentation

Add command documentation to `docs/commands.md`:

```markdown
### myentity

Manage my entity.

#### list

List entities.

\`\`\`bash
confl myentity list
confl myentity list --limit 50 --json
\`\`\`
```

### 6. Follow Design Principles

Read [`docs/architecture/design-principles.md`](docs/architecture/design-principles.md) for guidance:

- **Non-interactive by default** — no prompts, use args/flags
- **Machine-readable output** — support `--json` flag
- **Consistent flags** — use `--json`, `--limit`, etc.
- **Flexible input** — accept IDs, URLs, stdin where appropriate
- **Follow `gh` patterns** — when in doubt, do what GitHub CLI does

## Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes:**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Run all checks:**
   ```bash
   uv run ruff format .
   uv run ruff check --fix .
   uv run mypy src/
   uv run pytest
   ```

4. **Commit with clear messages:**
   ```bash
   git add .
   git commit -m "feat(myentity): add list command"
   ```
   
   Commit message format: `<type>(<scope>): <description>`
   - Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`
   - Scope: command or module name
   - Description: imperative mood, lowercase

5. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   ```
   Then create a pull request on GitHub.

6. **PR review:**
   - CI checks must pass (tests, linting, type checking)
   - Code review feedback will be provided
   - Make requested changes and push updates

## Development Tips

### Testing with Real API

For manual testing against real Confluence:

```bash
# Test with your configured instance
uv run confl page list --space TEST

# Use different profile
uv run confl --profile dev page list --space TEST

# Enable debug mode to see API requests
uv run confl --debug page get 123456
```

### Working with the API Client

The `ConfluenceClient` in `src/confl/client.py` handles all API interactions:

```python
from confl.client import get_client

client = get_client()

# GET request
result = client.get("/pages/123456")

# POST request
result = client.post("/pages", json={"title": "New Page", ...})

# Error handling
from confl.client import ApiError
try:
    client.get("/invalid")
except ApiError as e:
    print(f"API error: {e}")
```

### Debugging

Use `--debug` flag to see HTTP requests and responses:

```bash
uv run confl --debug page get 123456
```

Enable logging in your code:

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Running Locally

Install in development mode to test as you code:

```bash
uv sync
uv run confl --help
```

Changes to Python files are reflected immediately (no reinstall needed).

## Documentation

- **User documentation:** `docs/` — guides and command reference
- **Architecture documentation:** `docs/architecture/` — design decisions and principles
- **README:** High-level overview and quick start
- **Code docstrings:** Keep them concise and accurate

When adding features, update relevant documentation:
- New commands → `docs/commands.md`
- Changed behavior → Update existing docs
- Design decisions → Add ADR in `docs/architecture/`

## Getting Help

- **Architecture questions:** Read `docs/architecture/design-principles.md`
- **API reference:** [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/intro/)
- **Issues:** Check existing GitHub issues or create a new one
- **Questions:** Open a discussion on GitHub

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to confl!** 🎉
