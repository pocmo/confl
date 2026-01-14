# Design Principles

Guidelines for making design decisions in `confl`.

## Primary Audience

1. AI agents
2. Scripts and CI
3. Humans in terminals

Design for automation first, but make it pleasant for humans too.

## CLI Philosophy

### Follow established patterns

Look to well-designed CLIs for inspiration:
- `gh` (GitHub CLI) — excellent auth flow, URL handling, output formatting
- `kubectl` — entity-first structure, consistent flags
- `git` — composable commands, stdin/stdout piping

When in doubt, do what `gh` does.

### Non-interactive by default

- No prompts — all input via arguments, flags, or stdin
- Commands should be scriptable and pipeable
- If interactivity is needed, make it opt-in (e.g., `--interactive`)

### Human-friendly output, machine-readable available

- Default: Rich-formatted output for terminal readability
- `--json`: Structured output for parsing
- Always output to appropriate streams (stdout for data, stderr for errors/progress)

### Simple first, extend later

- Start with the minimum viable feature set
- Use simple exit codes (0/1/2) before adding granular ones
- Avoid premature abstraction — add complexity when there's a clear need

### Predictable behavior

- Consistent flag names across commands (`--space`, `--json`, `--raw`)
- Consistent exit codes
- No surprises — commands do what they say

### Flexible input

- Support multiple ways to provide content: `--body`, `--body-file`, stdin
- Accept both IDs and URLs where possible
- Environment variables override config files (for CI flexibility)

## When Adding Features

Ask:
1. Does an agent need this? → Make it scriptable
2. Does a human need this? → Make it readable
3. Can we follow `gh` or another established CLI? → Do that
4. Is this the simplest solution? → If not, simplify
