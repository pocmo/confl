# CLI UX Improvements

Analysis of CLI user experience best practices and specific improvements for confl.

## Executive Summary

Based on research of CLI best practices (clig.dev, 12-factor CLI apps) and analysis of well-designed CLIs (gh, kubectl, git, docker), this document identifies UX improvements for confl. The CLI already follows many best practices (entity-first structure, non-interactive by default, multiple output formats, helpful error messages), but there are opportunities to enhance usability for both humans and automation.

## Current State: What's Working Well

### ✅ Strong Foundations
- **Entity-first command structure** (`confl page get`, `confl space list`) — clear and consistent
- **Multiple output formats** (`--json`, `--markdown`, `--raw`, `--plain`) — excellent for both humans and scripts
- **Non-interactive by default** — scriptable and pipeable
- **Flexible input** — accepts IDs, URLs, files, stdin
- **Smart typo handling** — "Did you mean 'page'?" suggestions
- **Consistent error handling** — errors to stderr, data to stdout
- **Rich terminal output** — formatted tables, colored messages
- **Good help text** — includes examples in command help
- **Shell completion** — available via `--install-completion`

### ✅ Design Principles Alignment
- Primary audience (AI agents, scripts, humans) is clearly defined
- Follows gh CLI patterns for auth and output
- Predictable behavior with consistent flags
- Simple first, extend later philosophy

## Research: Best Practices from Leading CLIs

### GitHub CLI (gh)
- **Progress indicators** for long operations (cloning, downloading)
- **Interactive flags** for optional interactivity (`gh pr create --web`)
- **Smart defaults** (detects repo from git remote)
- **Confirmation prompts** for destructive actions with `--yes` override
- **Color coding** consistent throughout (green=success, red=error, yellow=warning)
- **Helpful error messages** with suggested fixes

### kubectl
- **Short aliases** for common commands (`k get` → `kubectl get`)
- **Resource abbreviations** (`po` → `pods`, `svc` → `services`)
- **Dry-run mode** (`--dry-run=client|server`)
- **Field selectors** for filtering without complex queries
- **Explain command** for documentation (`kubectl explain pod.spec`)

### git
- **Command groups** in help (porcelain vs. plumbing)
- **Verbose flag levels** (`-v`, `-vv`, `-vvv`)
- **Pager integration** for long output (optional)
- **Shell prompt integration** (branch status)

### docker
- **Progress bars** for pulls/pushes
- **Human-readable sizes** (1.2 GB, 45 MB)
- **Relative timestamps** ("2 hours ago", "3 days ago")
- **Table formatting** with aligned columns

## Identified Improvements

### Priority: HIGH (High Impact, Moderate Effort)

#### H1: Progress Indicators for Long Operations
**User Benefit:** Users know the command is working, not hung
**Use Cases:**
- Uploading large attachments
- Downloading large attachments
- Creating pages with complex content
- Bulk operations

**Implementation:**
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
    task = progress.add_task("Uploading attachment...", total=None)
    result = confluence.upload_attachment(...)
```

**Complexity:** Low
**Examples:** gh, docker, npm

#### H2: Confirmation Prompts for Destructive Actions
**User Benefit:** Prevents accidental data loss
**Use Cases:**
- `confl page delete`
- `confl space delete`
- `confl blogpost delete`
- `confl attachment delete`

**Implementation:**
```python
# Add --yes/-y flag to skip confirmation
if not yes_flag and sys.stdin.isatty():
    if not typer.confirm(f"Delete page {page_id}?"):
        raise typer.Abort()
```

**Complexity:** Low
**Trade-off:** Adds interactivity, but gated by `isatty()` check and `--yes` flag
**Examples:** gh, docker, kubectl

#### H3: Better Error Messages with Suggestions
**User Benefit:** Users can fix errors without reading docs
**Use Cases:**
- Missing configuration → suggest `confl auth login`
- Invalid page ID → explain expected format
- Rate limiting → suggest waiting or increasing timeout
- 404 errors → suggest checking permissions or page existence

**Current:**
```
Error: Invalid page reference: abc
```

**Improved:**
```
Error: Invalid page reference: 'abc'

Page references must be either:
  • A numeric page ID (e.g., 12345678)
  • A full Confluence page URL

Examples:
  confl page get 12345678
  confl page get "https://company.atlassian.net/wiki/spaces/DEV/pages/12345678"
```

**Complexity:** Moderate (requires enhancing error messages throughout)
**Examples:** gh, cargo, rustc

#### H4: Human-Readable Sizes and Timestamps
**User Benefit:** Easier to scan and understand output
**Use Cases:**
- Attachment sizes (1.2 MB instead of 1234567 bytes)
- Relative dates ("2 hours ago" instead of ISO timestamp)
- Duration formatting (1m 30s instead of 90.5 seconds)

**Implementation:**
```python
from rich.filesize import decimal as format_size
from rich.console import Console

# Sizes
size_str = format_size(attachment_size)  # "1.2 MB"

# Relative times (add to dependencies)
from dateutil.relativedelta import relativedelta
```

**Complexity:** Low
**Examples:** docker, gh, ls

#### H5: Dry-Run Mode
**User Benefit:** Test commands without making changes
**Use Cases:**
- Testing page updates before committing
- Validating API permissions
- CI pipeline testing
- Learning/experimentation

**Implementation:**
```python
# Add --dry-run flag to mutating commands
if dry_run:
    console.print("[yellow]DRY RUN:[/yellow] Would create page with title: {title}")
    console.print(f"  Space: {space}")
    console.print(f"  Parent: {parent or 'none'}")
    return
```

**Complexity:** Low-Moderate
**Examples:** kubectl, ansible, rsync

### Priority: MEDIUM (Good Impact, Moderate Effort)

#### M1: Verbose/Debug Modes
**User Benefit:** Troubleshooting and debugging
**Use Cases:**
- Debugging API issues
- Seeing HTTP requests/responses
- Troubleshooting auth problems
- CI debugging

**Implementation:**
```python
# Add global --verbose/-v and --debug flags
# --verbose: Show operation details
# --debug: Show HTTP requests, full tracebacks

if debug:
    httpx_client = httpx.Client(..., event_hooks={"request": [log_request], "response": [log_response]})
```

**Complexity:** Moderate
**Examples:** curl, git, ansible

#### M2: Improved Table Formatting
**User Benefit:** Easier to scan lists
**Current State:** Already uses Rich tables, but could be enhanced
**Improvements:**
- Truncate long titles with ellipsis
- Add color coding (status indicators)
- Sort options (by date, title, etc.)
- Pagination for very long lists

**Complexity:** Low-Moderate
**Examples:** kubectl, docker

#### M3: Search Filtering Shortcuts
**User Benefit:** Simpler search syntax for common queries
**Use Cases:**
- Find pages in space without CQL
- Find pages by label without CQL
- Find attachments by type

**Current:**
```bash
confl search "type=page AND space=DEV AND label=draft"
```

**Improved:**
```bash
confl search --type page --space DEV --label draft
# Generates CQL internally
```

**Complexity:** Moderate
**Examples:** gh (label filters), kubectl (field selectors)

#### M4: Config Profiles/Environments
**User Benefit:** Switch between multiple Confluence instances
**Use Cases:**
- Multiple work environments (dev, staging, prod)
- Multiple clients/organizations
- Personal vs. work instances

**Implementation:**
```bash
confl auth login --profile prod
confl auth login --profile staging
confl page get 123 --profile prod
# Or: export CONFL_PROFILE=prod
```

**Complexity:** Moderate
**Examples:** aws-cli, gcloud, kubectl

#### M5: Command Aliases
**User Benefit:** Less typing for power users
**Use Cases:**
- `confl p get` → `confl page get`
- `confl s list` → `confl space list`

**Trade-off:** May reduce clarity for new users
**Implementation:** Typer supports command aliases natively
**Complexity:** Low
**Examples:** kubectl, git

### Priority: LOW (Nice to Have)

#### L1: Shell Prompt Integration
**User Benefit:** Show current space/profile in shell prompt
**Complexity:** High (requires shell-specific plugins)
**Examples:** git (branch), kubectl (context)
**Note:** Lower priority as this is more for interactive use

#### L2: Man Pages
**User Benefit:** Standard Unix documentation
**Complexity:** Moderate
**Trade-off:** `--help` is already comprehensive
**Examples:** git, docker

#### L3: Pager Support for Long Output
**User Benefit:** Don't overwhelm terminal with long output
**Trade-off:** Complicates piping and scripting
**Implementation:** Use `less` or `more` only when:
- stdout is a TTY
- output exceeds terminal height
- user hasn't disabled it

**Complexity:** Low
**Examples:** git log, kubectl get

#### L4: Watch Mode
**User Benefit:** Monitor pages/spaces for changes
**Use Cases:**
- Wait for page updates
- Monitor CI/CD pipeline status pages

**Implementation:**
```bash
confl page get 123 --watch  # Re-fetch every N seconds
```

**Complexity:** Moderate
**Examples:** kubectl get --watch

#### L5: Inline Examples in Help
**Current State:** Some commands have examples
**Improvement:** Ensure ALL commands have 2-3 examples
**Complexity:** Low (documentation)

#### L6: ASCII Art / Branding
**User Benefit:** Memorable, polished feel
**Trade-off:** May annoy some users, complicates output parsing
**Priority:** Very low
**Note:** Could be opt-in with `--version --verbose`

## Implementation Priorities

### Phase 1: Quick Wins (1-2 days)
- H2: Confirmation prompts for delete commands
- H4: Human-readable sizes and timestamps
- L5: Complete inline examples in all help text
- H5: Dry-run mode for create/update/delete commands

### Phase 2: Core Improvements (3-5 days)
- H3: Enhanced error messages with suggestions
- H1: Progress indicators for long operations
- M1: Verbose/debug modes
- M2: Improved table formatting

### Phase 3: Advanced Features (1 week)
- M3: Search filtering shortcuts
- M4: Config profiles/environments
- M5: Command aliases

### Phase 4: Polish (as needed)
- L3: Pager support
- L4: Watch mode
- L1: Shell prompt integration

## Alignment with Design Principles

All improvements maintain core principles:

### ✅ Non-interactive by default
- Confirmation prompts only when stdin is a TTY
- All prompts skippable with `--yes` flag
- Dry-run doesn't require interaction

### ✅ Scriptable and pipeable
- Progress indicators only when stdout is a TTY
- All features work in non-interactive environments
- JSON output always machine-readable

### ✅ Human-friendly, machine-readable available
- Better defaults for humans
- `--json` still produces consistent output
- No breaking changes to output formats

### ✅ Simple first, extend later
- All improvements are additive
- No removal of existing functionality
- Optional flags don't complicate basic usage

## Rejected Ideas

### ❌ Interactive Wizards
**Reason:** Conflicts with "non-interactive by default" principle
**Alternative:** Keep existing explicit flags/arguments

### ❌ Built-in Editor Integration
**Reason:** Adds complexity, Unix philosophy says use $EDITOR
**Alternative:** Document how to use with editors

### ❌ Graphical Output (Charts, Graphs)
**Reason:** Terminal is text-based, use web UI for graphics
**Alternative:** Export data for visualization tools

### ❌ Plugin System
**Reason:** Premature, adds complexity before core features are solid
**Future:** Revisit when there's clear demand

### ❌ Built-in Macros/Scripting
**Reason:** Shell scripts already provide this
**Alternative:** Document common script patterns

## Success Metrics

How to measure success of improvements:

1. **User Feedback**
   - Fewer "how do I..." questions
   - Positive mentions of specific features
   - Reduced error-related issues

2. **Error Recovery**
   - Users can fix errors without external docs
   - Reduced auth-related confusion
   - Fewer "command not found" issues

3. **Adoption**
   - Increased usage of `--json` for automation
   - Use of dry-run in CI/CD
   - Profile switching for multi-environment users

4. **Performance Perception**
   - Progress indicators reduce "is it working?" questions
   - Faster perceived operations with feedback

## References

- [Command Line Interface Guidelines](https://clig.dev/)
- [12 Factor CLI Apps](https://medium.com/@jdxcode/12-factor-cli-apps-dd3c227a0e46)
- [Rich Progress Documentation](https://rich.readthedocs.io/en/stable/progress.html)
- [Typer Documentation](https://typer.tiangolo.com/)
- [GitHub CLI (gh)](https://cli.github.com/)
- docs/architecture/design-principles.md
- docs/architecture/cli-design.md

## Next Steps

1. Review this document with team/users
2. Create implementation tickets for Phase 1 improvements
3. Consider user feedback on priorities
4. Implement in phases with user testing between phases
