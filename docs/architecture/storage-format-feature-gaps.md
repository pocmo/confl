# Confluence Storage Format Feature Support Analysis

**Date:** 2026-01-14  
**Purpose:** Identify what Confluence storage format features we support vs. what exists, and prioritize gaps.

## Executive Summary

Our `storage_to_markdown()` converter has **strong coverage** of core Confluence storage format features with 77+ converter tests. We handle most common elements users encounter daily. Key gaps are in advanced macros (children, excerpt, jira) and page link handling.

**Priority Recommendation:** Focus on P1 items (page links, attachments visibility) as they affect readability. P2 items (advanced macros) are nice-to-have but less critical for MVP.

---

## 1. Storage Format Elements: Current Support Status

### 1.1 Basic XHTML Elements

| Element | Status | Notes |
|---------|--------|-------|
| **Headings** `<h1>` - `<h6>` | ✅ Supported | Full support with ATX-style markdown |
| **Bold** `<strong>` | ✅ Supported | Converts to `**text**` |
| **Italic** `<em>` | ✅ Supported | Converts to `*text*` |
| **Underline** `<u>` | ⚠️ Partial | No markdown equivalent, may render as plain text |
| **Strikethrough** `<s>`, `<del>` | ⚠️ Partial | May not be handled (need to verify) |
| **Superscript** `<sup>` | ⚠️ Partial | No markdown equivalent |
| **Subscript** `<sub>` | ⚠️ Partial | No markdown equivalent |
| **Inline code** `<code>` | ✅ Supported | Converts to `` `code` `` |
| **Paragraphs** `<p>` | ✅ Supported | Full support |
| **Line breaks** `<br/>` | ✅ Supported | Converts to double space + newline |
| **Horizontal rule** `<hr/>` | ✅ Supported | Converts to `---` |

**Priority:** P0 (core features)  
**Gaps:** Underline, strikethrough, super/subscript have no markdown equivalents. Low priority as they're rarely used.

### 1.2 Lists

| Element | Status | Notes |
|---------|--------|-------|
| **Unordered lists** `<ul>`, `<li>` | ✅ Supported | Full support including nested |
| **Ordered lists** `<ol>`, `<li>` | ✅ Supported | Full support including nested |
| **Task lists** `<ac:task-list>`, `<ac:task>` | ❌ Missing | Common for project management |

**Priority:** P0 for basic lists (done), P1 for task lists  
**Complexity:** Task lists = Moderate (need to convert to `- [ ]` / `- [x]` syntax)

### 1.3 Code Blocks

| Element | Status | Notes |
|---------|--------|-------|
| **Preformatted** `<pre>` | ✅ Supported | Via code macro |
| **Code macro** `<ac:structured-macro ac:name="code">` | ✅ Supported | Full support with syntax highlighting |
| **Noformat macro** | ❌ Missing | Similar to code but no syntax highlighting |

**Priority:** P0 (mostly done), P2 for noformat macro  
**Complexity:** Noformat = Simple (just render as plain code block)

### 1.4 Links and References

| Element | Status | Notes |
|---------|--------|-------|
| **External links** `<a href="http...">` | ✅ Supported | Standard HTML links |
| **Page links** `<ac:link><ri:page>` | ⚠️ Partial | May not fully handle, needs improvement |
| **Attachment links** `<ri:attachment>` | ⚠️ Partial | May not handle well |
| **User mentions** `<ri:user>` | ❌ Missing | Common in collaborative pages |
| **Anchor links** `<ac:anchor>` | ❌ Missing | For internal page navigation |

**Priority:** P1 for page links and attachments (affect readability), P2 for mentions and anchors  
**Complexity:** Page links = Moderate (need to extract title and optionally construct URL)

### 1.5 Images and Media

| Element | Status | Notes |
|---------|--------|-------|
| **External images** `<ac:image><ri:url>` | ✅ Supported | Converts to `![alt](url)` |
| **Attached images** `<ac:image><ri:attachment>` | ✅ Supported | Converts to `![alt](filename)` |
| **Image captions** `<ac:caption>` | ✅ Supported | Used as alt text |
| **Gallery macro** | ❌ Missing | Displays multiple images |
| **Multimedia macro** | ❌ Missing | Videos, audio |
| **Widget connector** | ❌ Missing | YouTube, Twitter embeds |

**Priority:** P0 (mostly done), P2 for gallery/multimedia  
**Complexity:** Gallery = Moderate, Multimedia/Widget = Complex (may just show placeholder)

### 1.6 Tables

| Element | Status | Notes |
|---------|--------|-------|
| **Basic tables** `<table>`, `<tr>`, `<td>`, `<th>` | ✅ Supported | Full support |
| **Table alignment** `style="text-align:..."` | ✅ Supported | Preserves alignment |
| **Merged cells** `colspan`, `rowspan` | 🔍 Unknown | Need to verify (markdown has limited support) |
| **Nested tables** | 🔍 Unknown | Need to verify |

**Priority:** P0 (mostly done), P2 for merged/nested cells  
**Complexity:** Merged cells = Complex (markdown doesn't support well, may need HTML fallback)

### 1.7 Block Quotes

| Element | Status | Notes |
|---------|--------|-------|
| **Block quotes** `<blockquote>` | ✅ Supported | Converts to `> text` |

**Priority:** P0 (done)

---

## 2. Confluence Macros: Support Status

### 2.1 Panel/Alert Macros (P0)

| Macro | Status | Notes |
|-------|--------|-------|
| **Info panel** | ✅ Supported | Converts to `> **INFO**: content` |
| **Warning panel** | ✅ Supported | Converts to `> **WARNING**: content` |
| **Note panel** | ✅ Supported | Converts to `> **NOTE**: content` |
| **Tip panel** | ✅ Supported | Converts to `> **TIP**: content` |
| **Panel macro** (generic) | ❌ Missing | Like info but customizable title/color |

**Priority:** P0 (mostly done), P2 for generic panel  
**Complexity:** Generic panel = Simple (similar to existing panel macros)

### 2.2 Content Structure Macros (P1)

| Macro | Status | Notes |
|-------|--------|-------|
| **Table of Contents** | ✅ Supported | Shows `_Table of Contents_` placeholder |
| **Expand** | ✅ Supported | Converts to `<details><summary>` |
| **Children display** | ❌ Missing | Lists child pages, common |
| **Page tree** | ❌ Missing | Hierarchical page list |
| **Excerpt** | ❌ Missing | Reusable content blocks, common |
| **Excerpt include** | ❌ Missing | Includes excerpts from other pages |
| **Include page** | ❌ Missing | Embeds entire pages |
| **Section/Column** | ❌ Missing | Multi-column layouts |

**Priority:** P1 for children/excerpt (common), P2 for others  
**Complexity:**  
- Children = Moderate (need API calls to fetch child pages)  
- Excerpt = Moderate (extract text, show with label)  
- Include = Complex (requires fetching other pages)  
- Section/Column = Complex (markdown doesn't support multi-column)

**Recommended handling:**
- Children: Show placeholder `[Children of this page]` or make API call (configurable)
- Excerpt: Extract and show content with `[Excerpt]` label
- Include: Show placeholder `[Included page: Title]`
- Section/Column: Linearize content (markdown limitation)

### 2.3 Status and Badges (P0)

| Macro | Status | Notes |
|-------|--------|-------|
| **Status macro** | ✅ Supported | Converts to emoji badges (✅ ⚠️ ❌ etc.) |

**Priority:** P0 (done)

### 2.4 Integration Macros (P2)

| Macro | Status | Notes |
|-------|--------|-------|
| **Jira issues** | ❌ Missing | Very common in dev teams |
| **Roadmap planner** | ❌ Missing | Project planning |
| **Team calendars** | ❌ Missing | Meeting schedules |

**Priority:** P1 for Jira (very common), P2 for others  
**Complexity:**  
- Jira = Moderate (extract issue keys, show list or placeholder)  
- Roadmap/Calendar = Complex (requires API calls and complex rendering)

**Recommended handling:**
- Jira: Extract issue keys and show as list: `[Jira: PROJ-123, PROJ-124]`
- Others: Show placeholder `[Roadmap]`, `[Calendar]`

### 2.5 File and Attachment Macros (P1)

| Macro | Status | Notes |
|-------|--------|-------|
| **Attachments** | ❌ Missing | Lists page attachments |
| **View file** | ❌ Missing | Displays file content inline |
| **Office Excel/Word/PPT** | ❌ Missing | Previews Office docs |
| **PDF** | ❌ Missing | Displays PDFs inline |

**Priority:** P1 for attachments list, P2 for previews  
**Complexity:**  
- Attachments list = Moderate (need API call)  
- Previews = Complex (just show placeholder/link)

**Recommended handling:**
- Attachments: Show list of filenames with placeholder
- Previews: Show `[File preview: filename.pdf]`

### 2.6 Navigation and Search (P2)

| Macro | Status | Notes |
|-------|--------|-------|
| **Page index** | ❌ Missing | Lists pages in space |
| **Livesearch** | ❌ Missing | Search box |
| **Recently updated** | ❌ Missing | Recent changes |
| **Content report table** | ❌ Missing | Query-based content lists |

**Priority:** P2 (low usage in typical pages)  
**Complexity:** Moderate to Complex (requires API calls)  
**Recommended handling:** Show placeholder with description

### 2.7 User and Social (P2)

| Macro | Status | Notes |
|-------|--------|-------|
| **User profile** | ❌ Missing | Shows user info |
| **Contributors summary** | ❌ Missing | Page contributors |
| **Profile picture** | ❌ Missing | User avatar |
| **User list** | ❌ Missing | Lists users |

**Priority:** P2 (low impact on content readability)  
**Complexity:** Simple to Moderate  
**Recommended handling:** Show username or placeholder

### 2.8 Charts and Visualization (P2)

| Macro | Status | Notes |
|-------|--------|-------|
| **Chart macro** | ❌ Missing | Bar/pie/line charts |
| **Page properties** | ❌ Missing | Structured metadata |
| **Page properties report** | ❌ Missing | Aggregates metadata |

**Priority:** P2 (specialized use cases)  
**Complexity:** Complex (charts can't render in terminal, show data table instead)  
**Recommended handling:** Show placeholder or extract underlying data

### 2.9 Other Macros (P2)

| Macro | Status | Notes |
|-------|--------|-------|
| **Anchor** | ❌ Missing | Internal page links |
| **RSS feed** | ❌ Missing | External RSS |
| **HTML/HTML include** | ❌ Missing | Embedded HTML (security risk) |
| **Create from template** | ❌ Missing | Button to create pages |

**Priority:** P2  
**Complexity:** Simple to Moderate  
**Recommended handling:**
- Anchor: Convert to markdown heading link `[link](#heading)`
- RSS: Show placeholder `[RSS Feed: URL]`
- HTML: Strip or show placeholder (security concern)
- Create button: Show placeholder `[Create page button]`

### 2.10 Unknown/Third-party Macros

| Status | Notes |
|--------|-------|
| ⚠️ Graceful fallback | We handle unknown macros gracefully (extract text or show placeholder) |

**Priority:** P0 (done)  
**Coverage:** Unknown macros now show `[macro-name]` placeholder with any extractable content

---

## 3. Feature Priority Matrix

### P0 - Critical for MVP (Already Complete ✅)

These are essential for basic page readability and are already implemented:

- ✅ Headings, paragraphs, basic formatting
- ✅ Lists (ordered, unordered, nested)
- ✅ Code blocks with syntax highlighting
- ✅ Links (external)
- ✅ Images (external and attached)
- ✅ Tables
- ✅ Block quotes
- ✅ Info/warning/note/tip panels
- ✅ Status macro with emoji badges
- ✅ Expand macro
- ✅ TOC macro (placeholder)
- ✅ Unknown macro handling (graceful fallback)

**Status:** All P0 features complete. MVP is viable.

### P1 - Important (Affects Readability)

Should be implemented soon as they're common and affect content understanding:

1. **Page link handling** - Improve `<ac:link><ri:page>` conversion
   - Extract page title
   - Optionally construct URL
   - Complexity: Moderate
   - Impact: High (internal links very common)

2. **Task lists** - Convert `<ac:task-list>` to markdown checkboxes
   - Complexity: Moderate
   - Impact: Medium (common in project pages)

3. **User mentions** - Handle `<ri:user>` tags
   - Show as `@username`
   - Complexity: Simple
   - Impact: Medium (common in collaborative pages)

4. **Jira macro** - Extract issue keys
   - Show as list: `[Jira: PROJ-123, PROJ-124]`
   - Complexity: Moderate
   - Impact: High for dev teams

5. **Children macro** - List child pages
   - Option 1: Show placeholder `[Children of this page]`
   - Option 2: Make API call to list children (configurable)
   - Complexity: Moderate
   - Impact: Medium (common for navigation)

6. **Excerpt macro** - Extract reusable content blocks
   - Show with label: `[Excerpt]\n\ncontent...\n\n`
   - Complexity: Moderate
   - Impact: Medium (common for summaries)

7. **Attachments macro** - List files attached to page
   - Show list with placeholder
   - Complexity: Moderate (needs API call)
   - Impact: Medium

**Estimated effort:** 2-4 tickets

### P2 - Nice to Have (Low Impact or Rare)

Lower priority, implement if time permits:

1. **Strikethrough** (`<s>`, `<del>`) - Some markdown renderers support `~~text~~`
2. **Noformat macro** - Like code block but no highlighting
3. **Panel macro** (generic) - Customizable panels
4. **Anchor macro** - Internal page links
5. **Gallery macro** - Multiple images
6. **Include page macro** - Embedded pages
7. **Page tree macro** - Hierarchical navigation
8. **Section/Column macro** - Multi-column layout (linearize in terminal)
9. **Chart macros** - Extract data or show placeholder
10. **Page properties macros** - Metadata display
11. **User/social macros** - Profile, contributors, etc.
12. **Navigation macros** - Page index, recently updated, etc.
13. **Multimedia/Widget connector** - Videos, embeds (show link/placeholder)
14. **Office/PDF preview macros** - Show filename/link

**Estimated effort:** Multiple tickets, as-needed basis

### P3 - Not Planned

Features that are very rare, too complex, or not suitable for terminal:

- HTML macro (security risk)
- Complex merged cells in tables (markdown limitation)
- Advanced roadmap/calendar features (complex rendering)
- RSS feed macro
- Create from template buttons
- Third-party/custom macros (handle via fallback)

---

## 4. Implementation Complexity Estimates

| Complexity | Time Estimate | Examples |
|------------|---------------|----------|
| **Simple** | 1-2 hours | User mentions, strikethrough, noformat, generic panel |
| **Moderate** | 3-8 hours | Task lists, page links, excerpt, children (with API), jira keys, attachments list |
| **Complex** | 1-2 days | Include page (fetch+render), gallery (multiple images), section/column (layout), charts (data extraction) |
| **Discovery needed** | TBD | Merged cells, nested tables, multimedia rendering |

---

## 5. Testing Coverage

### Current Coverage ✅

We have comprehensive test coverage (77+ tests) for:
- All P0 features
- Both directions: Markdown → Storage and Storage → Markdown
- Edge cases (HTML escaping, nested structures, etc.)

**Test file:** `tests/test_converter.py`

### Gaps 🔍

Missing test fixtures:
- Real Confluence page samples (tracked in ticket c-32c8)
- Complex nested macro combinations
- Task lists, page links, user mentions
- Unknown/third-party macros (we have basic tests)

**Recommendation:** Add integration tests with real page fixtures to validate end-to-end conversion.

---

## 6. Recommendations

### Immediate Actions (This Ticket)

1. ✅ Document feature support status (this document)
2. ✅ Identify priority gaps
3. ✅ File follow-up tickets

### Next Steps (Follow-up Tickets)

**File these implementation tickets:**

1. **P1 - Improve page link handling** (`<ac:link><ri:page>`)
   - Extract page title from `<ac:link-body>`
   - Show as `[Page Title]` or construct URL if possible
   - Handle space key and content title attributes

2. **P1 - Add task list support** (`<ac:task-list>`)
   - Convert to markdown checkboxes: `- [ ]` / `- [x]`
   - Extract task status and text

3. **P1 - Add user mention support** (`<ri:user>`)
   - Convert to `@username` or `@fullname`
   - Extract username attribute

4. **P1 - Add Jira macro support**
   - Extract issue keys (JQL query or explicit list)
   - Show as `[Jira: PROJ-123, PROJ-124]` or list

5. **P1 - Add children macro placeholder**
   - Show `[Children of this page]` or optionally make API call
   - Consider configuration option for API call behavior

6. **P1 - Add excerpt macro support**
   - Extract content from rich-text-body
   - Show with `[Excerpt]` label

7. **P2 - Add attachments macro support**
   - Make API call to list attachments (or show placeholder)
   - Format as list with filenames

8. **P2 - Add strikethrough support** (`<s>`, `<del>`)
   - Convert to `~~text~~` (GFM extension)
   - May need Rich markdown config

9. **P2 - Add noformat macro**
   - Convert to plain code block without language

10. **P2 - Add panel macro** (generic)
    - Like info/warning but with custom title
    - Extract title parameter

### Architectural Considerations

1. **API calls for dynamic macros:** Some macros (children, attachments) require API calls. Consider:
   - Configuration option: `--resolve-macros` flag
   - Caching to avoid repeated API calls
   - Graceful fallback if API call fails

2. **Markdown limitations:** Some Confluence features have no markdown equivalent:
   - Multi-column layouts → linearize
   - Merged table cells → best effort or HTML fallback
   - Charts/graphs → show data table or placeholder
   - Videos/widgets → show link/placeholder

3. **Security considerations:**
   - HTML macro: Don't render arbitrary HTML
   - External embeds: Show link, don't execute

4. **Performance:**
   - Large pages with many macros: Consider lazy loading or limits
   - API calls: Batch requests where possible

---

## 7. Confluence Storage Format Resources

### Official Documentation

- [Confluence Storage Format](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
- [Storage Format for Macros](https://confluence.atlassian.com/spaces/CONF50/pages/329980084/Confluence+Storage+Format+for+Macros)
- [Confluence Macros List](https://confluence.atlassian.com/doc/macros-139387.html)
- [Confluence Cloud REST API v2](https://developer.atlassian.com/cloud/confluence/rest/v2/)

### Internal Documentation

- `docs/architecture/content-rendering.md` - Our rendering approach
- `docs/architecture/content-formats.md` - Format requirements
- `src/confl/converter.py` - Converter implementation
- `tests/test_converter.py` - 77+ converter tests

---

## 8. Conclusion

**Current state:** Strong foundation with P0 features complete. Core readability is good.

**Main gaps:** Page links, task lists, user mentions, Jira macro, children/excerpt macros.

**Priority:** Focus on P1 items (7 tickets) as they're common and affect content understanding. P2 items are nice-to-have but not critical for MVP.

**Strategy:**
1. Implement P1 features (page links, task lists, mentions, jira, children, excerpt)
2. Add real page fixtures for integration testing
3. Monitor user feedback for additional macro support needs
4. Handle remaining features on as-needed basis

**Timeline estimate:**
- P1 features: 2-3 iterations (7 tickets, most are moderate complexity)
- P2 features: Ongoing, as-needed

The converter is production-ready for MVP with current feature set. P1 enhancements will significantly improve user experience for common use cases.
