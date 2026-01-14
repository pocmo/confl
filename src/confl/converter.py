"""Markdown to Confluence storage format conversion."""

import html
import logging
from typing import Any

import mistune
from bs4 import Tag
from markdownify import MarkdownConverter

logger = logging.getLogger(__name__)


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
        """
        Render block quote.

        Supports special syntax for Confluence panels:
        > **INFO**: Content → info panel
        > **WARNING**: Content → warning panel
        > **NOTE**: Content → note panel
        > **TIP**: Content → tip panel
        """
        stripped = text.strip()

        # Strip surrounding <p></p> tags if present (added by paragraph renderer)
        if stripped.startswith("<p>") and stripped.endswith("</p>"):
            stripped = stripped[3:-4].strip()

        # Check for panel syntax: **LABEL**: content
        for panel_type in ["INFO", "WARNING", "NOTE", "TIP"]:
            prefix = f"<strong>{panel_type}</strong>:"
            if stripped.startswith(prefix):
                content = stripped[len(prefix) :].strip()
                macro_name = panel_type.lower()
                return (
                    f'<ac:structured-macro ac:name="{macro_name}" ac:schema-version="1">'
                    f"<ac:rich-text-body><p>{content}</p></ac:rich-text-body>"
                    f"</ac:structured-macro>\n"
                )

        # Regular blockquote - restore paragraph tag if we removed it
        return f"<blockquote><p>{stripped}</p></blockquote>\n"

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
        - Confluence panels (info/warning/note/tip) via special blockquote syntax
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

        # Handle status macro
        if macro_name == "status":
            # Extract title and color parameters
            title = ""
            color = ""
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "title":
                    title = param.get_text().strip()
                elif param_name == "colour":
                    color = param.get_text().strip()

            # Convert to badge-like Markdown (use bold with emoji indicators)
            color_emoji = {
                "Green": "✅",
                "Yellow": "⚠️",
                "Red": "❌",
                "Blue": "ℹ️",
                "Grey": "⚪",
            }.get(color, "▪️")

            return f"{color_emoji} **{title}** "

        # Handle expand macro (collapsible content)
        if macro_name == "expand":
            # Extract title parameter
            title = "Details"
            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                if param_name == "title":
                    title = param.get_text().strip()
                    break

            # Extract rich-text-body content
            rich_body = el.find("ac:rich-text-body")
            if rich_body is not None:
                inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
                # Convert to details/summary HTML (supported in many Markdown renderers)
                return (
                    f"<details>\n<summary>{title}</summary>\n\n{inner_md.strip()}\n</details>\n\n"
                )

        # Handle table of contents macro
        if macro_name == "toc":
            return "_Table of Contents_\n\n"

        # Handle jira macro (Jira issue integration)
        if macro_name == "jira":
            # Extract parameters - can be single key, multiple keys, or JQL query
            jql_query = ""
            keys = []

            for param in el.find_all("ac:parameter"):
                param_name = param.get("ac:name")
                param_value = param.get_text().strip()

                if param_name == "key":
                    # Single issue key or comma-separated keys
                    if param_value:
                        keys.extend([k.strip() for k in param_value.split(",")])
                elif param_name == "jqlQuery":
                    jql_query = param_value

            # Format output based on what we found
            if jql_query:
                return f"[Jira query: {jql_query}]\n\n"
            elif keys:
                keys_str = ", ".join(keys)
                return f"[Jira: {keys_str}]\n\n"
            else:
                # Macro present but no recognizable parameters
                return "[Jira]\n\n"

        # For unknown macros, handle gracefully
        return self._handle_unknown_macro(el, macro_name, text, **options)

    def _handle_unknown_macro(self, el: Tag, macro_name: str, text: str, **options: Any) -> str:
        """Handle unknown Confluence macros gracefully.

        Args:
            el: The macro element
            macro_name: Name of the macro
            text: Extracted text content
            **options: Additional options

        Returns:
            Markdown representation of the macro
        """
        logger.debug(f"Converting unknown macro: {macro_name}")

        # Try to extract content from rich-text-body
        rich_body = el.find("ac:rich-text-body")
        if rich_body is not None:
            inner_md = self.process_tag(rich_body, **options)  # type: ignore[attr-defined]
            if inner_md.strip():
                # For macros with rich content, show a placeholder with content
                logger.debug(f"Extracted rich-text-body from {macro_name} macro")
                return f"[{macro_name}]\n\n{inner_md.strip()}\n\n"

        # Try to extract from plain-text-body
        plain_body = el.find("ac:plain-text-body")
        if plain_body is not None:
            plain_text = plain_body.get_text().strip()
            if plain_text:
                logger.debug(f"Extracted plain-text-body from {macro_name} macro")
                return f"[{macro_name}]\n\n{plain_text}\n\n"

        # Try to extract parameter values (for macros that just store data in params)
        params = []
        for param in el.find_all("ac:parameter"):
            param_name = param.get("ac:name", "")
            param_value = param.get_text().strip()
            if param_value:
                params.append(f"{param_name}: {param_value}")

        if params:
            logger.debug(f"Extracted parameters from {macro_name} macro")
            param_str = ", ".join(params)
            return f"[{macro_name}: {param_str}]\n\n"

        # If there's any text content, use it
        if text.strip():
            logger.debug(f"Extracted text content from {macro_name} macro")
            return text.strip() + "\n\n"

        # Last resort: show placeholder for macro with no extractable content
        # This prevents completely silent failures
        logger.debug(f"No content extracted from {macro_name} macro, using placeholder")
        return f"[{macro_name}]\n\n"

    def convert_ac_link(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence page link to Markdown.

        Handles <ac:link> tags with <ri:page> references.
        Shows link text in brackets: [Page Title]

        Example Confluence format:
            <ac:link ac:card-appearance="inline">
                <ri:page ri:space-key="PM" ri:content-title="Page Title" />
                <ac:link-body>Page Title</ac:link-body>
            </ac:link>

        Result: [Page Title]
        """
        # Extract link text from ac:link-body
        link_body = el.find("ac:link-body")
        if link_body is not None:
            link_text = link_body.get_text().strip()
            if link_text:
                return f"[{link_text}]"

        # Fallback: try to get page title from ri:page attributes
        ri_page = el.find("ri:page")
        if ri_page is not None:
            content_title = ri_page.get("ri:content-title", "")
            if content_title:
                return f"[{content_title}]"

        # Last resort: return any text content
        if text.strip():
            return f"[{text.strip()}]"

        return "[Page Link]"

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

    def convert_ac_task_list(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence task list to Markdown checkboxes.

        Handles <ac:task-list> containers with <ac:task> items.
        Each task has <ac:task-status> (complete/incomplete) and <ac:task-body>.

        Example Confluence format:
            <ac:task-list>
                <ac:task>
                    <ac:task-status>incomplete</ac:task-status>
                    <ac:task-body>Task description</ac:task-body>
                </ac:task>
                <ac:task>
                    <ac:task-status>complete</ac:task-status>
                    <ac:task-body>Completed task</ac:task-body>
                </ac:task>
            </ac:task-list>

        Result:
            - [ ] Task description
            - [x] Completed task
        """
        result = []

        # Find all task elements
        tasks = el.find_all("ac:task", recursive=False)
        for task in tasks:
            # Extract status (default to incomplete)
            status_elem = task.find("ac:task-status")
            is_complete = False
            if status_elem is not None:
                status_text = status_elem.get_text().strip().lower()
                is_complete = status_text == "complete"

            # Extract task body text
            body_elem = task.find("ac:task-body")
            if body_elem is not None:
                # Process the body content recursively for any nested formatting
                task_text = self.process_tag(body_elem, **options).strip()  # type: ignore[attr-defined]
                if task_text:
                    checkbox = "[x]" if is_complete else "[ ]"
                    result.append(f"- {checkbox} {task_text}")

        if result:
            return "\n".join(result) + "\n\n"

        return ""

    def convert_ri_user(self, el: Tag, text: str, **options: Any) -> str:
        """Convert Confluence user mention to @username format.

        Handles <ri:user> tags with username or account-id attributes.
        Prefers ri:username for readability, falls back to ri:userkey or ri:account-id.

        Example Confluence formats:
            <ri:user ri:username="jsmith" />
            <ri:user ri:account-id="abc123" ri:userkey="~jsmith" />

        Result: @jsmith or @abc123
        """
        # Try to extract username (most readable)
        username_attr = el.get("ri:username", "")
        # el.get() can return a list in some edge cases, ensure it's a string
        username = username_attr if isinstance(username_attr, str) else ""
        if username:
            return f"@{username}"

        # Fall back to userkey (often contains username with ~ prefix)
        userkey_attr = el.get("ri:userkey", "")
        userkey = userkey_attr if isinstance(userkey_attr, str) else ""
        if userkey:
            # Strip ~ prefix if present
            clean_userkey = userkey.lstrip("~")
            return f"@{clean_userkey}"

        # Last resort: use account-id
        account_id_attr = el.get("ri:account-id", "")
        account_id = account_id_attr if isinstance(account_id_attr, str) else ""
        if account_id:
            return f"@{account_id}"

        # If no identifier found, return placeholder
        return "@user"


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
        - Task lists → markdown checkboxes (- [ ] / - [x])
        - Code blocks (including code macro with syntax)
        - Inline code
        - Links (standard HTML and Confluence page links)
        - Images (both external URLs and attachments)
        - Tables
        - Block quotes
        - Horizontal rules
        - Info/warning/note/tip panels → block quotes with label
        - Status macros → emoji badges
        - Expand macros → HTML details/summary
        - TOC macro → italic text placeholder
        - Jira macro → bracketed Jira issue keys or query
        - Page links (ac:link with ri:page) → bracketed text
        - User mentions (ri:user) → @username format

    Partial support:
        - Unknown macros → text content or omitted

    Limitations:
        - Complex Confluence macros may not convert cleanly
        - Nested macros may lose formatting

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
