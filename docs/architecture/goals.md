# Goals

## Primary Audience

1. **AI agents** — CLI tools are easier for agents to use than MCP tools
2. **Scripting and CI** — automation pipelines that interact with Confluence
3. **Humans** — developers who want to read/update Confluence without leaving the terminal

## Core Capabilities

- **Read pages** — fetch and display Confluence content as rendered Markdown
- **Edit pages** — update page content from the command line
- **Scriptable** — non-interactive by default, designed for automation
- **Human-friendly output** — rich terminal formatting by default, with `--json` for machine parsing

## Design Principles

- Non-interactive by default — no prompts, all input via arguments/options/stdin
- Predictable output — consistent formats for parsing
- Clear exit codes — success/failure easily detectable by scripts and agents
