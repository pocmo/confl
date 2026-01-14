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
