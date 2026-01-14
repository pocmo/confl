# Content Rendering Architecture

## Problem Statement

When fetching Confluence pages via the API, the content comes in various formats (storage, atlas_doc_format, view, etc.). We need to render this content as readable, nicely formatted terminal output using Rich.

The key challenge: **How do we convert Confluence API responses to beautiful terminal output?**

## API Body Format Options

The Confluence Cloud REST API v2 supports multiple body formats via the `body-format` parameter:

### 1. Storage Format (`STORAGE`)

**What it is:**
- XHTML-based format with Confluence-specific tags and macros
- The canonical format used internally by Confluence
- Example:
  ```xml
  <p>Hello <strong>world</strong></p>
  <ac:structured-macro ac:name="code" ac:schema-version="1">
    <ac:parameter ac:name="language">python</ac:parameter>
    <ac:plain-text-body><![CDATA[print("hello")]]></ac:plain-text-body>
  </ac:structured-macro>
  ```

**Pros:**
- Most complete format with full fidelity
- Contains all Confluence macros and features
- Our existing converter already handles this format well
- We have extensive test coverage for storage ↔ Markdown conversion

**Cons:**
- Contains custom Confluence XML tags (not standard HTML)
- Requires custom parsing for macros

### 2. Atlas Doc Format (`ATLAS_DOC_FORMAT`)

**What it is:**
- JSON-based document structure (Atlassian Document Format / ADF)
- Modern format designed for programmatic manipulation
- Example:
  ```json
  {
    "version": 1,
    "type": "doc",
    "content": [
      {
        "type": "paragraph",
        "content": [
          { "type": "text", "text": "Hello " },
          { "type": "text", "text": "world", "marks": [{"type": "strong"}] }
        ]
      }
    ]
  }
  ```

**Pros:**
- Structured JSON format, easy to parse
- Well-documented by Atlassian
- Python library available: `atlas-doc-parser` (can convert ADF → Markdown)
- Future-proof format for new Confluence features

**Cons:**
- Returned as double-escaped JSON string (needs JSON.parse twice)
- Less mature than storage format
- Additional dependency required

### 3. View Format (`VIEW`)

**What it is:**
- Pre-rendered HTML for browser display
- What users see in Confluence web interface

**Pros:**
- Already rendered, no macro processing needed

**Cons:**
- Not designed for round-trip editing
- May contain JavaScript, CSS, extra wrapper elements
- Rendering could change over time (not stable)
- Overkill for terminal display

### 4. Other Formats

- `EXPORT_VIEW` - HTML for PDF generation
- `ANONYMOUS_EXPORT_VIEW` - Export without user-specific content
- `EDITOR` - Format for Confluence editor

These are specialized and not suitable for our use case.

## Recommended Approach

### Primary Strategy: Storage Format → Markdown → Rich

**Use `STORAGE` format** as the API response format for the following reasons:

1. **Existing Infrastructure**: We already have robust `storage_to_markdown()` converter with extensive test coverage (77+ converter tests)
2. **Proven Compatibility**: Our converter handles all major Confluence features:
   - Headings, paragraphs, formatting (bold, italic, code)
   - Lists (ordered, unordered, nested)
   - Code blocks with syntax highlighting
   - Tables
   - Links and images
   - Block quotes
   - **Confluence Macros:**
     - Code macro with language
     - Info/Warning/Note/Tip panels
     - Status indicator macro (with emoji badges)
     - Expand macro (collapsible sections)
     - TOC macro
3. **Rich Integration**: Rich has excellent built-in Markdown rendering support that handles all these elements beautifully
4. **Simple Pipeline**: `Storage → Markdown → Rich` is a clean, 2-step process
5. **No Additional Dependencies**: Uses existing libraries (mistune, markdownify, rich)

### Rendering Pipeline

```
┌─────────────────┐
│ Confluence API  │
│  (body.storage) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ storage_to_     │
│  markdown()     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Rich Markdown   │
│  Rendering      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Terminal Output │
└─────────────────┘
```

### Implementation Example

```python
from rich.console import Console
from rich.markdown import Markdown
from confl.converter import storage_to_markdown

def render_page_to_terminal(page_body_storage: str) -> None:
    """Render Confluence page storage format to terminal."""
    # Convert storage format to Markdown
    markdown_text = storage_to_markdown(page_body_storage)
    
    # Render with Rich
    console = Console()
    md = Markdown(markdown_text)
    console.print(md)
```

### Alternative: ADF Support (Future)

For future enhancement, we could add ADF support as an alternative:

```python
from atlas_doc_parser.api import NodeDoc

def render_adf_to_terminal(adf_json: dict) -> None:
    """Render ADF format to terminal."""
    # Parse ADF
    doc = NodeDoc.from_dict(adf_json)
    markdown_text = doc.to_markdown()
    
    # Render with Rich
    console = Console()
    md = Markdown(markdown_text)
    console.print(md)
```

**Recommendation:** Start with storage format. Add ADF support only if:
- Users request it
- We encounter storage format limitations
- Atlassian deprecates storage format (unlikely in near term)

## Confluence-Specific Element Handling

Our existing converter handles these Confluence elements:

### Supported Macros (Storage → Markdown)

| Macro | Markdown Representation | Terminal Output |
|-------|------------------------|-----------------|
| **Code macro** | ` ```language\ncode\n``` ` | Syntax-highlighted code block |
| **Info panel** | `> **INFO**: content` | Blockquote with label |
| **Warning panel** | `> **WARNING**: content` | Blockquote with label |
| **Note panel** | `> **NOTE**: content` | Blockquote with label |
| **Tip panel** | `> **TIP**: content` | Blockquote with label |
| **Status macro** | `✅ **title**` (emoji badge) | Colored emoji + text |
| **Expand macro** | `<details><summary>title</summary>content</details>` | Collapsible section |
| **TOC macro** | `_Table of Contents_` | Italic placeholder |

### Unsupported Macros

For macros we don't explicitly handle:
- Extract and display text content if available
- Otherwise, silently skip

Common unsupported macros that may need future work:
- **Children macro** - List child pages
- **Jira macro** - Embedded Jira issues
- **Excerpt macro** - Reusable content blocks
- **Anchor macro** - Internal page links
- **Page tree macro** - Hierarchical page list

**Strategy:** Display a placeholder or extract any readable text. Don't fail on unknown macros.

### Page Links

Storage format uses special tags for internal links:
```xml
<ac:link ac:card-appearance="inline">
  <ri:page ri:space-key="PM" ri:content-title="Page Title" />
  <ac:link-body>Page Title</ac:link-body>
</ac:link>
```

**Current Status:** Our converter may not fully handle these yet.

**Recommendation:** Add handling to convert to Markdown links:
- Extract link text from `<ac:link-body>`
- Generate URL or show title only if URL not available
- Example: `[Page Title](URL)` or just `Page Title` if no URL

## Testing Strategy

### Unit Tests

✅ Already have comprehensive tests in `tests/test_converter.py`:
- 77+ converter tests covering all major features
- Both Markdown → Storage and Storage → Markdown

### Integration Tests

**Need to add:**
1. Real Confluence page samples (fixtures)
2. End-to-end rendering tests
3. Visual regression tests (optional)

### Test Fixtures

Create sample pages in `tests/fixtures/pages/`:
- `simple_page.json` - Basic text and formatting
- `code_blocks.json` - Code macros with various languages
- `tables_lists.json` - Complex tables and nested lists
- `macros.json` - Info/Warning/Note panels, expand, status
- `links_images.json` - Various link and image types

Each fixture should contain:
```json
{
  "id": "12345",
  "title": "Test Page",
  "body": {
    "storage": {
      "value": "<xml storage format>",
      "representation": "storage"
    }
  }
}
```

## Output Format Flags

As specified in `content-formats.md`, support these output flags:

| Flag | Description | Implementation |
|------|-------------|----------------|
| (default) | Rich terminal rendering | `storage_to_markdown()` + `Rich(Markdown)` |
| `--markdown` | Raw Markdown text | `storage_to_markdown()` only |
| `--json` | Full API response | `json.dumps(response)` |
| `--raw` | Confluence storage format | Return `body.storage.value` as-is |
| `--plain` | Plain text, no formatting | `storage_to_markdown()` then strip formatting |

## Rich Rendering Features

Rich's Markdown renderer supports:
- ✅ Headings (with decorative boxes for H1)
- ✅ Bold, italic, inline code
- ✅ Lists (ordered, unordered, nested)
- ✅ Code blocks with syntax highlighting
- ✅ Tables with borders
- ✅ Blockquotes with left border
- ✅ Links (clickable in some terminals)
- ✅ Horizontal rules

**Limitations:**
- No built-in support for collapsible `<details>` (will render as static content)
- Images: Shows `![alt text](url)` notation (can't display images in most terminals)

## Implementation Tasks

Based on this research, file these follow-up tickets:

### P0 - Critical for MVP
1. ✅ Fix `get_page()` to request `body-format=storage` (already done)
2. Implement `page get` command with Rich rendering
3. Add `--markdown`, `--json`, `--raw` output flags
4. Handle unknown macros gracefully (extract text or skip)

### P1 - Important
1. Add test fixtures with real Confluence page samples
2. Improve page link handling (`<ac:link>` → Markdown links)
3. Add `--plain` output flag
4. Handle images gracefully (show alt text if attachment, URL if external)

### P2 - Nice to Have
1. Enhanced macro support (children, excerpt, jira macros)
2. Consider ADF format support as alternative
3. Visual regression testing for terminal output
4. Support for embedded media (show placeholder with link)

## Alternatives Considered

### Alternative 1: Use `view` format + HTML-to-Markdown

**Rejected because:**
- View format is unstable (rendering can change)
- Contains extra wrapper HTML, CSS, JavaScript
- Not designed for terminal display
- Would require more complex HTML parsing

### Alternative 2: Use ADF format directly

**Deferred because:**
- Requires additional dependency (`atlas-doc-parser`)
- Storage format already works well with our converter
- ADF is less mature and documented than storage format
- Can add ADF support later if needed

### Alternative 3: Custom XML parser for storage format

**Rejected because:**
- Reinventing the wheel
- Our existing markdownify-based converter works well
- Would require significant development and testing

## References

- [Confluence Cloud REST API v2 - Body Formats](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#body-formats)
- [Confluence Storage Format Documentation](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
- [Atlassian Document Format (ADF) Specification](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/)
- [Rich Library - Markdown Rendering](https://rich.readthedocs.io/en/stable/markdown.html)
- [atlas-doc-parser Python Library](https://pypi.org/project/atlas-doc-parser/)
- Web research conducted: 2026-01-14

## Decision Summary

✅ **Use Storage Format (`STORAGE`) as primary content format**

✅ **Rendering pipeline: Storage → Markdown → Rich**

✅ **Leverage existing `storage_to_markdown()` converter**

✅ **No new dependencies required**

✅ **Support multiple output flags (default/markdown/json/raw/plain)**

📝 **Future consideration: Add ADF support if needed**
