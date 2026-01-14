"""Markdown to Confluence storage format conversion."""

import html
from typing import Any

import mistune
from bs4 import Tag
from markdownify import MarkdownConverter


class ConfluenceStorageRenderer(mistune.HTMLRenderer):
    """Custom Mistune renderer that outputs Confluence storage format XHTML."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with HTML escaping enabled by default."""
        # Always escape HTML for security
        super().__init__(escape=True, **kwargs)

    def heading(self, text: str, level: int, **attrs: Any) -> str:
        """Render heading as Confluence storage format."""
        return f"<h{level}>{text}</h{level}>\n"

    def paragraph(self, text: str) -> str:
        """Render paragraph as Confluence storage format."""
        return f"<p>{text}</p>\n"

    def strong(self, text: str) -> str:
        """Render bold text."""
        return f"<strong>{text}</strong>"

    def emphasis(self, text: str) -> str:
        """Render italic text."""
        return f"<em>{text}</em>"

    def codespan(self, text: str) -> str:
        """Render inline code."""
        escaped_text = html.escape(text)
        return f"<code>{escaped_text}</code>"

    def block_code(self, code: str, info: str | None = None) -> str:
        """Render code block as Confluence code macro."""
        language = info.split()[0] if info else ""
        # Don't escape code in CDATA - it's already protected
        clean_code = code.rstrip()

        # Use Confluence code macro for syntax highlighting
        macro = '<ac:structured-macro ac:name="code"'
        if language:
            macro += (
                f' ac:schema-version="1"><ac:parameter ac:name="language">{language}</ac:parameter>'
            )
        else:
            macro += ' ac:schema-version="1">'

        macro += f"<ac:plain-text-body><![CDATA[{clean_code}]]></ac:plain-text-body>"
        macro += "</ac:structured-macro>\n"
        return macro

    def linebreak(self) -> str:
        """Render line break."""
        return "<br />"

    def softbreak(self) -> str:
        """Render soft line break (space)."""
        return " "

    def link(self, text: str, url: str, title: str | None = None) -> str:
        """Render link."""
        link_text = text if text else url
        safe_url = self.safe_url(url)
        return f'<a href="{safe_url}">{link_text}</a>'

    def image(self, text: str, url: str, title: str | None = None) -> str:
        """Render image as Confluence image tag."""
        alt = text
        safe_url = self.safe_url(url)
        # For external images, use ri:url
        if url.startswith(("http://", "https://")):
            img = f'<ac:image><ri:url ri:value="{safe_url}" />'
            if alt:
                img += f"<ac:caption><p>{html.escape(alt)}</p></ac:caption>"
            img += "</ac:image>"
            return img
        else:
            # For attachments, use ri:attachment
            img = f'<ac:image><ri:attachment ri:filename="{html.escape(url)}" />'
            if alt:
                img += f"<ac:caption><p>{html.escape(alt)}</p></ac:caption>"
            img += "</ac:image>"
            return img

    def list(self, text: str, ordered: bool, **attrs: Any) -> str:
        """Render list (ordered or unordered)."""
        tag = "ol" if ordered else "ul"
        return f"<{tag}>\n{text}</{tag}>\n"

    def list_item(self, text: str) -> str:
        """Render list item."""
        return f"<li>{text}</li>\n"

    def block_quote(self, text: str) -> str:
        """Render block quote."""
        return f"<blockquote><p>{text.strip()}</p></blockquote>\n"

    def thematic_break(self) -> str:
        """Render horizontal rule."""
        return "<hr />\n"

    def text(self, text: str) -> str:
        """Render plain text - escape HTML entities."""
        return html.escape(text)

    def table(self, text: str) -> str:
        """Render table."""
        return f"<table>\n{text}</table>\n"

    def table_head(self, text: str) -> str:
        """Render table head."""
        return f"<thead>\n<tr>\n{text}</tr>\n</thead>\n"

    def table_body(self, text: str) -> str:
        """Render table body."""
        return f"<tbody>\n{text}</tbody>\n"

    def table_row(self, text: str) -> str:
        """Render table row."""
        return f"<tr>\n{text}</tr>\n"

    def table_cell(self, text: str, align: str | None = None, head: bool = False) -> str:
        """Render table cell."""
        tag = "th" if head else "td"
        attrs = f' style="text-align:{align}"' if align else ""
        return f"<{tag}{attrs}>{text}</{tag}>\n"


def markdown_to_storage(markdown: str) -> str:
    """
    Convert Markdown to Confluence storage format.

    Args:
        markdown: Markdown text to convert

    Returns:
        Confluence storage format XHTML string

    Supported features:
        - Headings (h1-h6)
        - Bold (**text**) and italic (*text*)
        - Lists (ordered and unordered)
        - Code blocks (with syntax highlighting)
        - Inline code
        - Links
        - Images (external URLs and attachments)
        - Tables
        - Block quotes
        - Horizontal rules

    Example:
        >>> md = "# Hello\\n\\nThis is **bold** text."
        >>> storage = markdown_to_storage(md)
        >>> print(storage)
        <h1>Hello</h1>
        <p>This is <strong>bold</strong> text.</p>
    """
    renderer = ConfluenceStorageRenderer()
    md = mistune.create_markdown(renderer=renderer, plugins=["table"])
    result = md(markdown)
    # With a renderer, mistune always returns a string
    assert isinstance(result, str)
    return result.rstrip() + "\n"


class ConfluenceMarkdownConverter(MarkdownConverter):
    """Custom markdownify converter that handles Confluence storage format tags."""

    def convert_ac_structured_macro(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence structured macro to Markdown."""
        macro_name_attr = el.get("ac:name", "")
        # el.get() can return a list in some edge cases, ensure it's a string
        macro_name = macro_name_attr if isinstance(macro_name_attr, str) else ""

        # Handle code macro
        if macro_name == "code":
            # Extract language parameter
            language = ""
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "language":
                    language = param.get_text().strip()
                    break

            # Extract code content from plain-text-body
            code_body = el.find("ac:plain-text-body")
            if code_body is not None:
                code_text = code_body.get_text().strip()
                return f"```{language}\n{code_text}\n```\n\n"

        # Handle info/warning/note panels
        if macro_name in ("info", "warning", "note", "tip"):
            # Extract rich-text-body content
            rich_body = el.find("ac:rich-text-body")
            if rich_body is not None:
                # Convert the content inside recursively
                inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
                return f"> **{macro_name.upper()}**: {inner_md.strip()}\n\n"

        # For unknown macros, try to extract text or return nothing
        return text.strip() + "\n\n" if text.strip() else ""

    def convert_ac_image(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence image tag to Markdown."""
        # Try to find ri:url (external image)
        url_elem = el.find("ri:url")
        if url_elem is not None:
            url = url_elem.get("ri:value", "")
        else:
            # Try to find ri:attachment (attached image)
            attachment = el.find("ri:attachment")
            if attachment is not None:
                url = attachment.get("ri:filename", "")
            else:
                return ""

        # Try to find caption
        caption_elem = el.find("ac:caption")
        alt_text = ""
        if caption_elem is not None:
            alt_text = caption_elem.get_text().strip()

        return f"![{alt_text}]({url})"


def storage_to_markdown(storage: str) -> str:
    """
    Convert Confluence storage format to Markdown.

    This is a best-effort conversion. Some Confluence-specific features
    may not have direct Markdown equivalents and will be converted to
    the closest approximation or omitted.

    Args:
        storage: Confluence storage format XHTML string

    Returns:
        Markdown text

    Supported conversions:
        - Headings (h1-h6)
        - Bold and italic
        - Lists (ordered and unordered)
        - Code blocks (including code macro with syntax)
        - Inline code
        - Links
        - Images (both external URLs and attachments)
        - Tables
        - Block quotes
        - Horizontal rules

    Partial support:
        - Info/warning/note panels → block quotes with label
        - Unknown macros → text content or omitted

    Limitations:
        - Complex Confluence macros may not convert cleanly
        - Nested macros may lose formatting
        - Page links require special handling

    Example:
        >>> storage = "<h1>Hello</h1><p>This is <strong>bold</strong>.</p>"
        >>> md = storage_to_markdown(storage)
        >>> print(md)
        # Hello

        This is **bold**.
    """
    converter = ConfluenceMarkdownConverter(
        heading_style="ATX",  # Use # for headings
    )

    result = converter.convert(storage)
    return result.strip() + "\n"
