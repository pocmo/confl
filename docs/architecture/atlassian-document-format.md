---
Status: REFERENCE
Date: 2025-12-01
Purpose: Document Atlassian Document Format (ADF) specification
---

# Atlassian Document Format (ADF)

## Overview

The Atlassian Document Format (ADF) is a JSON-based rich text storage format used across Atlassian products including Confluence Cloud and Jira Cloud. It represents structured content as a hierarchy of nodes with marks for text formatting.

**Key characteristics:**
- JSON-based (vs. XHTML-based storage format)
- Shared across Atlassian products (Jira, Confluence)
- Schema-validated document structure
- Supports block nodes (paragraphs, headings, tables) and inline nodes (text, links, emoji)

## Why ADF Matters for confl

Understanding ADF is important because:
1. **API Representation**: Confluence Cloud REST API v2 supports both `storage` (XHTML) and `atlas_doc_format` (ADF) representations
2. **Modern Format**: ADF is the format used by Confluence's modern editor
3. **Potential Alternative**: ADF may be easier to work with than storage format for rendering and conversion
4. **Future Considerations**: We may want to support ADF input/output alongside storage format

## ADF vs Storage Format

| Aspect | ADF (atlas_doc_format) | Storage Format |
|--------|------------------------|----------------|
| Syntax | JSON | XHTML (XML-based) |
| Structure | Node hierarchy with marks | XML tags and attributes |
| Usage | Modern editor | Legacy, still primary format |
| API Field | `body.atlas_doc_format` | `body.storage` |
| Conversion | Markdown → ADF requires custom logic | Markdown → Storage via md2cf |

**Current confl implementation:** Uses storage format (XHTML) as primary format.

## JSON Schema

ADF documents follow a JSON schema available at: [http://go.atlassian.com/adf-json-schema](http://go.atlassian.com/adf-json-schema)

**Note:** Not all marks and nodes in the schema are valid for Confluence specifically. Refer to Atlassian documentation for supported features.

## Document Structure

### Root Node

Every ADF document starts with a `doc` node:

```json
{
  "version": 1,
  "type": "doc",
  "content": []
}
```

**Properties:**
- `version` (required): ADF version (currently 1)
- `type` (required): Always "doc" for root
- `content` (required): Array of top-level block nodes

### Node Types

Nodes have common properties:

| Property | Required | Description |
|----------|----------|-------------|
| `type` | ✔ | Node type (e.g., "paragraph", "heading") |
| `content` | ✔ (block nodes) | Array of child nodes |
| `marks` | | Array of formatting marks (for inline nodes) |
| `attrs` | | Additional attributes (varies by node type) |

### Document Order

ADF documents are **ordered**: there's a single sequential path through the document. Traversing in sequence and concatenating nodes yields content in correct order.

## Block Nodes

Block nodes define structural elements of the document.

### Top-Level Block Nodes

Can be placed directly under the root `doc` node:

- `blockquote` — Quote blocks
- `bulletList` — Unordered lists
- `codeBlock` — Code blocks with syntax highlighting
- `expand` — Collapsible sections
- `heading` — Headings (H1-H6)
- `mediaGroup` — Multiple media items
- `mediaSingle` — Single media item
- `orderedList` — Numbered lists
- `panel` — Info/warning/note panels
- `paragraph` — Text paragraphs
- `rule` — Horizontal rule
- `table` — Tables
- `multiBodiedExtension` — Extension with multiple bodies

### Child Block Nodes

Must be children of other nodes:

- `listItem` — List item (child of bulletList/orderedList)
- `media` — Media content (child of mediaGroup/mediaSingle)
- `nestedExpand` — Nested collapsible section
- `tableCell` — Table cell
- `tableHeader` — Table header cell
- `tableRow` — Table row
- `extensionFrame` — Extension frame

## Inline Nodes

Inline nodes contain actual document content:

- `text` — Text content (can have marks)
- `date` — Date representation
- `emoji` — Emoji
- `hardBreak` — Line break
- `inlineCard` — Inline card
- `mention` — User mention
- `status` — Status lozenge
- `mediaInline` — Inline media

## Marks

Marks define text formatting applied to inline nodes (especially `text`).

**Common properties:**
- `type` (required): Mark type
- `attrs`: Additional attributes (e.g., URL for links)

**Available marks:**
- `border` — Border
- `code` — Inline code
- `em` — Italic/emphasis
- `link` — Hyperlink
- `strike` — Strikethrough
- `strong` — Bold
- `subsup` — Subscript/superscript
- `textColor` — Text color
- `underline` — Underline

### Special: Alignment Mark

To center text, add a mark with:
- `type`: "alignment"
- `attrs.align`: "center"

## Examples

### Simple Text

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Hello world"
        }
      ]
    }
  ]
}
```

### Bold Text

```json
{
  "version": 1,
  "type": "doc",
  "content": [
    {
      "type": "paragraph",
      "content": [
        {
          "type": "text",
          "text": "Hello "
        },
        {
          "type": "text",
          "text": "world",
          "marks": [
            {
              "type": "strong"
            }
          ]
        }
      ]
    }
  ]
}
```

Result: Hello **world**

### Heading

```json
{
  "type": "heading",
  "attrs": {
    "level": 1
  },
  "content": [
    {
      "type": "text",
      "text": "Heading 1"
    }
  ]
}
```

**Attributes:**
- `level`: 1-6 (equivalent to HTML `<h1>` through `<h6>`)
- `localId` (optional): Unique identifier within document

### Code Block

```json
{
  "type": "codeBlock",
  "attrs": {
    "language": "javascript"
  },
  "content": [
    {
      "type": "text",
      "text": "var foo = {};\nvar bar = [];"
    }
  ]
}
```

**Attributes:**
- `language`: Code language for syntax highlighting (supports Prism languages)
  - If "text" or unsupported value, renders as plain monospaced text
  - See: [Prism available languages](https://github.com/conorhastings/react-syntax-highlighter/blob/master/AVAILABLE_LANGUAGES_PRISM.MD)

**Content:** Array of `text` nodes without marks.

### Hyperlink

```json
{
  "type": "text",
  "text": "Click here",
  "marks": [
    {
      "type": "link",
      "attrs": {
        "href": "https://example.com"
      }
    }
  ]
}
```

### Multiple Marks

Marks can be combined on a single text node:

```json
{
  "type": "text",
  "text": "Bold and italic",
  "marks": [
    {
      "type": "strong"
    },
    {
      "type": "em"
    }
  ]
}
```

### Bullet List

```json
{
  "type": "bulletList",
  "content": [
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "First item"
            }
          ]
        }
      ]
    },
    {
      "type": "listItem",
      "content": [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Second item"
            }
          ]
        }
      ]
    }
  ]
}
```

### Table

```json
{
  "type": "table",
  "content": [
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableHeader",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Header 1"
                }
              ]
            }
          ]
        },
        {
          "type": "tableHeader",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Header 2"
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "type": "tableRow",
      "content": [
        {
          "type": "tableCell",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Cell 1"
                }
              ]
            }
          ]
        },
        {
          "type": "tableCell",
          "content": [
            {
              "type": "paragraph",
              "content": [
                {
                  "type": "text",
                  "text": "Cell 2"
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## Using ADF with Confluence Cloud API

### Requesting ADF Format

When fetching page content, specify `atlas_doc_format` in the body format:

```bash
GET /wiki/api/v2/pages/{id}?body-format=atlas_doc_format
```

### Creating/Updating Pages with ADF

Specify `representation: "atlas_doc_format"` in the request body:

```json
{
  "spaceId": "123456",
  "status": "current",
  "title": "My Page",
  "body": {
    "representation": "atlas_doc_format",
    "value": "{\"version\":1,\"type\":\"doc\",\"content\":[...]}"
  }
}
```

**Note:** The `value` field is a JSON string containing the ADF document.

## Limitations and Edge Cases

### Confluence-Specific Gaps

- **Documentation**: ADF documentation is primarily for Jira. Some Confluence-specific features may not be fully documented
- **Node Support**: Not all ADF nodes may be supported in Confluence (and vice versa)
- **Best Practice**: Create content in Confluence editor, fetch via API, analyze resulting ADF JSON to understand supported features

### Conversion Challenges

- **No Official Converter**: No official Atlassian endpoint converts HTML/Markdown to ADF for Confluence
- **Community Tools**: Third-party libraries may help, but support varies
- **Bidirectional Conversion**: Converting ADF → Markdown → ADF may lose fidelity

### Extension Nodes

Complex extension nodes (e.g., Jira issues, page trees) may not have clear documentation. Analyze editor-generated ADF for real-world examples.

## Tools and Resources

### Official Documentation

- [ADF Structure Overview](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) — Core concepts, node types, marks
- [ADF JSON Schema](http://go.atlassian.com/adf-json-schema) — Validation schema
- [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/) — API usage
- [Individual Node Documentation](https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/) — Detailed specs for each node type
- [Individual Mark Documentation](https://developer.atlassian.com/cloud/jira/platform/apis/document/marks/) — Detailed specs for each mark type

### Interactive Tools

- [ADF Playground](https://developer.atlassian.com/cloud/jira/platform/apis/document/playground/) — Web-based document builder to construct ADF and view JSON

### Community Resources

- [ADF Conversion Discussion](https://community.developer.atlassian.com/t/converting-to-adf-atlassian-document-format/82496) — Community thread on conversion tools/APIs
- [ADF for Confluence Cloud](https://community.developer.atlassian.com/t/adf-for-confluence-cloud/93088) — Community insights on Confluence-specific ADF usage

## Recommendations for confl

### Current Approach

Continue using **storage format (XHTML)** as primary format:
- Established converter (md2cf) for Markdown → Storage
- Well-documented in Confluence-specific contexts
- Primary format returned by API

### Future Considerations

Consider adding ADF support if:
1. **Rendering Improvements**: ADF's structured JSON may be easier to render than XHTML parsing
2. **Editor Parity**: Supporting ADF input/output for modern editor compatibility
3. **Conversion Library**: A robust Markdown ↔ ADF library becomes available

### Implementation Path

If adding ADF support:
1. Add `--adf` flag to `page get` for ADF output (alongside --raw, --markdown)
2. Add `--adf` flag to `page create/update` for ADF input
3. Implement ADF → Markdown converter for reading (similar to storage_to_markdown)
4. Implement Markdown → ADF converter for writing (or use/adapt existing library)
5. Update documentation to explain when to use ADF vs storage format

## Related Documentation

- [Content Formats](content-formats.md) — Output/input format specifications
- [Markdown Conversion](markdown-conversion.md) — Current Markdown ↔ Storage format approach
- [API.md](API.md) — Confluence API details
