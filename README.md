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

## Markdown Support

`confl` automatically converts Markdown to Confluence storage format when creating or updating pages. This lets you write in familiar Markdown syntax while maintaining compatibility with Confluence's XHTML-based storage format.

### Supported Markdown Features

✅ **Fully Supported:**
- **Headings** — `# H1` through `###### H6`
- **Bold** — `**text**` or `__text__`
- **Italic** — `*text*` or `_text_`
- **Inline code** — `` `code` ``
- **Code blocks** — with syntax highlighting
  ```python
  def hello():
      print("world")
  ```
- **Links** — `[text](url)`
- **Images** — `![alt](url)` (external URLs and attachments)
- **Lists** — ordered (`1. item`) and unordered (`- item`)
- **Tables** — GitHub-flavored Markdown tables
- **Block quotes** — `> quote`
- **Horizontal rules** — `---` or `***`

### Confluence-Specific Features

✅ **Full Support:**
- **Code macro** — Automatically used for code blocks with syntax highlighting
- **Info/Warning/Note/Tip panels** — Use special blockquote syntax:
  ```markdown
  > **INFO**: This is an info panel
  > **WARNING**: This is a warning
  > **NOTE**: This is a note
  > **TIP**: This is a helpful tip
  ```

⚠️ **Partial Support:**
- **Status indicators** — Converted to emoji badges when reading (✅ ⚠️ ❌ ℹ️ ⚪)
- **Expand macro** — Converted to HTML `<details>/<summary>` when reading
- **TOC macro** — Converted to italic text placeholder when reading

❌ **Not Supported (Markdown Creation):**
- **Status boxes** — Can read, but can't create from Markdown
- **Collapsible panels** — Can read, but can't create from Markdown
- **Advanced macros** — Jira issues, page trees, etc.
- **Page links** — Use direct URLs instead

### Usage Examples

**Create a page with Markdown:**
```bash
# From command line argument
confl page create --space DOCS --title "API Guide" --body "# API\n\nUse \`GET /api/v1\`"

# From file
confl page create --space DOCS --title "README" --body-file README.md

# From stdin
cat notes.md | confl page create --space DOCS --title "Notes"
```

**Update a page with Markdown:**
```bash
confl page update PAGE_ID --body "## Updated\n\nNew content"
```

**Get page content in different formats:**
```bash
# Default: Rich terminal rendering with formatting
confl page get PAGE_ID

# Markdown format (for editing/saving)
confl page get PAGE_ID --markdown > page.md

# Plain text (no formatting)
confl page get PAGE_ID --plain

# Raw storage format (Confluence XHTML)
confl page get PAGE_ID --raw

# JSON (full API response)
confl page get PAGE_ID --json

# Body only (suppress metadata header)
confl page get PAGE_ID --body-only
```

### Bypassing Conversion (Raw Mode)

Use `--raw` to skip Markdown conversion and provide Confluence storage format directly:

```bash
# Provide storage format XHTML directly
confl page create --space DOCS --title "Advanced" --raw \
  --body '<ac:structured-macro ac:name="info">...</ac:structured-macro>'
```

This is useful when you need to:
- Use Confluence features not available in Markdown
- Preserve exact formatting from another Confluence page
- Debug conversion issues

### Troubleshooting

**Problem: Code block not rendering with syntax highlighting**

Make sure you specify the language after the opening backticks:

```markdown
```python  ← specify language
def hello():
    pass
` ` `
```

**Problem: Table not rendering correctly**

Ensure your table has proper header separators:

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**Problem: Special characters appearing as HTML entities**

This is expected behavior for security. Characters like `<`, `>`, `&` are automatically escaped.

**Problem: Content from Confluence looks different after edit**

Conversion is not always bidirectional. Some Confluence features (macros, panels) don't have Markdown equivalents and are converted to approximations. Use `--raw` mode if you need to preserve exact Confluence formatting.

### Limitations

- **Round-trip fidelity**: Markdown → Storage → Markdown may lose some formatting
- **Macro limitations**: Advanced Confluence macros will be converted to text or omitted
- **Nested content**: Complex nested structures may not convert cleanly
- **Best practice**: If you're editing in Markdown, stick to the supported features listed above

For full control over Confluence-specific features, use `--raw` mode with storage format XHTML.
