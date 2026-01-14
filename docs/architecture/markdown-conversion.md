# Markdown ↔ Confluence Storage Format Conversion

## Summary

After researching Python libraries for Markdown to/from Confluence storage format conversion, I recommend using **md2cf** for Markdown→Storage and **markdownify** (with Confluence adaptations) for Storage→Markdown conversions.

## Research Findings

### Confluence Storage Format

- Confluence uses a proprietary XHTML-based XML format for content storage
- Custom XML tags for macros: `<ac:structured-macro>`, `<ac:parameter>`, `<ac:rich-text-body>`
- Not standard HTML - must use storage format for API `body.storage.value`
- Official spec: https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html

### Available Libraries

#### Markdown → Storage Format

1. **md2cf** (RECOMMENDED)
   - Uses Mistune parser for accurate Markdown parsing
   - Outputs proper Confluence Storage Format XHTML
   - Supports: headings, lists, blockquotes, code blocks, images, links, tables
   - Includes REST API integration (we won't use this - we have our own client)
   - Active maintenance, good docs
   - Install: `pip install md2cf`
   - GitHub: https://github.com/iamjackg/md2cf

2. **markdown-to-confluence**
   - More feature-rich (diagrams, formulas, emojis, ToC)
   - Includes API automation
   - May be overkill for our needs
   - Install: `pip install markdown-to-confluence`

3. **convert-to-confluence**
   - Converts to Wiki Markup, NOT storage format XHTML
   - Not suitable for our use case

#### Storage Format → Markdown

1. **markdownify** (with Confluence adaptations)
   - Popular HTML→Markdown library
   - Can be extended to handle Confluence `ac:` tags
   - Requires custom handling for macros
   - Base library: `pip install markdownify`
   - Will need custom renderer subclass

2. **confluence-markdown-exporter**
   - Complete tool for exporting Confluence→Markdown
   - Handles macros, images, attachments
   - Uses Confluence API directly (we don't need this)
   - Code could be studied for conversion logic

### Feature Coverage Analysis

| Feature | md2cf (MD→Storage) | markdownify (Storage→MD) |
|---------|-------------------|------------------------|
| Headings (h1-h6) | ✅ | ✅ |
| Bold/Italic | ✅ | ✅ |
| Lists (ordered/unordered) | ✅ | ✅ |
| Code blocks (with syntax) | ✅ | ✅ |
| Inline code | ✅ | ✅ |
| Links | ✅ | ✅ |
| Images | ✅ | ✅ |
| Tables | ✅ | ✅ |
| Blockquotes | ✅ | ✅ |
| Confluence macros | ⚠️ Manual | ⚠️ Manual |
| Status boxes | ❌ | ❌ |
| Collapsible panels | ❌ | ❌ |

### Limitations

1. **Confluence-specific features** (macros, status boxes, panels) require:
   - Custom extensions to conversion logic
   - May need to document "unsupported features" for users
   - Could be P2/P3 follow-up work

2. **Bidirectional fidelity**:
   - Markdown→Storage→Markdown may lose some formatting
   - Not all Confluence features have Markdown equivalents
   - Users editing in Markdown should stick to supported features

## Recommended Approach

### Phase 1: Core Implementation (P0)

1. **Markdown → Storage Format**
   - Use `md2cf` library
   - Extract just the conversion logic (not the API client)
   - Create `src/confl/converter.py` module with:
     - `markdown_to_storage(md: str) -> str`
   - Support basic Markdown features (see table above)

2. **Storage Format → Markdown**
   - Use `markdownify` library
   - Create custom renderer for Confluence tags
   - Add to `src/confl/converter.py`:
     - `storage_to_markdown(storage: str) -> str`
   - Best-effort conversion, document limitations

3. **Testing**
   - Add fixtures for sample Markdown and storage format pairs
   - Test round-trip conversion for common cases
   - Document conversion limitations in README

### Phase 2: Enhanced Features (P1-P2)

1. **Common Macro Support**
   - Code macro with syntax highlighting
   - Info/warning/note panels
   - Status indicators
   - Table of contents

2. **Edge Cases**
   - Nested lists
   - Complex tables
   - Mixed content (code + tables + images)

3. **Validation**
   - Warn on unsupported Markdown features
   - Validate storage format output
   - Provide "preview" command before upload

## Implementation Plan

### Dependencies to Add

```toml
[project]
dependencies = [
    # ... existing ...
    "mistune>=3.0.0",  # md2cf uses this
]

[project.optional-dependencies]
dev = [
    # ... existing ...
    "markdownify>=0.11.0",  # for storage→markdown
]
```

### Module Structure

```
src/confl/
├── converter.py          # NEW: Conversion logic
│   ├── markdown_to_storage()
│   ├── storage_to_markdown()
│   └── ConfluenceRenderer (custom mistune renderer)
├── api_client.py         # Uses converter for page content
└── cli.py               # --markdown vs --raw flags
```

### Integration Points

1. **API Client**: `create_page()` and `update_page()` accept markdown, convert to storage
2. **CLI**: `get` command outputs markdown by default (convert from storage)
3. **Format Flags**: `--raw` bypasses conversion, `--markdown` (default) converts

## Alternatives Considered

1. **Use atlassian-python-api**
   - Full Confluence client library
   - Heavy dependency, we only need conversion
   - ❌ Rejected: Too much overlap with our API client

2. **Build custom converter from scratch**
   - Full control over features
   - Significant implementation work
   - ❌ Rejected: Don't reinvent the wheel

3. **Use markdown-to-confluence**
   - More features than md2cf
   - Heavier dependency
   - ⚠️ Consider if we need advanced features later

## Follow-up Tickets to Create

1. **[P0] Implement markdown_to_storage() conversion**
   - Add mistune dependency
   - Create converter.py module
   - Extract/adapt md2cf conversion logic
   - Add tests with fixtures

2. **[P1] Implement storage_to_markdown() conversion**
   - Add markdownify dependency
   - Create custom Confluence renderer
   - Handle basic ac: tags
   - Add tests

3. **[P2] Document Markdown conversion limitations**
   - Update README with supported features
   - Document unsupported Confluence features
   - Add troubleshooting guide

4. **[P3] Add macro support for info/warning panels**
   - Extend converter for common macros
   - Map to Markdown equivalents where possible

## References

- [Confluence Storage Format Docs](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
- [md2cf GitHub](https://github.com/iamjackg/md2cf)
- [markdownify PyPI](https://pypi.org/project/markdownify/)
- [Mistune Documentation](https://mistune.readthedocs.io/)
