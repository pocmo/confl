"""Tests for Markdown to Confluence storage format conversion."""

from confl.converter import markdown_to_storage


class TestHeadings:
    """Test heading conversion."""

    def test_h1(self) -> None:
        assert markdown_to_storage("# Heading 1") == "<h1>Heading 1</h1>\n"

    def test_h2(self) -> None:
        assert markdown_to_storage("## Heading 2") == "<h2>Heading 2</h2>\n"

    def test_h3(self) -> None:
        assert markdown_to_storage("### Heading 3") == "<h3>Heading 3</h3>\n"

    def test_h6(self) -> None:
        assert markdown_to_storage("###### Heading 6") == "<h6>Heading 6</h6>\n"


class TestInlineFormatting:
    """Test inline text formatting."""

    def test_bold(self) -> None:
        result = markdown_to_storage("This is **bold** text")
        assert "<strong>bold</strong>" in result
        assert result.startswith("<p>")

    def test_italic(self) -> None:
        result = markdown_to_storage("This is *italic* text")
        assert "<em>italic</em>" in result

    def test_bold_and_italic(self) -> None:
        result = markdown_to_storage("**bold** and *italic*")
        assert "<strong>bold</strong>" in result
        assert "<em>italic</em>" in result

    def test_inline_code(self) -> None:
        result = markdown_to_storage("Use `code` here")
        assert "<code>code</code>" in result

    def test_inline_code_escapes_html(self) -> None:
        result = markdown_to_storage("`<script>alert('xss')</script>`")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result


class TestParagraphs:
    """Test paragraph conversion."""

    def test_single_paragraph(self) -> None:
        result = markdown_to_storage("This is a paragraph.")
        assert result == "<p>This is a paragraph.</p>\n"

    def test_multiple_paragraphs(self) -> None:
        md = "First paragraph.\n\nSecond paragraph."
        result = markdown_to_storage(md)
        assert "<p>First paragraph.</p>" in result
        assert "<p>Second paragraph.</p>" in result


class TestLists:
    """Test list conversion."""

    def test_unordered_list(self) -> None:
        md = "- Item 1\n- Item 2\n- Item 3"
        result = markdown_to_storage(md)
        assert "<ul>" in result
        assert "</ul>" in result
        assert "<li>Item 1</li>" in result
        assert "<li>Item 2</li>" in result
        assert "<li>Item 3</li>" in result

    def test_ordered_list(self) -> None:
        md = "1. First\n2. Second\n3. Third"
        result = markdown_to_storage(md)
        assert "<ol>" in result
        assert "</ol>" in result
        assert "<li>First</li>" in result
        assert "<li>Second</li>" in result
        assert "<li>Third</li>" in result

    def test_nested_list(self) -> None:
        md = "- Item 1\n  - Nested 1\n  - Nested 2\n- Item 2"
        result = markdown_to_storage(md)
        assert result.count("<ul>") == 2  # Parent and nested list
        assert result.count("</ul>") == 2


class TestCodeBlocks:
    """Test code block conversion."""

    def test_code_block_no_language(self) -> None:
        md = "```\nprint('hello')\n```"
        result = markdown_to_storage(md)
        assert '<ac:structured-macro ac:name="code"' in result
        assert "<ac:plain-text-body><![CDATA[print('hello')]]></ac:plain-text-body>" in result
        assert "</ac:structured-macro>" in result

    def test_code_block_with_language(self) -> None:
        md = "```python\nprint('hello')\n```"
        result = markdown_to_storage(md)
        assert '<ac:structured-macro ac:name="code"' in result
        assert '<ac:parameter ac:name="language">python</ac:parameter>' in result
        assert "print('hello')" in result

    def test_code_block_escapes_special_chars(self) -> None:
        md = "```\n<html>&test</html>\n```"
        result = markdown_to_storage(md)
        # In CDATA sections, characters don't need to be escaped
        assert "<html>&test</html>" in result
        assert "<ac:plain-text-body><![CDATA[<html>&test</html>]]></ac:plain-text-body>" in result

    def test_code_block_java(self) -> None:
        md = "```java\npublic class Test {}\n```"
        result = markdown_to_storage(md)
        assert '<ac:parameter ac:name="language">java</ac:parameter>' in result
        assert "public class Test {}" in result


class TestLinks:
    """Test link conversion."""

    def test_simple_link(self) -> None:
        md = "[Google](https://google.com)"
        result = markdown_to_storage(md)
        assert '<a href="https://google.com">Google</a>' in result

    def test_link_with_title(self) -> None:
        md = '[Google](https://google.com "Search Engine")'
        result = markdown_to_storage(md)
        # Title is often ignored in simple renderers
        assert '<a href="https://google.com">Google</a>' in result

    def test_autolink(self) -> None:
        md = "Visit https://example.com"
        result = markdown_to_storage(md)
        # Without url plugin, URLs are plain text
        assert "https://example.com" in result


class TestImages:
    """Test image conversion."""

    def test_external_image(self) -> None:
        md = "![Alt text](https://example.com/image.png)"
        result = markdown_to_storage(md)
        assert "<ac:image>" in result
        assert '<ri:url ri:value="https://example.com/image.png" />' in result
        assert "<ac:caption><p>Alt text</p></ac:caption>" in result
        assert "</ac:image>" in result

    def test_attachment_image(self) -> None:
        md = "![Logo](logo.png)"
        result = markdown_to_storage(md)
        assert "<ac:image>" in result
        assert '<ri:attachment ri:filename="logo.png" />' in result
        assert "<ac:caption><p>Logo</p></ac:caption>" in result

    def test_image_without_alt(self) -> None:
        md = "![](https://example.com/image.png)"
        result = markdown_to_storage(md)
        assert "<ac:image>" in result
        assert '<ri:url ri:value="https://example.com/image.png" />' in result
        # Empty alt should not have caption
        assert "<ac:caption>" not in result


class TestTables:
    """Test table conversion."""

    def test_simple_table(self) -> None:
        md = """| A | B |
|---|---|
| 1 | 2 |"""
        result = markdown_to_storage(md)
        assert "<table>" in result
        assert "</table>" in result
        assert "<thead>" in result
        assert "<th>A</th>" in result
        assert "<th>B</th>" in result
        assert "<tbody>" in result
        assert "<td>1</td>" in result
        assert "<td>2</td>" in result

    def test_table_with_alignment(self) -> None:
        md = """| Left | Center | Right |
|:-----|:------:|------:|
| L    | C      | R     |"""
        result = markdown_to_storage(md)
        assert 'style="text-align:left"' in result
        assert 'style="text-align:center"' in result
        assert 'style="text-align:right"' in result

    def test_table_with_multiple_rows(self) -> None:
        md = """| Name | Age |
|------|-----|
| Alice | 30 |
| Bob   | 25 |
| Carol | 35 |"""
        result = markdown_to_storage(md)
        assert result.count("<tr>") == 4  # 1 header + 3 data rows
        assert "<td>Alice</td>" in result
        assert "<td>Bob</td>" in result
        assert "<td>Carol</td>" in result


class TestBlockQuotes:
    """Test block quote conversion."""

    def test_simple_blockquote(self) -> None:
        md = "> This is a quote"
        result = markdown_to_storage(md)
        assert "<blockquote>" in result
        assert "<p>This is a quote</p>" in result
        assert "</blockquote>" in result

    def test_multiline_blockquote(self) -> None:
        md = "> Line 1\n> Line 2"
        result = markdown_to_storage(md)
        assert "<blockquote>" in result
        assert "Line 1" in result
        assert "Line 2" in result


class TestHorizontalRule:
    """Test horizontal rule conversion."""

    def test_hr_dashes(self) -> None:
        assert "<hr />" in markdown_to_storage("---")

    def test_hr_asterisks(self) -> None:
        assert "<hr />" in markdown_to_storage("***")

    def test_hr_underscores(self) -> None:
        assert "<hr />" in markdown_to_storage("___")


class TestComplexDocuments:
    """Test conversion of complex documents with mixed elements."""

    def test_mixed_content(self) -> None:
        md = """# Title

This is a **paragraph** with *formatting*.

- List item 1
- List item 2

```python
def hello():
    return "world"
```

[Link](https://example.com)

| Col1 | Col2 |
|------|------|
| A    | B    |
"""
        result = markdown_to_storage(md)
        # Check all elements are present
        assert "<h1>Title</h1>" in result
        assert "<strong>paragraph</strong>" in result
        assert "<em>formatting</em>" in result
        assert "<ul>" in result
        assert '<ac:structured-macro ac:name="code"' in result
        assert '<a href="https://example.com">Link</a>' in result
        assert "<table>" in result

    def test_empty_markdown(self) -> None:
        assert markdown_to_storage("") == "\n"

    def test_whitespace_only(self) -> None:
        result = markdown_to_storage("   \n\n   ")
        # Should produce minimal output
        assert result.strip() == "" or result == "\n"


class TestHTMLEscaping:
    """Test that HTML is properly escaped."""

    def test_escape_html_in_text(self) -> None:
        md = "This has <script>alert('xss')</script> tags"
        result = markdown_to_storage(md)
        assert "&lt;script&gt;" in result
        assert "<script>" not in result or '<ac:structured-macro ac:name="code"' in result

    def test_escape_ampersand(self) -> None:
        md = "AT&T Corporation"
        result = markdown_to_storage(md)
        assert "AT&amp;T" in result

    def test_escape_quotes(self) -> None:
        md = 'He said "hello"'
        result = markdown_to_storage(md)
        # Quotes in text should be escaped or left as-is
        assert "hello" in result


class TestLineBreaks:
    """Test line break handling."""

    def test_hard_line_break(self) -> None:
        # Two spaces at end of line create hard break in Markdown
        md = "Line 1  \nLine 2"
        result = markdown_to_storage(md)
        # Should have br tag or be on separate lines
        assert "Line 1" in result
        assert "Line 2" in result


class TestStorageToMarkdown:
    """Test Confluence storage format to Markdown conversion."""

    def test_basic_heading(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<h1>Hello World</h1>"
        result = storage_to_markdown(storage)
        assert result.strip() == "# Hello World"

    def test_multiple_headings(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<h1>Title</h1><h2>Subtitle</h2><h3>Section</h3>"
        result = storage_to_markdown(storage)
        assert "# Title" in result
        assert "## Subtitle" in result
        assert "### Section" in result

    def test_paragraph(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<p>This is a paragraph.</p>"
        result = storage_to_markdown(storage)
        assert "This is a paragraph." in result

    def test_bold_and_italic(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<p>This is <strong>bold</strong> and <em>italic</em>.</p>"
        result = storage_to_markdown(storage)
        assert "**bold**" in result
        assert "*italic*" in result

    def test_inline_code(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<p>Use <code>code</code> here</p>"
        result = storage_to_markdown(storage)
        assert "`code`" in result

    def test_unordered_list(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<ul><li>Item 1</li><li>Item 2</li><li>Item 3</li></ul>"
        result = storage_to_markdown(storage)
        assert "* Item 1" in result or "- Item 1" in result
        assert "* Item 2" in result or "- Item 2" in result
        assert "* Item 3" in result or "- Item 3" in result

    def test_ordered_list(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<ol><li>First</li><li>Second</li><li>Third</li></ol>"
        result = storage_to_markdown(storage)
        assert "1. First" in result or "1) First" in result
        assert "2. Second" in result or "2) Second" in result
        assert "3. Third" in result or "3) Third" in result

    def test_link(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<p>Visit <a href="https://example.com">example</a></p>'
        result = storage_to_markdown(storage)
        assert "[example](https://example.com)" in result

    def test_blockquote(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<blockquote><p>This is quoted text.</p></blockquote>"
        result = storage_to_markdown(storage)
        assert "> This is quoted text." in result

    def test_horizontal_rule(self) -> None:
        from confl.converter import storage_to_markdown

        storage = "<hr />"
        result = storage_to_markdown(storage)
        assert "---" in result or "* * *" in result

    def test_table(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <table>
            <thead>
                <tr><th>Name</th><th>Age</th></tr>
            </thead>
            <tbody>
                <tr><td>Alice</td><td>30</td></tr>
                <tr><td>Bob</td><td>25</td></tr>
            </tbody>
        </table>
        """
        result = storage_to_markdown(storage)
        assert "Name" in result
        assert "Age" in result
        assert "Alice" in result
        assert "30" in result
        assert "Bob" in result
        assert "25" in result
        assert "|" in result  # Tables use pipes


class TestConfluenceCodeMacro:
    """Test Confluence code macro conversion."""

    def test_code_macro_with_language(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="code" ac:schema-version="1">
            <ac:parameter ac:name="language">python</ac:parameter>
            <ac:plain-text-body><![CDATA[print('hello')]]></ac:plain-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "```python" in result
        assert "print('hello')" in result
        assert "```" in result

    def test_code_macro_without_language(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="code" ac:schema-version="1">
            <ac:plain-text-body><![CDATA[some code]]></ac:plain-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "```" in result
        assert "some code" in result

    def test_code_macro_multiline(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="code" ac:schema-version="1">
            <ac:parameter ac:name="language">javascript</ac:parameter>
            <ac:plain-text-body><![CDATA[function hello() {
    console.log('Hello');
}]]></ac:plain-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "```javascript" in result
        assert "function hello()" in result
        assert "console.log('Hello');" in result


class TestConfluenceImages:
    """Test Confluence image tag conversion."""

    def test_external_image_url(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<ac:image><ri:url ri:value="https://example.com/image.png" /></ac:image>'
        result = storage_to_markdown(storage)
        assert "![](https://example.com/image.png)" in result

    def test_image_with_caption(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:image>
            <ri:url ri:value="https://example.com/logo.png" />
            <ac:caption><p>Company Logo</p></ac:caption>
        </ac:image>
        """
        result = storage_to_markdown(storage)
        assert "![Company Logo](https://example.com/logo.png)" in result

    def test_attached_image(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<ac:image><ri:attachment ri:filename="screenshot.png" /></ac:image>'
        result = storage_to_markdown(storage)
        assert "![](screenshot.png)" in result


class TestConfluencePanels:
    """Test Confluence panel macro conversion."""

    def test_info_panel(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="info" ac:schema-version="1">
            <ac:rich-text-body>
                <p>This is important information.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "> **INFO**:" in result
        assert "important information" in result

    def test_warning_panel(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="warning" ac:schema-version="1">
            <ac:rich-text-body>
                <p>Be careful!</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "> **WARNING**:" in result
        assert "Be careful!" in result

    def test_note_panel(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="note" ac:schema-version="1">
            <ac:rich-text-body>
                <p>Quick note here.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "> **NOTE**:" in result
        assert "Quick note" in result

    def test_tip_panel(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="tip" ac:schema-version="1">
            <ac:rich-text-body>
                <p>Pro tip!</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "> **TIP**:" in result
        assert "Pro tip!" in result


class TestMarkdownPanelsToStorage:
    """Test Markdown panel syntax conversion to Confluence storage format."""

    def test_info_panel_from_markdown(self) -> None:
        md = "> **INFO**: This is important information."
        result = markdown_to_storage(md)
        assert '<ac:structured-macro ac:name="info"' in result
        assert "<ac:rich-text-body>" in result
        assert "important information" in result

    def test_warning_panel_from_markdown(self) -> None:
        md = "> **WARNING**: Be careful!"
        result = markdown_to_storage(md)
        assert '<ac:structured-macro ac:name="warning"' in result
        assert "Be careful!" in result

    def test_note_panel_from_markdown(self) -> None:
        md = "> **NOTE**: Quick note here."
        result = markdown_to_storage(md)
        assert '<ac:structured-macro ac:name="note"' in result
        assert "Quick note" in result

    def test_tip_panel_from_markdown(self) -> None:
        md = "> **TIP**: Pro tip for you."
        result = markdown_to_storage(md)
        assert '<ac:structured-macro ac:name="tip"' in result
        assert "Pro tip" in result

    def test_regular_blockquote_unchanged(self) -> None:
        md = "> This is just a regular quote"
        result = markdown_to_storage(md)
        assert "<blockquote>" in result
        assert "<ac:structured-macro" not in result


class TestStatusMacro:
    """Test Confluence status macro conversion."""

    def test_status_green(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="title">Complete</ac:parameter>
            <ac:parameter ac:name="colour">Green</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "✅" in result
        assert "**Complete**" in result

    def test_status_yellow(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="title">In Progress</ac:parameter>
            <ac:parameter ac:name="colour">Yellow</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "⚠️" in result
        assert "**In Progress**" in result

    def test_status_red(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="title">Blocked</ac:parameter>
            <ac:parameter ac:name="colour">Red</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "❌" in result
        assert "**Blocked**" in result

    def test_status_blue(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="title">Info</ac:parameter>
            <ac:parameter ac:name="colour">Blue</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "ℹ️" in result
        assert "**Info**" in result

    def test_status_grey(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="title">Draft</ac:parameter>
            <ac:parameter ac:name="colour">Grey</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "⚪" in result
        assert "**Draft**" in result

    def test_status_unknown_color(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="status" ac:schema-version="1">
            <ac:parameter ac:name="title">Custom</ac:parameter>
            <ac:parameter ac:name="colour">Purple</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "▪️" in result  # Default emoji
        assert "**Custom**" in result


class TestExpandMacro:
    """Test Confluence expand (collapsible) macro conversion."""

    def test_expand_with_title(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="expand" ac:schema-version="1">
            <ac:parameter ac:name="title">Click to expand</ac:parameter>
            <ac:rich-text-body>
                <p>Hidden content here.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "<details>" in result
        assert "<summary>Click to expand</summary>" in result
        assert "Hidden content" in result
        assert "</details>" in result

    def test_expand_without_title_extracts_first_paragraph(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="expand" ac:schema-version="1">
            <ac:rich-text-body>
                <p>This is the question?</p>
                <p>This is the answer.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "<details>" in result
        assert "<summary>This is the question?</summary>" in result  # First paragraph as title
        assert "This is the answer" in result
        assert "This is the question?" not in result.split("</summary>")[1]  # Not repeated in body

    def test_expand_without_title_or_paragraphs(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="expand" ac:schema-version="1">
            <ac:rich-text-body>
                <ul><li>Item 1</li></ul>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "<details>" in result
        assert "<summary>Details</summary>" in result  # Fallback to default
        assert "Item 1" in result


class TestTOCMacro:
    """Test Confluence table of contents macro conversion."""

    def test_toc_macro(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<ac:structured-macro ac:name="toc" ac:schema-version="1"></ac:structured-macro>'
        result = storage_to_markdown(storage)
        assert "_Table of Contents_" in result


class TestJiraMacro:
    """Test Confluence Jira macro conversion."""

    def test_jira_macro_single_key(self) -> None:
        """Test Jira macro with single issue key."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
            <ac:parameter ac:name="key">PROJ-123</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Jira: PROJ-123]" in result

    def test_jira_macro_multiple_keys(self) -> None:
        """Test Jira macro with multiple issue keys."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
            <ac:parameter ac:name="key">PROJ-123, PROJ-124, PROJ-125</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Jira: PROJ-123, PROJ-124, PROJ-125]" in result

    def test_jira_macro_jql_query(self) -> None:
        """Test Jira macro with JQL query."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
            <ac:parameter ac:name="jqlQuery">project = PROJ AND status = Open</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Jira query: project = PROJ AND status = Open]" in result

    def test_jira_macro_jql_with_server(self) -> None:
        """Test Jira macro with JQL query and server parameter."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
            <ac:parameter ac:name="server">Company JIRA</ac:parameter>
            <ac:parameter ac:name="jqlQuery">assignee = currentUser()</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        # JQL query takes precedence
        assert "[Jira query: assignee = currentUser()]" in result

    def test_jira_macro_empty(self) -> None:
        """Test Jira macro with no parameters."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Jira]" in result

    def test_jira_macro_key_with_whitespace(self) -> None:
        """Test Jira macro with whitespace in key parameter."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
            <ac:parameter ac:name="key">  PROJ-123  ,  PROJ-456  </ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        # Should trim whitespace
        assert "[Jira: PROJ-123, PROJ-456]" in result

    def test_jira_macro_in_paragraph(self) -> None:
        """Test Jira macro embedded in text content."""
        from confl.converter import storage_to_markdown

        storage = """
        <p>See related issues: 
        <ac:structured-macro ac:name="jira" ac:schema-version="1">
            <ac:parameter ac:name="key">PROJ-123</ac:parameter>
        </ac:structured-macro>
        for details.</p>
        """
        result = storage_to_markdown(storage)
        assert "See related issues:" in result
        assert "[Jira: PROJ-123]" in result
        assert "for details." in result


class TestExcerptMacro:
    """Test excerpt macro conversion."""

    def test_excerpt_macro_with_rich_text(self) -> None:
        """Test excerpt macro with formatted content."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="excerpt" ac:schema-version="1">
            <ac:rich-text-body>
                <p>This is the excerpt content that can be reused elsewhere.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Excerpt]" in result
        assert "This is the excerpt content that can be reused elsewhere." in result

    def test_excerpt_macro_with_multiple_paragraphs(self) -> None:
        """Test excerpt macro with multiple paragraphs."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="excerpt" ac:schema-version="1">
            <ac:rich-text-body>
                <p>First paragraph of excerpt.</p>
                <p>Second paragraph of excerpt.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Excerpt]" in result
        assert "First paragraph of excerpt." in result
        assert "Second paragraph of excerpt." in result

    def test_excerpt_macro_with_formatting(self) -> None:
        """Test excerpt macro preserves formatting like bold and italic."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="excerpt" ac:schema-version="1">
            <ac:rich-text-body>
                <p>This is <strong>bold</strong> and <em>italic</em> text.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Excerpt]" in result
        assert "**bold**" in result
        assert "*italic*" in result

    def test_excerpt_macro_empty(self) -> None:
        """Test excerpt macro without content."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="excerpt" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Excerpt]" in result

    def test_excerpt_macro_with_list(self) -> None:
        """Test excerpt macro with list content."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="excerpt" ac:schema-version="1">
            <ac:rich-text-body>
                <ul>
                    <li>First item</li>
                    <li>Second item</li>
                </ul>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Excerpt]" in result
        assert "First item" in result
        assert "Second item" in result

    def test_excerpt_macro_in_paragraph(self) -> None:
        """Test excerpt macro embedded in text content."""
        from confl.converter import storage_to_markdown

        storage = """
        <p>Here is an excerpt: 
        <ac:structured-macro ac:name="excerpt" ac:schema-version="1">
            <ac:rich-text-body>
                <p>Important summary text.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        More text follows.</p>
        """
        result = storage_to_markdown(storage)
        assert "Here is an excerpt:" in result
        assert "[Excerpt]" in result
        assert "Important summary text." in result
        assert "More text follows." in result


class TestChildrenMacro:
    """Test children macro conversion."""

    def test_children_macro_default(self) -> None:
        """Test basic children macro with no parameters."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="children" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Child pages]" in result

    def test_children_macro_with_all_parameter(self) -> None:
        """Test children macro with all=true (include all descendants)."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="children" ac:schema-version="1">
            <ac:parameter ac:name="all">true</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Child pages:" in result
        assert "include all descendants" in result

    def test_children_macro_with_sort_parameter(self) -> None:
        """Test children macro with sort parameter."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="children" ac:schema-version="1">
            <ac:parameter ac:name="sort">title</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Child pages:" in result
        assert "sorted by title" in result

    def test_children_macro_with_depth_parameter(self) -> None:
        """Test children macro with depth parameter."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="children" ac:schema-version="1">
            <ac:parameter ac:name="depth">2</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Child pages:" in result
        assert "depth 2" in result

    def test_children_macro_with_multiple_parameters(self) -> None:
        """Test children macro with multiple parameters."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="children" ac:schema-version="1">
            <ac:parameter ac:name="sort">title</ac:parameter>
            <ac:parameter ac:name="depth">3</ac:parameter>
            <ac:parameter ac:name="all">true</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Child pages:" in result
        # Should contain all three parameter descriptions
        assert "sorted by title" in result
        assert "depth 3" in result
        assert "include all descendants" in result

    def test_children_macro_in_paragraph(self) -> None:
        """Test children macro embedded in paragraph text."""
        from confl.converter import storage_to_markdown

        storage = """
        <p>See the following pages:
        <ac:structured-macro ac:name="children" ac:schema-version="1">
            <ac:parameter ac:name="sort">creation</ac:parameter>
        </ac:structured-macro>
        for more information.</p>
        """
        result = storage_to_markdown(storage)
        assert "See the following pages:" in result
        assert "[Child pages:" in result
        assert "sorted by creation" in result
        assert "for more information." in result


class TestAttachmentsMacro:
    """Test attachments macro conversion."""

    def test_attachments_macro_default(self) -> None:
        """Test basic attachments macro with no parameters."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="attachments" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page attachments]" in result

    def test_attachments_macro_with_old_parameter(self) -> None:
        """Test attachments macro with old=true (include old versions)."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="attachments" ac:schema-version="1">
            <ac:parameter ac:name="old">true</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page attachments:" in result
        assert "include old versions" in result

    def test_attachments_macro_with_upload_parameter(self) -> None:
        """Test attachments macro with upload=true (upload enabled)."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="attachments" ac:schema-version="1">
            <ac:parameter ac:name="upload">true</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page attachments:" in result
        assert "upload enabled" in result

    def test_attachments_macro_with_patterns_parameter(self) -> None:
        """Test attachments macro with patterns parameter (file filter)."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="attachments" ac:schema-version="1">
            <ac:parameter ac:name="patterns">*.pdf</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page attachments:" in result
        assert "pattern: *.pdf" in result

    def test_attachments_macro_with_multiple_parameters(self) -> None:
        """Test attachments macro with multiple parameters."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="attachments" ac:schema-version="1">
            <ac:parameter ac:name="old">true</ac:parameter>
            <ac:parameter ac:name="upload">true</ac:parameter>
            <ac:parameter ac:name="patterns">*.jpg,*.png</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page attachments:" in result
        # Should contain all three parameter descriptions
        assert "include old versions" in result
        assert "upload enabled" in result
        assert "pattern: *.jpg,*.png" in result

    def test_attachments_macro_in_paragraph(self) -> None:
        """Test attachments macro embedded in paragraph text."""
        from confl.converter import storage_to_markdown

        storage = """
        <p>The following files are available:
        <ac:structured-macro ac:name="attachments" ac:schema-version="1">
            <ac:parameter ac:name="patterns">*.pdf</ac:parameter>
        </ac:structured-macro>
        for download.</p>
        """
        result = storage_to_markdown(storage)
        assert "The following files are available:" in result
        assert "[Page attachments:" in result
        assert "pattern: *.pdf" in result
        assert "for download." in result


class TestUnknownMacros:
    """Test handling of unknown/unsupported Confluence macros."""

    def test_unknown_macro_with_rich_text_body(self) -> None:
        """Test unknown macro with rich text content."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="custom-panel" ac:schema-version="1">
            <ac:rich-text-body>
                <p>This is custom content.</p>
            </ac:rich-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Macro: custom-panel]" in result
        assert "This is custom content." in result

    def test_unknown_macro_with_plain_text_body(self) -> None:
        """Test unknown macro with plain text content."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="custom-macro" ac:schema-version="1">
            <ac:plain-text-body><![CDATA[Plain text content here]]></ac:plain-text-body>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Macro: custom-macro]" in result
        assert "Plain text content here" in result

    def test_unknown_macro_with_parameters(self) -> None:
        """Test unknown macro with only parameters uses simplified format."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="custom-widget" ac:schema-version="1">
            <ac:parameter ac:name="widgetId">widget-123</ac:parameter>
            <ac:parameter ac:name="color">blue</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        # Should use simplified format without parameter details
        assert "[Macro: custom-widget]" in result

    def test_unknown_macro_with_nested_text(self) -> None:
        """Test unknown macro extracting nested text content."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="anchor" ac:schema-version="1">
            <ac:parameter ac:name="name">section-1</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        # Should use simplified format
        assert "[Macro: anchor]" in result

    def test_page_tree_macro(self) -> None:
        """Test page-tree macro (shows page hierarchy)."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="pagetree" ac:schema-version="1">
            <ac:parameter ac:name="root">@self</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        # Should use clean placeholder for pagetree
        assert "[Page tree]" in result

    def test_unknown_macro_empty(self) -> None:
        """Test completely empty unknown macro."""
        from confl.converter import storage_to_markdown

        storage = (
            '<ac:structured-macro ac:name="empty-macro" '
            'ac:schema-version="1"></ac:structured-macro>'
        )
        result = storage_to_markdown(storage)
        # Should not crash and should show placeholder with new format
        assert "[Macro: empty-macro]" in result

    def test_unknown_macro_no_crash(self) -> None:
        """Test that unknown macros never cause crashes."""
        from confl.converter import storage_to_markdown

        # Test various unknown macro structures
        test_cases = [
            '<ac:structured-macro ac:name="unknown1"></ac:structured-macro>',
            (
                '<ac:structured-macro ac:name="unknown2">'
                '<ac:parameter ac:name="test"></ac:parameter>'
                "</ac:structured-macro>"
            ),
            (
                '<ac:structured-macro ac:name="unknown3">'
                "<ac:rich-text-body></ac:rich-text-body>"
                "</ac:structured-macro>"
            ),
            (
                '<ac:structured-macro ac:name="unknown4">'
                "<ac:plain-text-body></ac:plain-text-body>"
                "</ac:structured-macro>"
            ),
        ]

        for storage in test_cases:
            # Should not raise any exception
            result = storage_to_markdown(storage)
            assert isinstance(result, str)
            assert len(result) >= 0  # Valid string output

    def test_include_macro(self) -> None:
        """Test include macro (includes content from another page)."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="include" ac:schema-version="1">
            <ac:parameter ac:name="page">Other Page Title</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        # Should show what page would be included
        assert "[Include: Other Page Title]" in result

    def test_include_macro_without_page(self) -> None:
        """Test include macro without page parameter."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="include" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Include page]" in result

    def test_excerpt_include_macro(self) -> None:
        """Test excerpt-include macro."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="excerpt-include" ac:schema-version="1">
            <ac:parameter ac:name="page">Source Page</ac:parameter>
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Excerpt from: Source Page]" in result

    def test_recently_updated_macro(self) -> None:
        """Test recently-updated macro."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="recently-updated" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Recently updated pages]" in result

    def test_content_report_table_macro(self) -> None:
        """Test content-report-table macro."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="content-report-table" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Content report]" in result

    def test_livesearch_macro(self) -> None:
        """Test livesearch macro."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="livesearch" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Live search]" in result

    def test_page_properties_macro(self) -> None:
        """Test page-properties macro."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="page-properties" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page properties]" in result

    def test_page_properties_report_macro(self) -> None:
        """Test page-properties-report macro."""
        from confl.converter import storage_to_markdown

        storage = """
        <ac:structured-macro ac:name="page-properties-report" ac:schema-version="1">
        </ac:structured-macro>
        """
        result = storage_to_markdown(storage)
        assert "[Page properties]" in result


class TestRoundTripConversion:
    """Test Markdown -> Storage -> Markdown round-trip conversions."""

    def test_basic_roundtrip(self) -> None:
        from confl.converter import markdown_to_storage, storage_to_markdown

        md = "# Hello\n\nThis is **bold** text."
        storage = markdown_to_storage(md)
        result = storage_to_markdown(storage)
        # Check key content is preserved
        assert "# Hello" in result or "Hello" in result
        assert "**bold**" in result

    def test_list_roundtrip(self) -> None:
        from confl.converter import markdown_to_storage, storage_to_markdown

        md = "- Item 1\n- Item 2\n- Item 3"
        storage = markdown_to_storage(md)
        result = storage_to_markdown(storage)
        # Lists should be preserved (though format may differ slightly)
        assert "Item 1" in result
        assert "Item 2" in result
        assert "Item 3" in result

    def test_code_block_roundtrip(self) -> None:
        from confl.converter import markdown_to_storage, storage_to_markdown

        md = "```python\nprint('test')\n```"
        storage = markdown_to_storage(md)
        result = storage_to_markdown(storage)
        assert "```python" in result or "```" in result
        assert "print('test')" in result


class TestConfluencePageLinks:
    """Test Confluence page link conversion."""

    def test_page_link_with_link_body(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:link ac:card-appearance="inline">
            <ri:page ri:space-key="PM" ri:content-title="Project Overview" />
            <ac:link-body>Project Overview</ac:link-body>
        </ac:link>
        """
        result = storage_to_markdown(storage)
        assert "[Project Overview]" in result

    def test_page_link_without_link_body(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:link>
            <ri:page ri:space-key="DEV" ri:content-title="API Documentation" />
        </ac:link>
        """
        result = storage_to_markdown(storage)
        assert "[API Documentation]" in result

    def test_page_link_in_paragraph(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>For more information, see <ac:link>
            <ri:page ri:content-title="Getting Started" />
            <ac:link-body>Getting Started</ac:link-body>
        </ac:link> guide.</p>
        """
        result = storage_to_markdown(storage)
        assert "For more information, see [Getting Started] guide." in result

    def test_page_link_card_appearance(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:link ac:card-appearance="block">
            <ri:page ri:space-key="DOCS" ri:content-title="Installation Guide" />
            <ac:link-body>Installation Guide</ac:link-body>
        </ac:link>
        """
        result = storage_to_markdown(storage)
        assert "[Installation Guide]" in result

    def test_multiple_page_links(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>See <ac:link>
            <ri:page ri:content-title="Page 1" />
            <ac:link-body>Page 1</ac:link-body>
        </ac:link> and <ac:link>
            <ri:page ri:content-title="Page 2" />
            <ac:link-body>Page 2</ac:link-body>
        </ac:link> for details.</p>
        """
        result = storage_to_markdown(storage)
        assert "[Page 1]" in result
        assert "[Page 2]" in result
        assert "for details" in result

    def test_page_link_with_special_characters(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:link>
            <ri:page ri:content-title="FAQ &amp; Help" />
            <ac:link-body>FAQ &amp; Help</ac:link-body>
        </ac:link>
        """
        result = storage_to_markdown(storage)
        assert "[FAQ & Help]" in result

    def test_page_link_fallback_to_text(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: link with only text content
        storage = """
        <ac:link>Some Link Text</ac:link>
        """
        result = storage_to_markdown(storage)
        assert "[Some Link Text]" in result

    def test_page_link_empty_fallback(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: completely empty link
        storage = """
        <ac:link></ac:link>
        """
        result = storage_to_markdown(storage)
        assert "[Page Link]" in result


class TestTaskLists:
    """Test Confluence task list conversion."""

    def test_single_incomplete_task(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>Write documentation</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [ ] Write documentation" in result

    def test_single_complete_task(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Review code</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [x] Review code" in result

    def test_multiple_tasks_mixed_status(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Set up project</ac:task-body>
            </ac:task>
            <ac:task>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>Write tests</ac:task-body>
            </ac:task>
            <ac:task>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Create README</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [x] Set up project" in result
        assert "- [ ] Write tests" in result
        assert "- [x] Create README" in result

    def test_task_without_status(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: task without status element (should default to incomplete)
        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-body>Default task</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [ ] Default task" in result

    def test_task_with_formatted_content(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>Review <strong>bold text</strong> and <em>italics</em></ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [ ] Review **bold text** and *italics*" in result

    def test_task_in_paragraph_context(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>Project tasks:</p>
        <ac:task-list>
            <ac:task>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>First task</ac:task-body>
            </ac:task>
            <ac:task>
                <ac:task-status>complete</ac:task-status>
                <ac:task-body>Second task</ac:task-body>
            </ac:task>
        </ac:task-list>
        <p>More content</p>
        """
        result = storage_to_markdown(storage)
        assert "Project tasks:" in result
        assert "- [ ] First task" in result
        assert "- [x] Second task" in result
        assert "More content" in result

    def test_empty_task_list(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: empty task list
        storage = """
        <ac:task-list>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        # Should not crash, returns empty string or minimal content
        assert isinstance(result, str)

    def test_task_with_special_characters(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>incomplete</ac:task-status>
                <ac:task-body>Fix bug in &lt;Component&gt; &amp; test</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [ ] Fix bug in <Component> & test" in result

    def test_task_status_case_insensitive(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ac:task-list>
            <ac:task>
                <ac:task-status>COMPLETE</ac:task-status>
                <ac:task-body>Uppercase status</ac:task-body>
            </ac:task>
            <ac:task>
                <ac:task-status>InCoMpLeTe</ac:task-status>
                <ac:task-body>Mixed case status</ac:task-body>
            </ac:task>
        </ac:task-list>
        """
        result = storage_to_markdown(storage)
        assert "- [x] Uppercase status" in result
        assert "- [ ] Mixed case status" in result


class TestUserMentions:
    """Test Confluence user mention conversion."""

    def test_user_mention_with_username(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<p>Hello <ri:user ri:username="jsmith" /></p>'
        result = storage_to_markdown(storage)
        assert "@jsmith" in result

    def test_user_mention_with_account_id(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<p>Hello <ri:user ri:account-id="abc123" /></p>'
        result = storage_to_markdown(storage)
        assert "@abc123" in result

    def test_user_mention_with_userkey(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<p>Hello <ri:user ri:userkey="~jsmith" /></p>'
        result = storage_to_markdown(storage)
        assert "@jsmith" in result

    def test_user_mention_with_userkey_no_tilde(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<p>Hello <ri:user ri:userkey="jsmith" /></p>'
        result = storage_to_markdown(storage)
        assert "@jsmith" in result

    def test_user_mention_prefers_username(self) -> None:
        from confl.converter import storage_to_markdown

        # When multiple attributes present, username should be preferred
        storage = (
            '<p>Hello <ri:user ri:username="jsmith" '
            'ri:account-id="abc123" ri:userkey="~jdoe" /></p>'
        )
        result = storage_to_markdown(storage)
        assert "@jsmith" in result
        assert "@abc123" not in result
        assert "@jdoe" not in result

    def test_user_mention_falls_back_to_userkey(self) -> None:
        from confl.converter import storage_to_markdown

        # When username not present, should use userkey
        storage = '<p>Hello <ri:user ri:userkey="~jsmith" ri:account-id="abc123" /></p>'
        result = storage_to_markdown(storage)
        assert "@jsmith" in result
        assert "@abc123" not in result

    def test_user_mention_falls_back_to_account_id(self) -> None:
        from confl.converter import storage_to_markdown

        # When username and userkey not present, should use account-id
        storage = '<p>Hello <ri:user ri:account-id="abc123" /></p>'
        result = storage_to_markdown(storage)
        assert "@abc123" in result

    def test_user_mention_without_attributes(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: ri:user without any identifier (should use placeholder)
        storage = "<p>Hello <ri:user /></p>"
        result = storage_to_markdown(storage)
        assert "@user" in result

    def test_multiple_user_mentions(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>Meeting with <ri:user ri:username="jsmith" /> and <ri:user ri:username="bjones" /></p>
        """
        result = storage_to_markdown(storage)
        assert "@jsmith" in result
        assert "@bjones" in result

    def test_user_mention_in_formatted_text(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>Assigned to <strong><ri:user ri:username="jsmith" /></strong> for review</p>
        """
        result = storage_to_markdown(storage)
        assert "@jsmith" in result
        assert "**" in result  # Should preserve bold formatting

    def test_user_mention_in_list(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ul>
            <li>Contact <ri:user ri:username="jsmith" /></li>
            <li>Follow up with <ri:user ri:username="bjones" /></li>
        </ul>
        """
        result = storage_to_markdown(storage)
        assert "@jsmith" in result
        assert "@bjones" in result

    def test_user_mention_with_special_characters(self) -> None:
        from confl.converter import storage_to_markdown

        # Test usernames with dots, dashes, underscores
        storage = """
        <p>
            <ri:user ri:username="john.smith" />
            <ri:user ri:username="jane-doe" />
            <ri:user ri:username="bob_jones" />
        </p>
        """
        result = storage_to_markdown(storage)
        assert "@john.smith" in result
        assert "@jane-doe" in result
        assert "@bob_jones" in result


class TestTimeElements:
    """Test HTML time element conversion."""

    def test_time_with_datetime_attribute(self) -> None:
        from confl.converter import storage_to_markdown

        storage = '<p>Due date: <time datetime="2026-02-15" /></p>'
        result = storage_to_markdown(storage)
        assert "2026-02-15" in result

    def test_time_with_datetime_and_local_id(self) -> None:
        from confl.converter import storage_to_markdown

        # Actual format from Confluence fixtures
        storage = '<p>Target: <time datetime="2026-02-15" local-id="abc123" /></p>'
        result = storage_to_markdown(storage)
        assert "2026-02-15" in result

    def test_time_in_table_cell(self) -> None:
        from confl.converter import storage_to_markdown

        # Common use case: dates in table cells
        storage = """
        <table>
            <tr>
                <th>Item</th>
                <th>Date</th>
            </tr>
            <tr>
                <td>Task 1</td>
                <td><time datetime="2026-02-15" /></td>
            </tr>
        </table>
        """
        result = storage_to_markdown(storage)
        assert "2026-02-15" in result

    def test_time_with_text_content(self) -> None:
        from confl.converter import storage_to_markdown

        # Time element with inner text (fallback case)
        storage = '<p>Due: <time datetime="2026-02-15">February 15, 2026</time></p>'
        result = storage_to_markdown(storage)
        # Should use datetime attribute when present
        assert "2026-02-15" in result

    def test_time_without_datetime(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: time element without datetime attribute but with text
        storage = "<p>Due: <time>February 15, 2026</time></p>"
        result = storage_to_markdown(storage)
        # Should fall back to text content
        assert "February 15, 2026" in result

    def test_time_without_datetime_or_text(self) -> None:
        from confl.converter import storage_to_markdown

        # Edge case: time element with no attributes or content
        storage = "<p>Due: <time /></p>"
        result = storage_to_markdown(storage)
        # Should use placeholder
        assert "[date]" in result

    def test_multiple_time_elements(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>Start: <time datetime="2026-02-10" /> End: <time datetime="2026-02-20" /></p>
        """
        result = storage_to_markdown(storage)
        assert "2026-02-10" in result
        assert "2026-02-20" in result

    def test_time_in_formatted_text(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <p>Deadline: <strong><time datetime="2026-02-15" /></strong></p>
        """
        result = storage_to_markdown(storage)
        assert "2026-02-15" in result
        assert "**" in result  # Should preserve bold formatting

    def test_time_in_list(self) -> None:
        from confl.converter import storage_to_markdown

        storage = """
        <ul>
            <li>Phase 1: <time datetime="2026-02-10" /></li>
            <li>Phase 2: <time datetime="2026-02-20" /></li>
        </ul>
        """
        result = storage_to_markdown(storage)
        assert "2026-02-10" in result
        assert "2026-02-20" in result
