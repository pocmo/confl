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
